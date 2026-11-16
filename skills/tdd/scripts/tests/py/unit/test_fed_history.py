"""The fed_history fixture: case_history answered from a table of named revisions (PRD 017.5, R26, R27)."""
import importlib

import pytest


@pytest.fixture
def tests_frozen():
    return importlib.import_module("veri.tests_frozen")


LEDGER = ".tdd/issue-7.md"
ONE = "def test_one():\n    assert 1\n"
TWO = "def test_two():\n    assert 2\n"
SUITE, GONE = "tests/test_a.py", "tests/test_gone.py"  # names, not literals, in calls: a literal suite path reads as a nested run


def test_fed_history_answers_every_case_history_query_tests_frozen_makes_from_its_table_of_named_revisions(
        tmp_path, fed_history, tests_frozen):
    fed_history(("base", "start", {"tests/test_a.py": ONE, "src/a.py": "x = 1\n",
                                   LEDGER: "# Plan for #7\n\n- [ ] step one\n- [ ] step two\n"}),
                ("red", "red: test_two", {"tests/test_a.py": ONE + "\n\n" + TWO}),
                ("green", "green: step one", {"src/a.py": "x = 2\n",
                                              LEDGER: "# Plan for #7\n\n- [x] step one\n- [ ] step two\n"}),
                ("later", "red: step two", {"src/a.py": "x = 3\n"}),
                root=tmp_path, branch="tdd/7-thing")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text(ONE)
    (tmp_path / "tests" / "test_b.py").write_text(TWO)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 4\n")
    history = tests_frozen.case_history

    answers = {
        "toplevel": history.toplevel(),
        "has_rev": [history.has_rev(rev) for rev in ("HEAD", "HEAD~1", "base", "HEAD~4", "nowhere")],
        "current_branch": history.current_branch(),
        "text_at": [history.text_at("HEAD~3", SUITE, quiet=True), history.text_at("red", "gone.py")],
        "cases_at": [sorted(history.cases_at(rev, SUITE)) for rev in ("base", "HEAD")],
        "cases_at absent": history.cases_at("HEAD", GONE),
        "revisions": [history.revisions(SUITE), history.revisions("src/a.py", since="red")],
        "first_revision_with": [history.first_revision_with("test_two", SUITE),
                                history.first_revision_with("never", SUITE)],
        "changed_test_files": history.changed_test_files(),
        "commit_of": history.commit_of("HEAD~2"),
        "step_commits": [sorted(history.step_commits("step one", "7")), sorted(history.step_commits("step two", "7"))],
    }

    assert answers == {
        "toplevel": str(tmp_path),
        "has_rev": [True, True, True, False, False],
        "current_branch": "tdd/7-thing",
        "text_at": [ONE, ""],
        "cases_at": [["test_one"], ["test_one", "test_two"]],
        "cases_at absent": {},
        "revisions": [["red", "base"], ["later", "green"]],
        "first_revision_with": ["red", ""],
        "changed_test_files": ["tests/test_a.py", "tests/test_b.py"],
        "commit_of": "red",
        "step_commits": [["green", "red"], ["later"]],
    }


def test_fed_history_fails_the_case_naming_a_case_history_query_its_table_does_not_answer_past_any_except_exception(
        fed_history, tests_frozen):
    fed_history(("base", "start", {"test_a.py": ONE}), ("next", "more", {"test_a.py": ONE + "\n\n" + TWO}))

    with pytest.raises(BaseException) as raised:
        try:
            tests_frozen.case_history.default_branch()
        except Exception:
            pass

    assert (type(raised.value) is pytest.fail.Exception, str(raised.value)) == (
        True, "fed_history does not answer case_history.default_branch")


def test_fed_history_answers_subject_with_the_revisions_subject_as_git_log_prints_it(fed_history, tests_frozen):
    fed_history(("base", "start", {"test_a.py": ONE}), ("next", "refactor: more", {"test_a.py": ONE + "\n\n" + TWO}))
    history = tests_frozen.case_history

    assert [history.subject(rev) for rev in ("HEAD", "HEAD~1", "base")] == ["refactor: more\n", "start\n", "start\n"]


def test_fed_history_answers_a_file_named_by_its_absolute_path_under_the_root_as_git_does_by_its_relative_path(
        tmp_path, fed_history, tests_frozen):
    fed_history(("base", "start", {SUITE: ONE}), ("red", "red: test_two", {SUITE: ONE + "\n\n" + TWO}), root=tmp_path)
    history, absolute = tests_frozen.case_history, str(tmp_path / SUITE)

    assert {
        "text_at": history.text_at("base", absolute),
        "cases_at": sorted(history.cases_at("HEAD", absolute)),
        "revisions": history.revisions(absolute, since="base"),
        "first_revision_with": history.first_revision_with("test_two", absolute),
    } == {"text_at": ONE, "cases_at": ["test_one", "test_two"], "revisions": ["red"], "first_revision_with": "red"}


def test_fed_history_answers_a_revision_followed_by_a_caret_as_its_first_parent_as_git_does(fed_history, tests_frozen):
    fed_history(("base", "start", {SUITE: ONE}), ("next", "more", {SUITE: ONE + "\n\n" + TWO}),
                ("last", "again", {SUITE: TWO}))
    history = tests_frozen.case_history

    assert {
        "text_at": [history.text_at(rev, SUITE) for rev in ("last^", "next^", "HEAD^", "base^")],
        "has_rev": [history.has_rev(rev) for rev in ("next^", "base^")],
        "commit_of": history.commit_of("last^"),
    } == {"text_at": [ONE + "\n\n" + TWO, ONE, ONE + "\n\n" + TWO, ""], "has_rev": [True, False], "commit_of": "next"}


