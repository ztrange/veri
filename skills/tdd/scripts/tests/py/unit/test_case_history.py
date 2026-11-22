"""In-process cases for veri/case_history.py, the git history queries tests_frozen's policy asks.

subprocess is faked through fake_processes and each case runs inside tmp_path, so a fake that failed to
engage would ask git about an empty directory, never about the repository under test."""
import importlib
import subprocess

import pytest


@pytest.fixture
def case_history(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    return importlib.import_module("veri.case_history")


@pytest.fixture
def runs(fake_processes):
    """install(answers) -> fake: answers maps the argv after "git" to (code, out, err) or an exception to raise;
    any other git command fails with code 1. fake.seen holds (argv, kwargs) per call."""
    def install(answers):
        table = {" ".join(("git",) + key): answer for key, answer in answers.items()}
        return fake_processes.answers(table, default=(1, b"", b"fatal: nope\n"), exact=True)
    return install


def test_toplevel_is_the_working_trees_root_without_its_newline(case_history, runs):
    runs({("rev-parse", "--show-toplevel"): (0, b"/work/repo\n", b"")})
    assert case_history.toplevel() == "/work/repo"


def test_toplevel_is_none_outside_a_repository(case_history, runs):
    runs({("rev-parse", "--show-toplevel"): (128, b"", b"fatal: not a git repository\n")})
    assert case_history.toplevel() is None


def test_has_rev_is_true_for_a_revision_git_verifies(case_history, runs):
    runs({("rev-parse", "--verify", "-q", "HEAD~1"): (0, b"", b"")})
    assert case_history.has_rev("HEAD~1") is True


def test_has_rev_is_false_for_a_revision_git_cannot_verify(case_history, runs):
    runs({})
    assert case_history.has_rev("HEAD") is False


def test_current_branch_is_the_abbreviated_head(case_history, runs):
    runs({("rev-parse", "--abbrev-ref", "HEAD"): (0, b"tdd/12-port\n", b"")})
    assert case_history.current_branch() == "tdd/12-port"


def test_current_branch_is_empty_when_git_cannot_say(case_history, runs):
    runs({})
    assert case_history.current_branch() == ""


SUITE = "def test_a():\n    assert 1\n\n\ndef test_b():\n    assert 2\n"


def test_text_at_is_the_file_as_it_was_at_the_revision(case_history, runs):
    runs({("show", "abc:t_x.py"): (0, SUITE.encode(), b"")})
    assert case_history.text_at("abc", "t_x.py") == SUITE


def test_text_at_replaces_bytes_that_are_not_utf8(case_history, runs):
    runs({("show", "abc:t_x.py"): (0, b"assert '\xff'\n", b"")})
    assert case_history.text_at("abc", "t_x.py") == "assert '�'\n"


def test_text_at_is_empty_when_the_file_cannot_be_shown(case_history, runs):
    runs({})
    assert case_history.text_at("abc", "t_x.py") == ""


def test_text_at_lets_stderr_through_unless_asked_to_be_quiet(case_history, runs):
    fake = runs({("show", "abc:t_x.py"): (0, b"", b"")})
    case_history.text_at("abc", "t_x.py")
    case_history.text_at("abc", "t_x.py", quiet=True)
    assert [kwargs["stderr"] for _, kwargs in fake.seen] == [None, subprocess.DEVNULL]


def test_cases_at_names_each_case_with_its_body(case_history, runs):
    runs({("show", "abc:t_x.py"): (0, SUITE.encode(), b"")})
    assert case_history.cases_at("abc", "t_x.py") == {
        "test_a": "def test_a():\n    assert 1", "test_b": "def test_b():\n    assert 2"}


def test_cases_at_is_empty_for_a_file_absent_from_a_readable_revision(case_history, runs):
    runs({("show", "abc:t_x.py"): (128, b"", b"fatal: path does not exist\n"),
          ("ls-tree", "--name-only", "abc", "--", "t_x.py"): (0, b"", b"")})
    assert case_history.cases_at("abc", "t_x.py") == {}


def test_cases_at_raises_oserror_naming_the_command_when_the_revision_cannot_be_read(case_history, runs):
    runs({("show", "nope:t_x.py"): (128, b"", b"fatal: bad object\n  nope\n")})
    with pytest.raises(OSError, match=r"^git show nope:t_x\.py failed: fatal: bad object nope$"):
        case_history.cases_at("nope", "t_x.py")


def test_revisions_lists_the_commits_that_touched_the_path_newest_first(case_history, runs):
    runs({("log", "--format=%H", "--", "t_x.py"): (0, b"bbb\naaa\n", b"")})
    assert case_history.revisions("t_x.py") == ["bbb", "aaa"]


def test_revisions_is_empty_when_git_cannot_log(case_history, runs):
    runs({})
    assert case_history.revisions("t_x.py") == []


def test_revisions_since_a_base_lists_only_the_commits_after_it(case_history, runs):
    runs({("log", "--format=%H", "base..HEAD", "--", "t_x.py"): (0, b"bbb\n", b"")})
    assert case_history.revisions("t_x.py", since="base") == ["bbb"]


def test_paths_at_lists_the_files_directly_in_a_directory(case_history, runs):
    runs({("ls-tree", "--name-only", "abc", "--", "cmd/x/"): (0, b"cmd/x/a_test.go\ncmd/x/b_test.go\n", b"")})
    assert case_history.paths_at("abc", "cmd/x") == ["cmd/x/a_test.go", "cmd/x/b_test.go"]


def test_paths_at_lists_the_root_level_files_for_the_empty_directory_4606(case_history, runs):
    runs({("ls-tree", "--name-only", "abc", "--", "."): (0, b"a_test.go\nb_test.go\n", b"")})
    assert case_history.paths_at("abc", "") == ["a_test.go", "b_test.go"]


def test_paths_at_is_empty_when_git_cannot_list(case_history, runs):
    runs({})
    assert case_history.paths_at("abc", "cmd/x") == []


def test_subject_is_the_first_line_of_the_commit_message(case_history, runs):
    runs({("log", "-1", "--format=%s", "abc"): (0, b"refactor: tidy\n", b"")})
    assert case_history.subject("abc") == "refactor: tidy\n"


def test_subject_is_empty_when_git_cannot_log(case_history, runs):
    runs({})
    assert case_history.subject("abc") == ""


def test_first_revision_with_is_the_oldest_commit_changing_the_occurrences_of_the_text(case_history, runs):
    runs({("log", "--reverse", "--format=%H", "-Sstep one", "--", "ledger.md"): (0, b"aaa\nbbb\n", b"")})
    assert case_history.first_revision_with("step one", "ledger.md") == "aaa"


def test_first_revision_with_is_empty_when_no_commit_changes_it(case_history, runs):
    runs({("log", "--reverse", "--format=%H", "-Sstep one", "--", "ledger.md"): (0, b"", b"")})
    assert case_history.first_revision_with("step one", "ledger.md") == ""


DIFF = ("diff", "--name-only", "--no-renames", "-z", "HEAD")
UNTRACKED = ("ls-files", "--others", "--exclude-standard", "--full-name", "-z", ":/")


def test_changed_test_files_lists_changed_then_untracked_test_files_and_no_others(case_history, runs):
    runs({DIFF: (0, b"src/test_a.py\0src/app.py\0", b""), UNTRACKED: (0, b"src/test_b.py\0notes.md\0", b"")})
    assert case_history.changed_test_files() == ["src/test_a.py", "src/test_b.py"]


def test_changed_test_files_is_empty_when_nothing_changed(case_history, runs):
    runs({DIFF: (0, b"", b""), UNTRACKED: (0, b"", b"")})
    assert case_history.changed_test_files() == []


def test_changed_test_files_raises_oserror_naming_the_failed_listing(case_history, runs):
    runs({DIFF: (0, b"", b""), UNTRACKED: (128, b"", b"fatal: not a\n  repository\n")})
    with pytest.raises(OSError, match=r"^git ls-files failed: fatal: not a repository$"):
        case_history.changed_test_files()


def ledger_history(ledger_path, texts, tails=None):
    """Answers for a ledger committed as c1, c2, ...: its log, each revision's text, and rev-list ranges."""
    revs = ["c%d" % (i + 1) for i in range(len(texts))]
    answers = {("log", "--reverse", "--format=%H", "--", ledger_path): (0, ("\n".join(revs) + "\n").encode(), b"")}
    for rev, text in zip(revs, texts):
        answers[("show", "%s:%s" % (rev, ledger_path))] = (0, text.encode(), b"")
    for (first, last), listed in (tails or {}).items():
        answers[("rev-list", "%s..%s" % (first, last))] = (0, listed.encode(), b"")
    return answers


@pytest.fixture
def ledger_path():
    return importlib.import_module("veri.run_dir").ledger(".", "7")


LEDGER = ["- [ ] a\n- [ ] b\n", "- [x] a\n- [ ] b\n", "- [x] a\n- [x] b\n"]


def test_step_commits_are_those_after_the_previous_tick_up_to_the_one_that_ticked_the_step(
        case_history, runs, ledger_path):
    runs(ledger_history(ledger_path, LEDGER, {("c2", "c3"): "c3\n"}))
    assert case_history.step_commits("b", "7") == {"c3"}


def test_step_commits_of_the_first_step_run_from_the_first_ledger_commit(case_history, runs, ledger_path):
    runs(ledger_history(ledger_path, LEDGER, {("c1", "c2"): "x1\nx2\n"}))
    assert case_history.step_commits("a", "7") == {"x1", "x2"}


def test_step_commits_of_a_step_committed_but_not_ticked_run_to_head(case_history, runs, ledger_path):
    runs(ledger_history(ledger_path, LEDGER[:2], {("c2", "HEAD"): "h1\n"}))
    assert case_history.step_commits("b", "7") == {"h1"}


def test_step_commits_raises_lookup_error_for_a_step_no_committed_ledger_line_holds(case_history, runs, ledger_path):
    runs(ledger_history(ledger_path, LEDGER))
    with pytest.raises(LookupError, match=r"^step zzz: no committed ledger line of it was found"):
        case_history.step_commits("zzz", "7")


def test_step_commits_raises_lookup_error_without_an_issue(case_history, runs):
    runs({})
    with pytest.raises(LookupError, match=r"^step b: no committed ledger line of it was found"):
        case_history.step_commits("b", "")


def test_step_commits_raises_oserror_when_the_ledger_log_fails(case_history, runs, ledger_path):
    runs({})
    with pytest.raises(OSError, match=r"^git log --reverse --format=%H -- .*failed: fatal: nope$"):
        case_history.step_commits("b", "7")


def test_commit_of_is_the_sha_the_revision_names(case_history, runs):
    runs({("rev-parse", "--verify", "--quiet", "v1^{commit}"): (0, b"abc123\n", b"")})
    assert case_history.commit_of("v1") == "abc123"


def test_commit_of_raises_oserror_when_the_revision_names_no_commit(case_history, runs):
    runs({})
    with pytest.raises(OSError, match=r"^git rev-parse --verify --quiet v1\^\{commit\} failed: fatal: nope$"):
        case_history.commit_of("v1")
