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
        monkeypatch, capsys, dispatch):
    launches = []
    waits = []

    def wait():
        waits.append(1)
        raise _StopWaiting

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