def test_fed_history_answers_a_ref_and_a_detached_revision_by_name_and_default_branch_with_the_default_it_is_fed(
        fed_history, tests_frozen):
    fed_history(("base", "start", {SUITE: ONE}), ("next", "more", {SUITE: ONE + "\n\n" + TWO}),
                refs={"origin/main": "base"}, detached={"pre": ("before the rebase", {SUITE: TWO})},
                default="main")
    history = tests_frozen.case_history

    assert {
        "default_branch": history.default_branch(),
        "ref": (history.has_rev("origin/main"), history.commit_of("origin/main"),
                sorted(history.cases_at("origin/main", SUITE)), history.subject("origin/main")),
        "detached": (history.has_rev("pre"), history.commit_of("pre"), history.text_at("pre", SUITE),
                     sorted(history.cases_at("pre", SUITE)), history.subject("pre")),
        "line": history.revisions(SUITE),
    } == {
        "default_branch": "main",
        "ref": (True, "base", ["test_one"], "start\n"),
        "detached": (True, "pre", TWO, ["test_two"], "before the rebase\n"),
        "line": ["next", "base"],
    }


def test_fed_history_answers_revisions_since_a_revision_off_the_line_with_none_as_case_history_answers_a_failed_git_log(
        fed_history, tests_frozen):
    fed_history(("base", "start", {SUITE: ONE}), ("next", "more", {SUITE: ONE + "\n\n" + TWO}),
                detached={"pre": ("before the rebase", {SUITE: TWO})})
    history = tests_frozen.case_history

    assert [history.revisions(SUITE, since=rev) for rev in ("pre", "nowhere", "base")] == [[], [], ["next"]]


def test_fed_commits_checks_out_an_earlier_revision_as_git_checkout_would_keeping_the_later_ones_readable_and_names_a_ref_at_its_head(
        tmp_path, fed_commits, tests_frozen):
    repo = fed_commits(default="main")
    (tmp_path / "tests").mkdir()
    (tmp_path / SUITE).write_text(ONE)
    repo.add("tests")
    base = repo.commit("base")
    (tmp_path / SUITE).write_text(TWO)
    (tmp_path / "lib.py").write_text("one\n")
    (tmp_path / "notes.txt").write_text("untracked\n")
    repo.add("tests", "lib.py")
    work = repo.commit("work")
    repo.checkout(base)
    on_disk = ((tmp_path / SUITE).read_text(), (tmp_path / "lib.py").exists(), (tmp_path / "notes.txt").read_text())
    (tmp_path / SUITE).write_text(ONE + "\n\n" + TWO)
    upstream = repo.commit("upstream", all=True)
    repo.ref("origin/main")
    history = tests_frozen.case_history

    assert {
        "on disk": on_disk,
        "names": [base, work, upstream],
        "line": history.revisions(SUITE),
        "work": (history.text_at(work, SUITE), history.text_at(work, "lib.py"), history.subject(work)),
        "origin": (history.commit_of("origin/main"), history.default_branch()),
        "head": (history.text_at("HEAD", SUITE), history.text_at("HEAD", "lib.py")),
    } == {
        "on disk": (ONE, False, "untracked\n"),
        "names": ["c1", "c2", "c3"],
        "line": ["c3", "c1"],
        "work": (TWO, "one\n", "work\n"),
        "origin": ("c3", "main"),
        "head": (ONE + "\n\n" + TWO, ""),
    }


def test_fed_commits_commits_the_work_tree_as_git_add_and_git_commit_would_and_answers_the_pass_markers_git_calls(
        tmp_path, fed_commits, tests_frozen, monkeypatch):
    monkeypatch.chdir(tmp_path)
    repo = fed_commits()
    history = tests_frozen.case_history
    unborn = (history.has_rev("HEAD"), history.changed_test_files())
    (tmp_path / "tests").mkdir()
    (tmp_path / SUITE).write_text(ONE)
    (tmp_path / "notes.txt").write_text("one\n")
    repo.add("tests", "notes.txt")
    base = repo.commit("base")
    (tmp_path / SUITE).write_text(ONE + "\n\n" + TWO)
    (tmp_path / "notes.txt").write_text("two\n")
    repo.add("tests")
    (tmp_path / SUITE).write_text(TWO)
    staged = repo.commit("red: stage the suite only")
    repo.mv(SUITE, GONE)
    moved = repo.commit("refactor: move the suite")
    (tmp_path / "notes.txt").unlink()
    everything = repo.commit("drop the notes", all=True)
    marker = tests_frozen.frozen_record
    marker.write_pass_marker("a step", marker.work_tree_hash())

    assert {
        "unborn": unborn,
        "names": [base, staged, moved, everything, repo.head],
        "staged at add time": history.text_at(staged, SUITE),
        "notes unstaged": history.text_at(staged, "notes.txt"),
        "moved": (history.text_at(moved, SUITE), history.text_at(moved, GONE)),
        "deleted by -a": (history.has_rev(everything), history.text_at(everything, "notes.txt")),
        "subject": history.subject("HEAD~1"),
        "changed": history.changed_test_files(),
        "marker": (tmp_path / marker.pass_marker_path("a step")).read_text(),
    } == {
        "unborn": (False, []),
        "names": ["c1", "c2", "c3", "c4", "c4"],
        "staged at add time": ONE + "\n\n" + TWO,
        "notes unstaged": "one\n",
        "moved": ("", ONE + "\n\n" + TWO),
        "deleted by -a": (True, ""),
        "subject": "refactor: move the suite\n",
        "changed": [],
        "marker": "step: a step\nhead: c4\ntree: fed-tree\n",
    }
