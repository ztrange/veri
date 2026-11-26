"""In-process cases for veri/refactor_touched.py, the module refactor-touched.sh is a shim over."""
import importlib
import subprocess
import sys

import pytest

USAGE = "usage: refactor-touched.sh <commit> | --issue <base> [--candidate <text>]\n"


@pytest.fixture
def refactor_touched():
    return importlib.import_module("veri.refactor_touched")


def test_main_with_no_commit_or_no_base_returns_2_with_the_usage_line_alone_and_no_process(
        monkeypatch, capsys, refactor_touched, fake_processes):
    calls = fake_processes()

    for argv in ([], ["--issue"]):
        code = refactor_touched.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)

    assert calls == []


def test_main_with_an_unresolvable_commit_returns_2_naming_it_then_the_usage_line_and_runs_no_diff(
        monkeypatch, capsys, refactor_touched, fake_processes):
    sha = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    fake = fake_processes.answers({"git rev-parse --verify --quiet": (1, "", "")}, default=(0, "", ""))

    code = refactor_touched.main([sha])
    captured = capsys.readouterr()

    assert (code, captured.out, captured.err) == (
        2, "", f"refactor-touched: cannot resolve commit '{sha}'\n" + USAGE)
    assert [c for c in fake.argvs if c[:2] == ["git", "diff"]] == []


def test_main_prints_the_commits_paths_outside_tdd_comma_joined_or_returns_3_when_only_tdd_changed(
        monkeypatch, capsys, refactor_touched, fake_processes):
    sha = "0123456789abcdef0123456789abcdef01234567"
    answers = {}
    fake_processes.answers({
        f"git diff --name-only {sha}^ {sha}": lambda line, **kwargs: (0, answers["diff"], "")},
        default=(0, "", ""), exact=True)

    answers["diff"] = "skills/b.sh\n.tdd/issue-1-plan.md\nsub/.tdd/x\na.py\n"
    code = refactor_touched.main([sha])
    captured = capsys.readouterr()
    assert (code, captured.out) == (0, "skills/b.sh,sub/.tdd/x,a.py\n")

    answers["diff"] = ".tdd/issue-1-plan.md\n.tdd/issue-1-skill-commit\n"
    code = refactor_touched.main([sha])
    captured = capsys.readouterr()
    assert (code, captured.out) == (3, "")


def test_main_with_issue_diffs_base_against_head_and_ignores_trailing_and_non_first_issue_arguments(
        monkeypatch, capsys, refactor_touched, fake_processes):
    base = "fedcba9876543210fedcba9876543210fedcba98"
    sha = "0123456789abcdef0123456789abcdef01234567"
    answers = {"resolves": True}
    fake = fake_processes.answers({
        "git rev-parse --verify --quiet": lambda line, **kwargs: (0 if answers["resolves"] else 1, "", ""),
        f"git diff --name-only {base} HEAD": lambda line, **kwargs: (0, answers["diff"], ""),
        f"git diff --name-only {sha}^ {sha}": (0, "c.sh\n", "")},
        default=(0, "", ""), exact=False)

    def answer(argv):
        code = refactor_touched.main(argv)
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    answers["diff"] = "a.py\n.tdd/issue-1-plan.md\nb.sh\n"
    assert answer(["--issue", base]) == (0, "a.py,b.sh\n", "")
    assert ["git", "diff", "--name-only", base, "HEAD"] in fake.argvs
    assert answer(["--issue", base, "extra"]) == (0, "a.py,b.sh\n", "")

    answers["diff"] = ".tdd/issue-1-plan.md\n"
    assert answer(["--issue", base]) == (3, "", "")

    assert answer([sha, "extra"]) == (0, "c.sh\n", "")
    assert answer([sha, "--issue", base]) == (0, "c.sh\n", "")

    answers["resolves"] = False
    assert answer(["--issue", base]) == (
        2, "", f"refactor-touched: cannot resolve commit '{base}'\n" + USAGE)


def test_main_refuses_an_empty_commit_or_base_and_filters_only_paths_starting_tdd_printed_as_git_prints_them(
        monkeypatch, capsys, refactor_touched, fake_processes):
    sha = "0123456789abcdef0123456789abcdef01234567"
    calls = fake_processes()

    for argv in ([""], ["--issue", ""]):
        code = refactor_touched.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)
    assert calls == []

    diff = 'sub/.tdd/x\n".tdd/\\303\\244.sh"\n.tdd/issue-1-plan.md\na,b.sh\n'
    fake_processes.answers({f"git diff --name-only {sha}^ {sha}": (0, diff, "")}, default=(0, "", ""))

    code = refactor_touched.main([sha])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (
        0, 'sub/.tdd/x,".tdd/\\303\\244.sh",a,b.sh\n', "")


def test_main_runs_git_in_the_callers_directory_letting_its_stderr_through_on_a_failed_rev_parse_or_diff(
        monkeypatch, capsys, tmp_path, refactor_touched, fake_processes):
    root = "0123456789abcdef0123456789abcdef01234567"
    answers = {}

    def stage(name):
        def answer(line, **kwargs):
            code, err = answers[name]
            if err and kwargs.get("stderr") not in (subprocess.PIPE, subprocess.DEVNULL,
                                                     subprocess.STDOUT):
                print(err, file=sys.stderr, end="")
            return code, "", None
        return answer

    fake = fake_processes.answers({"git rev-parse": stage("rev-parse"), "git diff": stage("diff")},
                                  default=(0, "", ""))
    monkeypatch.chdir(tmp_path)

    fatal = "fatal: not a git repository (or any of the parent directories): .git\n"
    answers["rev-parse"] = (128, fatal)
    code = refactor_touched.main(["HEAD"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (
        2, "", fatal + "refactor-touched: cannot resolve commit 'HEAD'\n" + USAGE)

    ambiguous = f"fatal: ambiguous argument '{root}^': unknown revision or path not in the working tree.\n"
    answers["rev-parse"] = (0, "")
    answers["diff"] = (128, ambiguous)
    code = refactor_touched.main([root])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (3, "", ambiguous)

    assert all(args[0] == "git" and "-C" not in args and "cwd" not in kwargs
               for args, kwargs in fake.seen)
