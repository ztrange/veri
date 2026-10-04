"""In-process cases for veri/workqueue.py, the module workqueue.sh is a shim over."""
import importlib
import json
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


def fake_git(monkeypatch, main_tree, origin=None):
    """subprocess.run answering `git worktree list` with <main_tree> and `git remote get-url origin` with <origin>, or no origin."""
    def fake_run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "list"]:
            return subprocess.CompletedProcess(args, 0, "worktree %s\nHEAD abc\nbranch refs/heads/main\n\n" % main_tree, "")
        if list(args[:3]) == ["git", "remote", "get-url"]:
            if origin is not None:
                return subprocess.CompletedProcess(args, 0, origin + "\n", "")
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


@pytest.mark.parametrize("answer", [
    subprocess.CompletedProcess([], 128, "", "fatal: not a git repository (or any of the parent directories): .git\n"),
    subprocess.CompletedProcess([], 0, "", ""),
], ids=["git-refused", "git-printed-nothing"])
def test_main_refuses_an_unknown_subcommand_with_2_and_writes_nothing_when_git_names_no_main_working_tree_and_ignores_extra_arguments(answer, tmp_path, monkeypatch, capsys, workqueue):
    def failing_run(args, **kwargs):
        if list(args[:3]) == ["git", "worktree", "list"]:
            if not kwargs.get("capture_output") and kwargs.get("stderr") is None:
                sys.stderr.write(answer.stderr)
            return subprocess.CompletedProcess(args, answer.returncode, answer.stdout, answer.stderr)
        raise AssertionError("unexpected command: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", failing_run)
    monkeypatch.chdir(tmp_path)

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    assert run([]) == (2, "", "workqueue.sh: unknown subcommand: \n" + USAGE)
    assert run(["bogus"]) == (2, "", "workqueue.sh: unknown subcommand: bogus\n" + USAGE)
    assert run(["bogus", "next", "beta"]) == (2, "", "workqueue.sh: unknown subcommand: bogus\n" + USAGE)
    assert run(["alpha", "start", "12"]) == (2, "", "workqueue.sh: unknown subcommand: alpha\n" + USAGE)
    assert list(tmp_path.iterdir()) == []

    fake_git(monkeypatch, tmp_path)
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    before = b"alpha\t12\tqueued\t\n"
    queue.write_bytes(before)
    fixture = tmp_path / "gh"
    fixture.mkdir()
    (fixture / "issues.json").write_text("[]")
    monkeypatch.setenv("VERI_GH_JSON", str(fixture))

    assert run(["start", "beta", "12", "extra"]) == (1, "", "workqueue.sh: beta holds no queued item for issue 12\n")
    assert run(["next", "beta", "extra"])[:2] == (3, "")
    assert queue.read_bytes() == before


def test_next_prints_the_workers_first_queued_item_with_no_open_blocker_reading_blockers_against_the_origin_slug(tmp_path, monkeypatch, capsys, workqueue):
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    before = (b"beta\t1\tqueued\t\nalpha\t2\trunning\t\nalpha\t012\tqueued\t\nalpha\t14\tqueued\t\n"
              b"alpha\t13\tqueued\t\nalpha\t99\tqueued\t\ngamma\t12\tqueued\t\n")
    queue.write_bytes(before)
    fixture = tmp_path / "gh"
    fixture.mkdir()
    (fixture / "issues.json").write_text(json.dumps([
        {"number": 1, "state": "OPEN", "body": ""},
        {"number": 2, "state": "OPEN", "body": ""},
        {"number": 5, "state": "open", "body": ""},
        {"number": 6, "state": "CLOSED", "body": ""},
        {"number": 7, "state": "Open", "body": None},
        {"number": 12, "state": "OPEN", "body": "Work.\n\n## Blocked by\n\n- #5\n- #6\n"},
        {"number": 14, "state": "OPEN", "body": "Work.\n\n## Blocked by\n\n- https://github.com/ztrange/veri/issues/7\n"},
        {"number": 13, "state": "OPEN", "body": "Work.\n\n## Blocked by\n\n- https://github.com/other/repo/issues/7\n- #6\n"},
    ]))
    monkeypatch.setenv("VERI_GH_JSON", str(fixture))

    def run(argv):
        code = workqueue.main(argv)
        out, err = capsys.readouterr()
        return code, out, err

    fake_git(monkeypatch, tmp_path, origin="https://github.com/ztrange/veri.git")
    assert run(["next", "alpha"]) == (0, "13\n", "")
    fake_git(monkeypatch, tmp_path, origin="git@github.com:ztrange/veri.git")
    assert run(["next", "alpha"]) == (0, "13\n", "")
    assert run(["next", "gamma"]) == (3, "", "")
    assert run(["next", "delta"]) == (3, "", "")
    fake_git(monkeypatch, tmp_path)
    assert run(["next", "alpha"]) == (0, "99\n", "")
    assert queue.read_bytes() == before


def test_next_reads_a_queue_line_of_three_tab_fields_and_a_queued_issue_whose_body_is_null(tmp_path, monkeypatch, capsys, workqueue):
    queue = tmp_path / ".tdd" / "workqueue"
    queue.parent.mkdir()
    before = b"alpha\t7\tqueued\n"
    queue.write_bytes(before)
    fixture = tmp_path / "gh"
    fixture.mkdir()
    (fixture / "issues.json").write_text(json.dumps([{"number": 7, "state": "OPEN", "body": None}]))
    monkeypatch.setenv("VERI_GH_JSON", str(fixture))
    fake_git(monkeypatch, tmp_path)

    code = workqueue.main(["next", "alpha"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "7\n", "")
    assert queue.read_bytes() == before
