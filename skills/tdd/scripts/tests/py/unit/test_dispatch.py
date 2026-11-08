"""In-process cases for veri/dispatch.py, the module dispatch.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def dispatch():
    return importlib.import_module("veri.dispatch")


def test_main_with_no_target_prints_the_usage_line_on_stderr_and_exits_2(run_cli, dispatch):
    code, out, err = run_cli(dispatch, [])
    assert (code, out, err) == (2, "", "usage: dispatch.sh --target <N>\n")


class _StopWaiting(Exception):
    pass


def test_main_with_fewer_live_conductors_than_target_launches_the_first_queued_issue_silently_and_keeps_waiting(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    launches = []
    waits = []

    def wait():
        waits.append(1)
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12", "15"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "2"])
    except _StopWaiting:
        code = None

    assert (launches, waits, code, capsys.readouterr().out) == (["12"], [1], None, "")


def test_launch_runs_run_conductor_through_detach_leaf_appending_its_output_to_the_conductor_log_with_stdin_from_dev_null(
        monkeypatch, tmp_path, dispatch):
    import os
    import subprocess
    scripts = os.path.dirname(os.path.dirname(os.path.abspath(dispatch.__file__)))
    (tmp_path / ".tdd").mkdir()
    log = tmp_path / ".tdd" / "conductor-12.log"
    log.write_bytes(b"earlier\n")
    calls = []

    def popen(argv, stdin=None, stdout=None, stderr=None, **kw):
        calls.append((list(argv), stdin, stdout is stderr))
        stdout.write(b"conductor output\n")
        stdout.flush()

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch.subprocess, "Popen", popen)

    dispatch.launch("12")

    assert (calls, log.read_bytes()) == (
        [([os.path.join(scripts, "detach-leaf.sh"), os.path.join(scripts, "run-conductor.sh"), "12"],
          subprocess.DEVNULL, True)],
        b"earlier\nconductor output\n")


def test_main_with_target_or_more_live_conductors_launches_nothing_and_signals_no_process_while_it_keeps_waiting(
        monkeypatch, capsys, dispatch):
    import os
    launches = []
    waits = []
    signals = []

    def wait():
        waits.append(1)
        raise _StopWaiting

    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5", "7"], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12", "15"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)
    monkeypatch.setattr(os, "kill", lambda pid, sig: signals.append((pid, sig)))

    try:
        code = dispatch.main(["--target", "2"])
    except _StopWaiting:
        code = None

    assert (launches, signals, waits, code, capsys.readouterr().out) == ([], [], [1], None, "")


def test_main_launches_the_next_issue_only_once_the_previous_launch_has_its_ledger_under_the_main_working_tree(
        monkeypatch, tmp_path, dispatch):
    launches = []
    seen_at_wait = []
    ledger = tmp_path / ".tdd" / "wt" / "12" / ".tdd" / "issue-12.md"
    ledger.parent.mkdir(parents=True)

    def wait():
        seen_at_wait.append(list(launches))
        if len(seen_at_wait) == 2:
            ledger.write_text("- [ ] step\n")
        if len(seen_at_wait) == 3:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues",
                        lambda: [i for i in ["12", "15", "18", "19"] if i not in launches], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "3"])

    assert seen_at_wait == [["12"], ["12"], ["12", "15"]]


def test_main_appends_one_launched_line_with_the_local_iso_time_to_dispatch_log_under_the_main_working_tree_per_launch(
        monkeypatch, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    waits = []
    launched = []

    def wait():
        waits.append(1)
        if len(waits) == 2:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: [i for i in ["12", "15"] if i not in launched], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: launched.append(issue) or (tmp_path / ".tdd" / "wt" / issue / ".tdd").mkdir(parents=True)
                        or (tmp_path / ".tdd" / "wt" / issue / ".tdd" / f"issue-{issue}.md").write_text("x"),
                        raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "2"])

    assert (tmp_path / ".tdd" / "dispatch.log").read_text() == (
        "launched 12 2026-11-07T10:30:00\nlaunched 15 2026-11-07T10:30:00\n")
