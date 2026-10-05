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


def routing_git(monkeypatch, answers):
    """subprocess.run answering each git argv tuple in <answers> with (exit code, stdout, stderr), each stream sent where the call routes it."""
    calls = []

    def deliver(text, target):
        if target in (subprocess.PIPE, subprocess.DEVNULL):
            return
        if target is None:
            sys.stdout.write(text)
        elif target == 1:
            sys.stdout.write(text)
        elif target == 2 or target == subprocess.STDOUT:
            sys.stderr.write(text)
        else:
            target.write(text)

    def fake_run(args, **kwargs):
        calls.append(list(args))
        if tuple(args) not in answers:
            raise AssertionError("unexpected command: %r" % (args,))
        code, stdout, stderr = answers[tuple(args)]
        captured = kwargs.get("capture_output")
        out_to = subprocess.PIPE if captured else kwargs.get("stdout")
        err_to = subprocess.PIPE if captured else kwargs.get("stderr")
        deliver(stdout, out_to)
        deliver(stderr, 2 if err_to is None else err_to)
        if kwargs.get("check") and code != 0:
            raise subprocess.CalledProcessError(code, args, stdout, stderr)
        return subprocess.CompletedProcess(
            args, code, stdout if out_to == subprocess.PIPE else None, stderr if err_to == subprocess.PIPE else None)

    def refused(*args, **kwargs):
        raise AssertionError("unexpected process: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    for name in ("Popen", "call", "check_call", "check_output", "getoutput", "getstatusoutput"):
        monkeypatch.setattr(subprocess, name, refused)
    return calls


def test_main_remove_refuses_a_dirty_worktree_and_removes_a_clean_one_without_force_at_the_unnormalised_registry_path(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/a/../repo"
    path = main_tree + "/.tdd/wt/7"
    registry = ("worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
                "worktree /srv/other\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/x\n\n" % main_tree)
    listing = ("git", "worktree", "list", "--porcelain")
    status = ("git", "-C", path, "status", "--porcelain")
    remove = ("git", "worktree", "remove", path)

    calls = routing_git(monkeypatch, {listing: (0, registry, ""), status: (0, "?? stray\n", "")})
    code = issue_worktree.main(["--remove", "7"])
    assert (code, capsys.readouterr()[:], [c for c in calls if c[:3] == list(remove[:3])]) == (
        2, ("", "issue-worktree: %s has uncommitted changes — refusing to remove it\n" % path), [])

    for argv in (["--remove", "7"], ["--remove", "7", "extra"]):
        calls = routing_git(monkeypatch, {listing: (0, registry, ""), status: (0, "", ""),
                                          remove: (0, "removed it\n", "")})
        code = issue_worktree.main(argv)
        assert (argv, code, capsys.readouterr()[:], calls) == (
            argv, 0, ("", "removed it\n"), [list(listing), list(status), list(remove)])

    calls = routing_git(monkeypatch, {listing: (0, registry, ""),
                                      status: (128, "", "fatal: cannot change to '%s'\n" % path),
                                      remove: (128, "", "fatal: '%s' is not a working tree\n" % path)})
    code = issue_worktree.main(["--remove", "7"])
    assert (code, capsys.readouterr().out, calls) == (2, "", [list(listing), list(status), list(remove)])


def test_main_remove_returns_a_dying_gits_status_inside_0_to_3_as_it_is_and_maps_only_one_outside_to_2(
        monkeypatch, capsys, issue_worktree):
    main_tree = "/srv/repo"
    path = main_tree + "/.tdd/wt/7"
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n" % main_tree
    listing = ("git", "worktree", "list", "--porcelain")
    status = ("git", "-C", path, "status", "--porcelain")
    remove = ("git", "worktree", "remove", path)

    calls = routing_git(monkeypatch, {listing: (1, "", "error: listing failed\n")})
    code = issue_worktree.main(["--remove", "7"])
    assert (code, capsys.readouterr().out, calls) == (1, "", [list(listing)])

    for remove_code, want in ((1, 1), (128, 2)):
        calls = routing_git(monkeypatch, {listing: (0, registry, ""), status: (0, "", ""),
                                          remove: (remove_code, "", "error: remove failed\n")})
        code = issue_worktree.main(["--remove", "7"])
        assert (remove_code, code, capsys.readouterr().out, calls) == (
            remove_code, want, "", [list(listing), list(status), list(remove)])
