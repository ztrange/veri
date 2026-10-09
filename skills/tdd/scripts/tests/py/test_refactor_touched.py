"""In-process cases for veri/refactor_touched.py, the module refactor-touched.sh is a shim over."""
import importlib
import subprocess
import sys

import pytest

USAGE = "usage: refactor-touched.sh <commit> | --issue <base>\n"


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
        monkeypatch, capsys, refactor_touched):
    sha = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    calls = []

    def fake(args, *rest, **kwargs):
        calls.append(list(args))
        code = 1 if list(args)[:4] == ["git", "rev-parse", "--verify", "--quiet"] else 0
        return subprocess.CompletedProcess(args, code, "", "")

    for entry in ("run", "Popen", "call", "check_call", "check_output"):
        monkeypatch.setattr(subprocess, entry, fake)

    code = refactor_touched.main([sha])
    captured = capsys.readouterr()

    assert (code, captured.out, captured.err) == (
        2, "", f"refactor-touched: cannot resolve commit '{sha}'\n" + USAGE)
    assert [c for c in calls if c[:2] == ["git", "diff"]] == []


def test_main_prints_the_commits_paths_outside_tdd_comma_joined_or_returns_3_when_only_tdd_changed(
        monkeypatch, capsys, refactor_touched):
    sha = "0123456789abcdef0123456789abcdef01234567"
    answers = {}

    def fake(args, *rest, **kwargs):
        args = list(args)
        if args == ["git", "diff", "--name-only", f"{sha}^", sha]:
            out = answers["diff"]
            if not kwargs.get("text") and not kwargs.get("universal_newlines") \
                    and not kwargs.get("encoding"):
                out = out.encode()
            return subprocess.CompletedProcess(args, 0, out, "")
        return subprocess.CompletedProcess(args, 0, "", "")

    for entry in ("run", "Popen", "call", "check_call"):
        monkeypatch.setattr(subprocess, entry, fake)
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: fake(*a, **k).stdout)

    answers["diff"] = "skills/b.sh\n.tdd/issue-1-plan.md\nsub/.tdd/x\na.py\n"
    code = refactor_touched.main([sha])
    captured = capsys.readouterr()
    assert (code, captured.out) == (0, "skills/b.sh,sub/.tdd/x,a.py\n")

    answers["diff"] = ".tdd/issue-1-plan.md\n.tdd/issue-1-skill-commit\n"
    code = refactor_touched.main([sha])
    captured = capsys.readouterr()
    assert (code, captured.out) == (3, "")


def test_main_with_issue_diffs_base_against_head_and_ignores_trailing_and_non_first_issue_arguments(
        monkeypatch, capsys, refactor_touched):
    base = "fedcba9876543210fedcba9876543210fedcba98"
    sha = "0123456789abcdef0123456789abcdef01234567"
    answers = {"resolves": True}
    calls = []

    def fake(args, *rest, **kwargs):
        args = list(args)
        calls.append(args)
        if args[:4] == ["git", "rev-parse", "--verify", "--quiet"]:
            return subprocess.CompletedProcess(args, 0 if answers["resolves"] else 1, "", "")
        if args == ["git", "diff", "--name-only", base, "HEAD"]:
            out = answers["diff"]
        elif args == ["git", "diff", "--name-only", f"{sha}^", sha]:
            out = "c.sh\n"
        else:
            out = ""
        if not kwargs.get("text") and not kwargs.get("universal_newlines") \
                and not kwargs.get("encoding"):
            out = out.encode()
        return subprocess.CompletedProcess(args, 0, out, "")

    for entry in ("run", "Popen", "call", "check_call"):
        monkeypatch.setattr(subprocess, entry, fake)
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: fake(*a, **k).stdout)

    def answer(argv):
        code = refactor_touched.main(argv)
        captured = capsys.readouterr()
        return code, captured.out, captured.err

    answers["diff"] = "a.py\n.tdd/issue-1-plan.md\nb.sh\n"
    assert answer(["--issue", base]) == (0, "a.py,b.sh\n", "")
    assert ["git", "diff", "--name-only", base, "HEAD"] in calls
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

    def fake(args, *rest, **kwargs):
        args = list(args)
        out = diff if args == ["git", "diff", "--name-only", f"{sha}^", sha] else ""
        if not kwargs.get("text") and not kwargs.get("universal_newlines") \
                and not kwargs.get("encoding"):
            out = out.encode()
        return subprocess.CompletedProcess(args, 0, out, "")

    for entry in ("run", "Popen", "call", "check_call"):
        monkeypatch.setattr(subprocess, entry, fake)
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: fake(*a, **k).stdout)

    code = refactor_touched.main([sha])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (
        0, 'sub/.tdd/x,".tdd/\\303\\244.sh",a,b.sh\n', "")


def test_main_runs_git_in_the_callers_directory_letting_its_stderr_through_on_a_failed_rev_parse_or_diff(
        monkeypatch, capsys, tmp_path, refactor_touched):
    root = "0123456789abcdef0123456789abcdef01234567"
    answers = {}
    calls = []

    def fake(args, *rest, **kwargs):
        args = list(args)
        calls.append((args, kwargs))
        if args[:2] == ["git", "rev-parse"]:
            code, err = answers["rev-parse"]
        elif args[:2] == ["git", "diff"]:
            code, err = answers["diff"]
        else:
            code, err = 0, ""
        if err and kwargs.get("stderr") not in (subprocess.PIPE, subprocess.DEVNULL,
                                                 subprocess.STDOUT):
            print(err, file=sys.stderr, end="")
        out = ""
        if not kwargs.get("text") and not kwargs.get("universal_newlines") \
                and not kwargs.get("encoding"):
            out = out.encode()
        return subprocess.CompletedProcess(args, code, out, None)

    for entry in ("run", "Popen", "call", "check_call"):
        monkeypatch.setattr(subprocess, entry, fake)
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: fake(*a, **k).stdout)
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
               for args, kwargs in calls)
