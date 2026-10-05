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


@pytest.fixture
def issue_worktree():
    return importlib.import_module("veri.issue_worktree")


def _git(monkeypatch, answers):
    """subprocess faked in-process: each git call answers (status, stdout) from <answers> by its argument list; returns the calls made."""
    calls = []

    def answer(args, kwargs):
        calls.append(list(args))
        key = tuple(args[1:]) if pathlib.Path(args[0]).name == "git" else None
        if key not in answers:
            raise AssertionError("unexpected subprocess call: %r" % (args,))
        status, out = answers[key]
        if status and kwargs.get("check"):
            raise subprocess.CalledProcessError(status, args, out, "")
        return status, out

    def fake_run(args, *rest, **kwargs):
        status, out = answer(args, kwargs)
        return subprocess.CompletedProcess(args, status, out, "")

    def fake_check_output(args, *rest, **kwargs):
        status, out = answer(args, dict(kwargs, check=True))
        return out

    def fake_call(args, *rest, **kwargs):
        return answer(args, kwargs)[0]

    def fake_check_call(args, *rest, **kwargs):
        answer(args, dict(kwargs, check=True))
        return 0

    def fake_popen(args, *rest, **kwargs):
        raise AssertionError("unexpected subprocess.Popen: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    monkeypatch.setattr(subprocess, "call", fake_call)
    monkeypatch.setattr(subprocess, "check_call", fake_check_call)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    return calls


def test_main_refuses_a_missing_argument_with_the_usage_line_and_2_before_any_git_call_and_maps_git_s_128_to_2(
        capsys, monkeypatch, issue_worktree):
    usage = "usage: issue-worktree.sh <n> <slug> | --remove <n>\n"
    calls = _git(monkeypatch, {})
    answers = []
    for argv in ([], ["270"], ["--remove"], ["", "x"]):
        code = issue_worktree.main(argv)
        captured = capsys.readouterr()
        answers.append((argv, code, captured.out, captured.err))
    assert answers == [
        ([], 2, "", usage),
        (["270"], 2, "", usage),
        (["--remove"], 2, "", usage),
        (["", "x"], 2, "", usage),
    ]
    assert calls == []

    calls = _git(monkeypatch, {("worktree", "list", "--porcelain"): (128, "")})
    code = issue_worktree.main(["7", "slug"])
    captured = capsys.readouterr()
    assert (code, captured.out) == (2, "")
    assert [call[1:] for call in calls] == [["worktree", "list", "--porcelain"]]

    _git(monkeypatch, {("worktree", "list", "--porcelain"): (-9, "")})
    code = issue_worktree.main(["7", "slug"])
    captured = capsys.readouterr()
    assert (code, captured.out) == (2, "")


def test_main_hands_back_a_registered_worktree_keyed_on_n_alone_at_the_main_tree_s_unnormalised_path(
        tmp_path, capsys, monkeypatch, issue_worktree):
    (tmp_path / "a").mkdir()
    main_tree = "%s/a/../main" % tmp_path
    (tmp_path / "main" / ".tdd" / "wt" / "7").mkdir(parents=True)
    registry = (
        "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
        "worktree %s/.tdd/wt/7\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/tdd/7-slug\n\n"
        "worktree %s/.tdd/wt/abc\nHEAD 3333333333333333333333333333333333333333\nbranch refs/heads/tdd/abc-x\nprunable gitdir file points to non-existent location\n\n"
    ) % (main_tree, main_tree, main_tree)
    calls = _git(monkeypatch, {("worktree", "list", "--porcelain"): (0, registry)})
    answers = []
    for argv in (["7", "other"], ["7", "other", "extra"], ["7", "--remove"], ["abc", "slug"]):
        code = issue_worktree.main(argv)
        captured = capsys.readouterr()
        answers.append((argv, code, captured.out))
    assert answers == [
        (["7", "other"], 0, "%s/.tdd/wt/7\n" % main_tree),
        (["7", "other", "extra"], 0, "%s/.tdd/wt/7\n" % main_tree),
        (["7", "--remove"], 0, "%s/.tdd/wt/7\n" % main_tree),
        (["abc", "slug"], 0, "%s/.tdd/wt/abc\n" % main_tree),
    ]
    assert not (tmp_path / "main" / ".tdd" / "wt" / "abc").exists()
    assert [call[1:] for call in calls] == [["worktree", "list", "--porcelain"]] * 4


def test_main_hands_back_nothing_for_a_path_the_registry_only_nearly_holds(
        tmp_path, capsys, monkeypatch, issue_worktree):
    main_tree = "%s/a/../main" % tmp_path
    (tmp_path / "main" / ".tdd" / "wt" / "7").mkdir(parents=True)
    registry = (
        "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/main\n\n"
        "worktree %s/.tdd/wt/70\nHEAD 2222222222222222222222222222222222222222\nbranch refs/heads/tdd/70-x\n\n"
        "worktree %s/.tdd/wt/7/\nHEAD 3333333333333333333333333333333333333333\nbranch refs/heads/tdd/7-y\n\n"
        "worktree %s/main/.tdd/wt/7\nHEAD 4444444444444444444444444444444444444444\nbranch refs/heads/tdd/7-z\n\n"
    ) % (main_tree, main_tree, main_tree, tmp_path)
    calls = _git(monkeypatch, {("worktree", "list", "--porcelain"): (0, registry)})
    try:
        issue_worktree.main(["7", "slug"])
    except AssertionError as refused:
        assert str(refused).startswith("unexpected subprocess call")
    assert capsys.readouterr().out == ""
    assert calls[0][1:] == ["worktree", "list", "--porcelain"]
