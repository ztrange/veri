"""In-process cases for veri/issue_worktree.py, the module issue-worktree.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: issue-worktree.sh <n> <slug> | --remove <n>\n"


@pytest.fixture
def issue_worktree():
    return importlib.import_module("veri.issue_worktree")


def fake_git(monkeypatch, answers):
    """subprocess.run answering each git argv tuple in <answers> with (exit code, stdout); every call recorded."""
    calls = []

    def fake_run(args, **kwargs):
        calls.append(list(args))
        code, stdout = answers.get(tuple(args), (None, None))
        if code is None:
            raise AssertionError("unexpected command: %r" % (args,))
        if kwargs.get("check") and code != 0:
            raise subprocess.CalledProcessError(code, args, stdout, "")
        return subprocess.CompletedProcess(args, code, stdout, "")

    def refused(*args, **kwargs):
        calls.append(list(args[0]) if args else kwargs)
        raise AssertionError("unexpected process: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    for name in ("Popen", "call", "check_call", "check_output", "getoutput", "getstatusoutput"):
        monkeypatch.setattr(subprocess, name, refused)
    return calls


def test_main_refuses_a_bad_argument_list_with_the_usage_line_before_any_git_and_maps_a_dying_git_to_2(
        monkeypatch, capsys, issue_worktree):
    for argv in ([], ["270"], ["--remove"], ["", "x"], ["7", ""]):
        calls = fake_git(monkeypatch, {})

        code = issue_worktree.main(argv)

        assert (argv, code, calls, capsys.readouterr()[:]) == (argv, 2, [], ("", USAGE))

    calls = fake_git(monkeypatch, {("git", "worktree", "list", "--porcelain"): (128, "")})

    code = issue_worktree.main(["7", "slug"])

    assert (code, capsys.readouterr().out, calls[:1]) == (2, "", [["git", "worktree", "list", "--porcelain"]])
