"""In-process cases for veri/workqueue.py, the module workqueue.sh is a shim over."""
import importlib
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = """workqueue.sh: usage: workqueue.sh assign <worker> <issue>...
                     workqueue.sh next <worker>
                     workqueue.sh start <worker> <issue>
                     workqueue.sh done <worker> <issue> <merge-sha>
                     workqueue.sh park <worker> <issue> <reason>
                     workqueue.sh show [<worker>]
"""


@pytest.fixture(autouse=True)
def no_ambient_tunables(monkeypatch):
    for name in ("VERI_GH_JSON", "VERI_WORKQUEUE_LOCK_WAIT"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def workqueue():
    return importlib.import_module("veri.workqueue")


def fake_git(monkeypatch, main_tree):
    """subprocess.run answering `git worktree list` with <main_tree> and `git remote get-url origin` with no origin."""
    def fake_run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "list"]:
            return subprocess.CompletedProcess(args, 0, "worktree %s\nHEAD abc\nbranch refs/heads/main\n\n" % main_tree, "")
        if list(args[:3]) == ["git", "remote", "get-url"]:
            return subprocess.CompletedProcess(args, 2, "", "error: No such remote 'origin'\n")
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)


def test_main_refuses_bad_arguments_with_2_and_the_usage_text_and_answers_next_with_nothing_launchable_as_3(tmp_path, monkeypatch, capsys, workqueue):
    fake_git(monkeypatch, tmp_path)
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    queue.write_bytes(b"alpha\t12\tqueued\t\n")
    fixture = tmp_path / "gh"
    fixture.mkdir()
    (fixture / "issues.json").write_text('[{"number": 12, "state": "OPEN", "body": ""}]')

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    assert run([]) == (2, "", "workqueue.sh: unknown subcommand: \n" + USAGE)
    assert run(["done", "alpha", "12"]) == (2, "", USAGE)
    assert run(["assign", "alpha", "12", "12"]) == (2, "", "workqueue.sh: issue 12 is named twice\n" + USAGE)
    monkeypatch.setenv("VERI_GH_JSON", str(fixture))
    code, out, _ = run(["next", "beta"])
    assert (code, out) == (3, "")


def test_start_naming_no_queued_item_of_the_worker_returns_1_and_leaves_the_main_working_tree_queue_unchanged(tmp_path, monkeypatch, capsys, workqueue):
    fake_git(monkeypatch, tmp_path)
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    before = b"alpha\t12\tqueued\t\nalpha\t13\trunning\t\n"
    queue.write_bytes(before)

    code = workqueue.main(["start", "beta", "12"])
    _, err = capsys.readouterr()

    assert (code, err) == (1, "workqueue.sh: beta holds no queued item for issue 12\n")
    assert queue.read_bytes() == before
