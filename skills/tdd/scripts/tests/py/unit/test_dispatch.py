"""In-process cases for veri/dispatch.py, the module dispatch.sh is a shim over."""
from datetime import datetime
import importlib
import sys

import pytest


@pytest.fixture
def dispatch():
    return importlib.import_module("veri.dispatch")


@pytest.fixture(autouse=True)
def no_unfaked_process_listing(monkeypatch, dispatch):
    real_run = dispatch.subprocess.run

    def run(argv, *args, **kw):
        if list(argv) == ["ps", "-axo", "args="]:
            raise AssertionError("unfaked queued_merges call: the case reads the real process table")
        return real_run(argv, *args, **kw)

    monkeypatch.setattr(dispatch.subprocess, "run", run)


def test_main_with_no_target_prints_the_usage_line_on_stderr_and_exits_2(run_cli, dispatch, monkeypatch, tmp_path):
    (tmp_path / ".tdd").mkdir()
    launches = []
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "launch", launches.append)
    code, out, err = run_cli(dispatch, [])
    assert (code, out, launches) == (2, "", [])
    assert str(tmp_path / ".tdd" / "role-dev.state") in err


def test_main_with_no_target_and_an_unreadable_role_dev_state_exits_2_naming_the_file_and_launches_nothing(
        run_cli, dispatch, monkeypatch, tmp_path):
    (tmp_path / ".tdd" / "role-dev.state").mkdir(parents=True)
    launches = []
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "launch", launches.append)
    code, out, err = run_cli(dispatch, [])
    assert (code, out, launches) == (2, "", [])
    assert str(tmp_path / ".tdd" / "role-dev.state") in err


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
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12", "15"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "2"])
    except _StopWaiting:
        code = None

    assert (launches, waits, code, capsys.readouterr().out) == (["12"], [1], None, "")


def test_main_with_no_target_applies_the_n_a_wait_changed_in_role_dev_state_at_the_second_slot_decision(
        monkeypatch, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    state = tmp_path / ".tdd" / "role-dev.state"
    state.write_text("n=1\n")
    launches = []
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 2:
            raise _StopWaiting
        state.write_text("n=1\nn=2\n")

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        dispatch.main([])
    except _StopWaiting:
        pass

    assert (launches, waits) == (["12"], [1, 1])


def test_main_with_no_target_applies_the_n_of_a_role_dev_state_timed_n_change_whose_expiry_has_not_passed(
        monkeypatch, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text(
        "n=1\ntimed-n dev-1 2026-11-07T10:00:00 2 until 2026-11-07T11:00:00\n")
    launches = []

    def wait():
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: datetime(2026, 11, 7, 10, 30).timestamp())
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        dispatch.main([])
    except _StopWaiting:
        pass

    assert launches == ["12"]


def test_main_with_no_target_keeps_the_n_line_in_force_once_a_role_dev_state_timed_n_change_has_expired(
        monkeypatch, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text(
        "n=1\ntimed-n dev-1 2026-11-07T10:00:00 2 until 2026-11-07T11:00:00\n")

    def decide(at):
        launches = []

        def wait():
            raise _StopWaiting

        monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
        monkeypatch.setattr(dispatch, "clock", lambda: at.timestamp())
        monkeypatch.setattr(dispatch, "now", lambda: at.isoformat(), raising=False)
        monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
        monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
        monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
        monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
        monkeypatch.setattr(dispatch, "wait", wait, raising=False)
        try:
            dispatch.main([])
        except _StopWaiting:
            pass
        return launches

    assert (decide(datetime(2026, 11, 7, 10, 30)), decide(datetime(2026, 11, 7, 11, 30))) == (["12"], [])


def test_main_with_no_target_does_not_apply_an_expired_role_dev_state_timed_n_change_lowering_the_n_line(
        monkeypatch, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text(
        "n=2\ntimed-n dev-1 2026-11-07T10:00:00 1 until 2026-11-07T11:00:00\n")
    launches = []

    def wait():
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: datetime(2026, 11, 7, 11, 30).timestamp())
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T11:30:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        dispatch.main([])
    except _StopWaiting:
        pass

    assert launches == ["12"]


def test_main_with_no_target_launches_the_issue_a_role_dev_state_override_names_before_the_first_solvable_issue(
        monkeypatch, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text("n=1\noverride dev-1 2026-11-07T10:00:00 take #15 first\n")
    launches = []

    def wait():
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12", "15"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        dispatch.main([])
    except _StopWaiting:
        pass

    assert launches == ["15"]


def test_main_with_no_target_ignores_a_role_dev_state_override_naming_an_issue_not_among_the_solvable_ones_and_launches_the_next_override_issue(
        monkeypatch, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text(
        "n=1\n"
        "override dev-1 2026-11-07T10:00:00 take #99 first\n"
        "override dev-2 2026-11-07T10:01:00 take #15 first\n")
    launches = []

    def wait():
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12", "15"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        dispatch.main([])
    except _StopWaiting:
        pass

    assert launches == ["15"]


def test_main_without_a_queued_merges_fake_fails_naming_the_unfaked_call_issue_3435(
        monkeypatch, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "wait", lambda: (_ for _ in ()).throw(_StopWaiting), raising=False)

    with pytest.raises(AssertionError, match="unfaked queued_merges call"):
        dispatch.main(["--target", "1"])


def test_main_with_a_queued_merges_fake_runs_under_the_guard_and_reaches_the_faked_wait_issue_3435(
        monkeypatch, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    waits = []

    def wait():
        waits.append(1)
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    assert waits == [1]


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

    assert (calls[:1], log.read_bytes()) == (
        [([os.path.join(scripts, "detach-leaf.sh"), os.path.join(scripts, "run-conductor.sh"), "12"],
          subprocess.DEVNULL, True)],
        b"earlier\nconductor output\n")


def test_launch_also_starts_restart_conductor_through_detach_leaf_appending_to_restart_log_with_stdin_from_dev_null_issue_3344(
        monkeypatch, tmp_path, dispatch):
    import os
    import subprocess
    scripts = os.path.dirname(os.path.dirname(os.path.abspath(dispatch.__file__)))
    (tmp_path / ".tdd").mkdir()
    log = tmp_path / ".tdd" / "restart-12.log"
    log.write_bytes(b"earlier\n")
    calls = []

    def popen(argv, stdin=None, stdout=None, stderr=None, **kw):
        calls.append((list(argv), stdin, stdout, stderr))
        if stdout is not None and getattr(stdout, "name", None) == str(log):
            stdout.write(b"watcher output\n")
            stdout.flush()

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch.subprocess, "Popen", popen)

    dispatch.launch("12")

    want = [os.path.join(scripts, "detach-leaf.sh"), os.path.join(scripts, "restart-conductor.sh"), "12"]
    restarts = [c for c in calls if c[0] == want]
    assert ([(c[1], c[2] is c[3]) for c in restarts], log.read_bytes()) == (
        [(subprocess.DEVNULL, True)], b"earlier\nwatcher output\n")


def test_launch_raises_and_starts_no_restart_conductor_when_the_run_conductor_launch_fails_issue_3344(
        monkeypatch, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    scripts_called = []

    def popen(argv, **kw):
        scripts_called.append(argv[1].rsplit("/", 1)[-1])
        raise OSError("exec failed")

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch.subprocess, "Popen", popen)

    with pytest.raises(OSError):
        dispatch.launch("12")

    assert scripts_called == ["run-conductor.sh"]


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
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
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
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
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
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: [i for i in ["12", "15"] if i not in launched], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: launched.append(issue) or (tmp_path / ".tdd" / "wt" / issue / ".tdd").mkdir(parents=True)
                        or (tmp_path / ".tdd" / "wt" / issue / ".tdd" / f"issue-{issue}.md").write_text("x"),
                        raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "2"])

    assert (tmp_path / ".tdd" / "dispatch.log").read_text() == (
        "launched 12 2026-11-07T10:30:00\nlaunched 15 2026-11-07T10:30:00\n")


def test_main_prints_done_with_the_pr_url_from_the_last_comment_heading_and_exits_0_when_a_live_conductor_exits(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd" / "wt" / "7").mkdir(parents=True)
    lives = [["7"], []]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 2:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment",
                        lambda issue: "### ✅ Done — https://github.com/o/r/pull/9\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out) == (0, "done 7 https://github.com/o/r/pull/9\n")


def test_main_prints_bail_and_exits_0_when_a_live_conductor_exits_and_its_last_comment_is_a_bail(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd" / "wt" / "7").mkdir(parents=True)
    lives = [["7"], []]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 2:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment", lambda issue: "### ⛔ Bailed\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out) == (0, "bail 7\n")


def test_main_prints_silent_exit_and_exits_0_when_a_live_conductor_exits_and_its_last_comment_is_neither_done_nor_bailed(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd" / "wt" / "7").mkdir(parents=True)
    lives = [["7"], []]
    waits = []

    elapsed = [1000]

    def wait():
        waits.append(1)
        elapsed[0] += 31
        if len(waits) > 6:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: elapsed[0], raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment", lambda issue: "### 🔧 Working on it\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out) == (0, "silent-exit 7\n")


def test_main_prints_no_exit_line_and_keeps_looping_when_a_seen_run_with_a_worktree_is_absent_for_one_pass_then_live_again_issue_3516(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd" / "wt" / "7").mkdir(parents=True)
    lives = [["7"], [], ["7"]]
    waits = []
    elapsed = [1000]

    def wait():
        waits.append(1)
        elapsed[0] += 31
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: elapsed[0], raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment", lambda issue: "### 🔧 Working on it\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = "looping"

    assert (code, capsys.readouterr().out) == ("looping", "")


def test_main_prints_no_exit_line_when_a_seen_run_is_absent_for_several_passes_spanning_under_30_seconds_then_live_again_issue_3516(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd" / "wt" / "7").mkdir(parents=True)
    lives = [["7"], [], [], [], [], ["7"]]
    waits = []
    elapsed = [1000]

    def wait():
        waits.append(1)
        elapsed[0] += 5
        if len(waits) == 7:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: elapsed[0], raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment", lambda issue: "### 🔧 Working on it\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = "looping"

    assert (code, capsys.readouterr().out) == ("looping", "")


def test_main_prints_no_exit_line_on_the_first_pass_of_a_new_absence_when_the_run_came_back_live_after_an_earlier_absence_over_30_seconds_old_issue_3516(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd" / "wt" / "7").mkdir(parents=True)
    lives = [["7"], [], ["7"], []]
    waits = []
    elapsed = [1000]

    def wait():
        waits.append(1)
        elapsed[0] += 31
        if len(waits) == 4:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: elapsed[0], raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment", lambda issue: "### 🔧 Working on it\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = "looping"

    assert (code, capsys.readouterr().out) == ("looping", "")


def test_main_prints_no_exit_line_and_keeps_looping_when_an_absent_run_has_a_restart_pending_marker_in_its_worktree_issue_3370(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd" / "wt" / "7" / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending").write_text("")
    lives = [["7"], []]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 2:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment", lambda issue: "### 🔧 Working on it\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = "looping"

    assert (code, capsys.readouterr().out) == ("looping", "")


def test_main_launches_nothing_on_any_tick_across_a_restart_of_one_of_two_slot_holding_runs_at_target_2_issue_3495(
        monkeypatch, tmp_path, dispatch):
    import os
    marker = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending"
    marker.parent.mkdir(parents=True)
    marker.write_text(f"{os.getpid()}\n")
    lives = [["5", "7"], ["5"], ["5", "7"]]
    launches = []
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives[len(waits)], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "2"])

    assert launches == []


def test_main_launches_nothing_on_the_tick_where_a_run_seen_live_is_restarting_beside_one_live_run_at_target_2_issue_3495(
        monkeypatch, tmp_path, dispatch):
    import os
    marker = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending"
    marker.parent.mkdir(parents=True)
    marker.write_text(f"{os.getpid()}\n")
    lives = [["5", "7"], ["5"]]
    launches = []
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 2:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives[len(waits)], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "2"])

    assert launches == []


def test_main_launches_exactly_one_at_target_3_beside_a_live_run_with_a_leftover_marker_and_a_never_seen_restarting_run_issue_3495(
        monkeypatch, capsys, tmp_path, dispatch):
    import os
    for issue in ("7", "9"):
        marker = tmp_path / ".tdd" / "wt" / issue / ".tdd" / "restart-pending"
        marker.parent.mkdir(parents=True)
        marker.write_text(f"{os.getpid()}\n")
    launches = []
    waits = []

    def launch(issue):
        launches.append(issue)
        ledger = tmp_path / ".tdd" / "wt" / issue / ".tdd" / f"issue-{issue}.md"
        ledger.parent.mkdir(parents=True)
        ledger.write_text("- [ ] step\n")

    def wait():
        waits.append(1)
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["7"] + launches, raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues",
                        lambda: [i for i in ["12", "15"] if i not in launches], raising=False)
    monkeypatch.setattr(dispatch, "launch", launch, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "3"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out, launches) == (None, "", ["12"])


def test_main_prints_silent_exit_when_an_absent_run_has_a_restart_pending_marker_naming_a_dead_restarter_issue_3370(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd" / "wt" / "7" / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending").write_text("4242\n")
    lives = [["7"], []]

    def dead(pid, sig):
        raise ProcessLookupError(pid)

    monkeypatch.setattr(dispatch.os, "kill", dead)
    monkeypatch.setattr(dispatch, "clock", lambda: elapsed[0], raising=False)
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment", lambda issue: "### 🔧 Working on it\n\nbody", raising=False)
    waits = []
    elapsed = [1000]

    def wait():
        waits.append(1)
        elapsed[0] += 31
        if len(waits) > 8:
            raise _StopWaiting

    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = "looping"

    assert (code, capsys.readouterr().out) == (0, "silent-exit 7\n")


def test_main_reports_a_deferred_run_once_its_restart_marker_goes_stale_after_several_deferral_passes_issue_3370(
        monkeypatch, capsys, tmp_path, dispatch):
    marker = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending"
    marker.parent.mkdir(parents=True)
    marker.write_text("")
    lives = [["7"], []]
    waits = []
    elapsed = [1000]

    def wait():
        waits.append(1)
        elapsed[0] += 31
        if len(waits) == 3:
            marker.write_text("4242\n")
        if len(waits) > 12:
            raise _StopWaiting

    def kill(pid, sig):
        raise ProcessLookupError(pid)

    monkeypatch.setattr(dispatch.os, "kill", kill)
    monkeypatch.setattr(dispatch, "clock", lambda: elapsed[0], raising=False)
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment", lambda issue: "### 🔧 Working on it\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = "looping"

    assert (code, capsys.readouterr().out) == (0, "silent-exit 7\n")


@pytest.mark.parametrize("content", ["", "4242\n"])
def test_main_prints_stalled_for_a_deferred_run_whose_restart_marker_never_clears_once_the_stall_window_passes_issue_3370(
        monkeypatch, capsys, tmp_path, dispatch, content):
    import os
    tdd = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    tdd.mkdir(parents=True)
    (tdd / "restart-pending").write_text(content)
    events = tdd / "events.jsonl"
    events.write_text('{"event": "leaf-start"}\n')
    os.utime(events, (1000, 1000))
    lives = [["7"], []]
    ticks = [1000, 1000, 1000, 1003]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) > 8:
            raise _StopWaiting

    monkeypatch.setenv("VERI_DISPATCH_STALL", "2")
    monkeypatch.setattr(dispatch.os, "kill", lambda pid, sig: None)
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: ticks.pop(0) if len(ticks) > 1 else ticks[0], raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment", lambda issue: "### 🔧 Working on it\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = "looping"

    assert (code, capsys.readouterr().out) == (0, "stalled 7\n")


def test_main_prints_silent_exit_and_exits_0_when_a_live_conductor_exits_and_its_issue_has_no_comments_issue_3418(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd" / "wt" / "7").mkdir(parents=True)
    lives = [["7"], []]
    waits = []

    elapsed = [1000]

    def wait():
        waits.append(1)
        elapsed[0] += 31
        if len(waits) > 6:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: elapsed[0], raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch.github, "gh_rest_list", lambda path, *a, **kw: "[]", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None
    except IndexError:
        code = "IndexError"

    assert (code, capsys.readouterr().out) == (0, "silent-exit 7\n")


def test_main_exits_2_naming_the_vanished_run_and_prints_no_closing_line_when_a_live_conductor_exits_leaving_no_worktree(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    lives = [["7"], [], []]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment",
                        lambda issue: "### ✅ Done — https://github.com/o/r/pull/9\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (2, "", "run 7 vanished: no worktree left behind\n")


def test_main_does_not_exit_or_report_vanished_and_keeps_looping_when_a_run_with_no_worktree_is_absent_for_one_pass_then_live_again_issue_3345(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    lives = [["7"], [], ["7"]]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment",
                        lambda issue: "### ✅ Done — https://github.com/o/r/pull/9\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = "looping"

    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == ("looping", "", "")


def test_main_does_not_exit_or_report_vanished_when_a_run_with_no_worktree_is_absent_once_live_again_then_absent_once_more_issue_3345(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    lives = [["7"], [], ["7"], []]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 4:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment",
                        lambda issue: "### ✅ Done — https://github.com/o/r/pull/9\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = "looping"

    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == ("looping", "", "")


def test_main_prints_merge_failed_with_the_pr_url_and_exits_0_when_a_running_queued_merge_ends_with_the_pr_not_merged(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    url = "https://github.com/o/r/pull/9"
    listings = [[url], []]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 2:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges",
                        lambda: listings.pop(0) if len(listings) > 1 else listings[0], raising=False)
    monkeypatch.setattr(dispatch, "pr_state", lambda pr_url: "CLOSED", raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out) == (0, f"merge-failed {url}\n")


def test_main_prints_nothing_while_a_queued_merge_is_still_listed_on_the_next_pass_even_though_the_pr_is_not_merged(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    url = "https://github.com/o/r/pull/9"
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 2:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [url], raising=False)
    monkeypatch.setattr(dispatch, "pr_state", lambda pr_url: "CLOSED", raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    assert capsys.readouterr().out == ""


def test_main_prints_nothing_and_takes_the_slot_decision_again_when_a_running_queued_merge_ends_with_the_pr_merged(
        monkeypatch, capsys, tmp_path, dispatch):
    url = "https://github.com/o/r/pull/9"
    ledger = tmp_path / ".tdd" / "wt" / "12" / ".tdd" / "issue-12.md"
    ledger.parent.mkdir(parents=True)
    listings = [[url], []]
    launches = []
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 1:
            ledger.write_text("- [ ] step\n")
        if len(waits) == 2:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges",
                        lambda: listings.pop(0) if len(listings) > 1 else listings[0], raising=False)
    monkeypatch.setattr(dispatch, "pr_state", lambda pr_url: "MERGED", raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues",
                        lambda: [i for i in ["12", "15"] if i not in launches], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "2"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out, launches, waits) == (None, "", ["12", "15"], [1, 1])


def test_main_prints_stalled_and_exits_0_when_a_live_conductors_event_log_records_no_new_event_for_the_stall_window(
        monkeypatch, capsys, tmp_path, dispatch):
    import os
    events = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl"
    events.parent.mkdir(parents=True)
    events.write_text('{"event": "leaf-start"}\n')
    os.utime(events, (1000, 1000))
    ticks = [1000, 1003]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setenv("VERI_DISPATCH_STALL", "2")
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: ticks.pop(0) if len(ticks) > 1 else ticks[0], raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["7"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out) == (0, "stalled 7\n")


def test_main_with_the_stall_window_unset_reports_a_conductor_silent_for_3600_seconds_but_not_one_silent_for_3599(
        monkeypatch, capsys, tmp_path, dispatch):
    import os
    events = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl"
    events.parent.mkdir(parents=True)
    events.write_text('{"event": "leaf-start"}\n')
    os.utime(events, (1000, 1000))
    ticks = [1000 + 3599, 1000 + 3600]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 4:
            raise _StopWaiting

    monkeypatch.delenv("VERI_DISPATCH_STALL", raising=False)
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: ticks.pop(0) if len(ticks) > 1 else ticks[0], raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["7"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out, len(waits)) == (0, "stalled 7\n", 2)


def test_main_with_a_non_integer_stall_window_prints_the_usage_on_stderr_and_exits_2_before_any_launch(
        monkeypatch, tmp_path, run_cli, dispatch):
    (tmp_path / ".tdd").mkdir()
    launches = []

    monkeypatch.setenv("VERI_DISPATCH_STALL", "abc")
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", lambda: (_ for _ in ()).throw(_StopWaiting), raising=False)

    code, out, err = run_cli(dispatch, ["--target", "1"])

    assert (code, out, err, launches) == (2, "", "usage: dispatch.sh [--target <N>]  (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing; with no --target, N and the launch order come from .tdd/role-dev.state in the main working tree: its last n= line, overridden by an unexpired timed-n line, and each override line pulls the issue it names to the front; exit 2 if that file is unreadable, has no n= line, or has a malformed n=, timed-n or override line)\n", [])


def test_main_prints_queue_empty_and_exits_3_when_solvable_issues_exits_3_and_no_conductor_is_live(
        monkeypatch, capsys, tmp_path, dispatch):
    import subprocess
    (tmp_path / ".tdd").mkdir()
    launches = []

    def wait():
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch.watch_runs.subprocess, "run",
                        lambda argv, **kw: subprocess.CompletedProcess(argv, 3, stdout="", stderr=""))
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out, launches) == (3, "queue-empty\n", [])


def test_main_prints_nothing_and_keeps_waiting_when_solvable_issues_exits_3_while_a_conductor_is_live(
        monkeypatch, capsys, tmp_path, dispatch):
    import subprocess
    (tmp_path / ".tdd").mkdir()
    launches = []
    waits = []

    def wait():
        waits.append(1)
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch.watch_runs.subprocess, "run",
                        lambda argv, **kw: subprocess.CompletedProcess(argv, 3, stdout="", stderr=""))
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "2"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out, launches, waits) == (None, "", [], [1])


def test_main_writes_the_stderr_of_an_unreadable_queue_and_exits_2_when_solvable_issues_fails_without_a_rate_limit(
        monkeypatch, tmp_path, run_cli, dispatch):
    import subprocess
    (tmp_path / ".tdd").mkdir()
    launches = []

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch.watch_runs.subprocess, "run",
                        lambda argv, **kw: subprocess.CompletedProcess(argv, 1, stdout="", stderr="gh: boom\n"))
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", lambda: (_ for _ in ()).throw(_StopWaiting), raising=False)

    code, out, err = run_cli(dispatch, ["--target", "1"])

    assert (code, out, err, launches) == (2, "", "gh: boom\n", [])


def test_main_with_a_rate_limited_queue_read_waits_for_the_reported_reset_making_no_queue_read_meanwhile_then_reads_again(
        monkeypatch, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    now = [1000]
    reset = 1025
    reads = []
    launches = []

    def solvable():
        reads.append(now[0])
        if now[0] < reset:
            raise dispatch.watch_runs.QueueUnreadable("gh: API rate limit exceeded for user ID 1 (HTTP 403)\n")
        return ["12"]

    def wait():
        if launches:
            raise _StopWaiting
        now[0] += 10

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
    monkeypatch.setattr(dispatch, "clock", lambda: now[0])
    monkeypatch.setattr(dispatch.watch_runs.time, "time", lambda: now[0])
    monkeypatch.setattr(dispatch.watch_runs.github, "rate_limit_reset", lambda run: reset)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", solvable, raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "2"])
    except _StopWaiting:
        code = None

    assert (reads, launches, code) == ([1000, 1030], ["12"], None)


def test_main_with_a_zero_or_non_integer_target_prints_the_usage_on_stderr_and_exits_2_launching_nothing(
        monkeypatch, tmp_path, run_cli, dispatch):
    (tmp_path / ".tdd").mkdir()
    launches = []

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", lambda: (_ for _ in ()).throw(_StopWaiting), raising=False)

    results = [run_cli(dispatch, argv) for argv in (["--target", "abc"], ["--target"])]

    usage = (2, "", "usage: dispatch.sh [--target <N>]  (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing; with no --target, N and the launch order come from .tdd/role-dev.state in the main working tree: its last n= line, overridden by an unexpired timed-n line, and each override line pulls the issue it names to the front; exit 2 if that file is unreadable, has no n= line, or has a malformed n=, timed-n or override line)\n")
    assert (results, launches) == ([usage, usage], [])


def test_main_with_a_negative_or_non_integer_target_prints_the_usage_on_stderr_and_exits_2_launching_nothing_issue_3520(
        monkeypatch, tmp_path, run_cli, dispatch):
    (tmp_path / ".tdd").mkdir()
    launches = []

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", lambda: (_ for _ in ()).throw(_StopWaiting), raising=False)

    results = [run_cli(dispatch, ["--target", value]) for value in ("-1", "abc", "1.5")]

    usage = (2, "", "usage: dispatch.sh [--target <N>]  (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing; with no --target, N and the launch order come from .tdd/role-dev.state in the main working tree: its last n= line, overridden by an unexpired timed-n line, and each override line pulls the issue it names to the front; exit 2 if that file is unreadable, has no n= line, or has a malformed n=, timed-n or override line)\n")
    assert (results, launches) == ([usage, usage, usage], [])


def test_main_with_target_0_is_accepted_and_launches_nothing_appending_no_launched_line_with_issues_queued_issue_3520(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd").mkdir()
    launches = []
    waits = []

    def wait():
        waits.append(1)
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12", "15"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "0"])
    except _StopWaiting:
        code = None

    captured = capsys.readouterr()
    assert (code, captured.err, launches, (tmp_path / ".tdd" / "dispatch.log").exists()) == (None, "", [], False)


def test_main_with_target_0_an_empty_queue_and_no_live_run_prints_no_queue_empty_and_keeps_waiting_issue_3520(
        monkeypatch, capsys, tmp_path, dispatch):
    import subprocess
    (tmp_path / ".tdd").mkdir()
    launches = []
    waits = []

    def wait():
        waits.append(1)
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch.watch_runs.subprocess, "run",
                        lambda argv, **kw: subprocess.CompletedProcess(argv, 3, stdout="", stderr=""))
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "0"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out, launches, waits) == (None, "", [], [1])


def test_main_with_target_0_and_a_live_run_that_exits_prints_its_done_line_and_exits_0_launching_nothing_issue_3520(
        monkeypatch, capsys, tmp_path, dispatch):
    (tmp_path / ".tdd" / "wt" / "7").mkdir(parents=True)

    def run(target):
        lives = [[], ["7"], []]
        launches = []

        monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
        monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
        monkeypatch.setattr(dispatch, "live_conductors",
                            lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
        monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
        monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
        monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
        monkeypatch.setattr(dispatch, "last_comment",
                            lambda issue: "### ✅ Done — https://github.com/o/r/pull/9\n\nbody", raising=False)
        monkeypatch.setattr(dispatch, "wait", lambda: None, raising=False)

        code = dispatch.main(["--target", target])
        return code, capsys.readouterr().out, launches

    done = "done 7 https://github.com/o/r/pull/9\n"
    assert (run("0"), run("1")) == ((0, done, []), (0, done, ["12"]))


def test_main_with_an_unknown_flag_prints_the_usage_on_stderr_and_exits_2_launching_nothing(
        monkeypatch, tmp_path, run_cli, dispatch):
    (tmp_path / ".tdd").mkdir()
    launches = []

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", lambda: (_ for _ in ()).throw(_StopWaiting), raising=False)

    code, out, err = run_cli(dispatch, ["--target", "1", "--frobnicate"])

    assert (code, out, err, launches) == (2, "", "usage: dispatch.sh [--target <N>]  (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing; with no --target, N and the launch order come from .tdd/role-dev.state in the main working tree: its last n= line, overridden by an unexpired timed-n line, and each override line pulls the issue it names to the front; exit 2 if that file is unreadable, has no n= line, or has a malformed n=, timed-n or override line)\n", [])


def test_main_with_an_unknown_flag_in_the_first_position_prints_the_usage_on_stderr_and_exits_2_launching_nothing(
        monkeypatch, tmp_path, run_cli, dispatch):
    (tmp_path / ".tdd").mkdir()
    launches = []

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", lambda: (_ for _ in ()).throw(_StopWaiting), raising=False)

    code, out, err = run_cli(dispatch, ["--frobnicate", "5"])

    assert (code, out, err, launches) == (2, "", "usage: dispatch.sh [--target <N>]  (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing; with no --target, N and the launch order come from .tdd/role-dev.state in the main working tree: its last n= line, overridden by an unexpired timed-n line, and each override line pulls the issue it names to the front; exit 2 if that file is unreadable, has no n= line, or has a malformed n=, timed-n or override line)\n", [])


def test_main_with_help_prints_the_usage_on_stdout_and_exits_0_launching_nothing_and_reading_no_queue(
        monkeypatch, tmp_path, run_cli, dispatch):
    (tmp_path / ".tdd").mkdir()
    launches = []
    reads = []

    def solvable():
        reads.append(1)
        return ["12"]

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", solvable, raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", lambda: (_ for _ in ()).throw(_StopWaiting), raising=False)

    code, out, err = run_cli(dispatch, ["--help"])

    assert (code, out, err, launches, reads) == (0, "usage: dispatch.sh [--target <N>]  (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing; with no --target, N and the launch order come from .tdd/role-dev.state in the main working tree: its last n= line, overridden by an unexpired timed-n line, and each override line pulls the issue it names to the front; exit 2 if that file is unreadable, has no n= line, or has a malformed n=, timed-n or override line)\n", "", [], [])


def test_main_with_help_writes_exactly_one_usage_line_to_the_stdout_descriptor_and_nothing_to_stderr(
        run_cli, dispatch):
    code, out, err = run_cli(dispatch, ["--help"])

    assert (code, out, err) == (0, "usage: dispatch.sh [--target <N>]  (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing; with no --target, N and the launch order come from .tdd/role-dev.state in the main working tree: its last n= line, overridden by an unexpired timed-n line, and each override line pulls the issue it names to the front; exit 2 if that file is unreadable, has no n= line, or has a malformed n=, timed-n or override line)\n", "")


def test_last_comment_returns_the_body_of_the_issues_last_comment_read_through_the_github_port_without_starting_a_gh_process(
        monkeypatch, dispatch):
    import json

    paths = []

    def gh_rest_list(path, *args):
        paths.append(path)
        return json.dumps([{"body": "### 🔧 first"}, {"body": "### ✅ Done https://x/pull/9"}])

    def no_process(*args, **kw):
        raise AssertionError("dispatch started a process of its own: %r" % (args,))

    monkeypatch.setattr(dispatch.github, "gh_rest_list", gh_rest_list, raising=False)
    monkeypatch.setattr(dispatch.subprocess, "run", no_process)

    assert dispatch.last_comment("12").strip() == "### ✅ Done https://x/pull/9"
    assert paths == ["repos/{owner}/{repo}/issues/12/comments?per_page=100"]


def test_pr_state_reads_a_merged_pull_request_as_merged_and_last_comment_ignores_a_trailing_empty_page(
        monkeypatch, dispatch):
    import json
    import types

    monkeypatch.setattr(
        dispatch.github, "gh_api",
        lambda path, *a, **kw: types.SimpleNamespace(stdout=json.dumps({"merged": True, "state": "closed"})),
        raising=False)
    monkeypatch.setattr(
        dispatch.github, "gh_rest_list",
        lambda path, *a, **kw: json.dumps([{"body": "first"}, {"body": "last"}]) + json.dumps([]),
        raising=False)

    assert (dispatch.pr_state("https://github.com/o/r/pull/7"), dispatch.last_comment("12")) == ("MERGED", "last")


def test_main_does_not_raise_or_exit_2_and_keeps_looping_when_a_vanished_queued_merge_url_answers_a_404_body_with_no_merged_key_issue_3356(
        monkeypatch, capsys, tmp_path, dispatch):
    import json
    import types

    (tmp_path / ".tdd").mkdir()
    url = "https://github.com/o/r/pull/9"
    listings = [[url], []]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges",
                        lambda: listings.pop(0) if len(listings) > 1 else listings[0], raising=False)
    monkeypatch.setattr(
        dispatch.github, "gh_api",
        lambda path, *a, **kw: types.SimpleNamespace(stdout=json.dumps({"message": "Not Found"})),
        raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    captured = capsys.readouterr()
    lines = (captured.out + captured.err).splitlines()
    assert (len(waits), len(lines) <= 1, all(url in line for line in lines)) == (3, True, True)


def test_main_prints_nothing_and_keeps_looping_when_a_vanished_queued_merge_url_answers_a_200_body_merged_true_through_gh_api_issue_3356(
        monkeypatch, capsys, tmp_path, dispatch):
    import json
    import types

    (tmp_path / ".tdd").mkdir()
    url = "https://github.com/o/r/pull/9"
    listings = [[url], []]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges",
                        lambda: listings.pop(0) if len(listings) > 1 else listings[0], raising=False)
    monkeypatch.setattr(
        dispatch.github, "gh_api",
        lambda path, *a, **kw: types.SimpleNamespace(stdout=json.dumps({"merged": True, "state": "closed"})),
        raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    captured = capsys.readouterr()
    assert (captured.out, captured.err, len(waits)) == ("", "", 3)


def test_main_prints_merge_failed_and_exits_0_when_a_vanished_queued_merge_url_answers_a_200_body_closed_not_merged_through_gh_api_issue_3356(
        monkeypatch, capsys, tmp_path, dispatch):
    import json
    import types

    (tmp_path / ".tdd").mkdir()
    url = "https://github.com/o/r/pull/9"
    listings = [[url], []]
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges",
                        lambda: listings.pop(0) if len(listings) > 1 else listings[0], raising=False)
    monkeypatch.setattr(
        dispatch.github, "gh_api",
        lambda path, *a, **kw: types.SimpleNamespace(stdout=json.dumps({"merged": False, "state": "closed"})),
        raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out) == (0, f"merge-failed {url}\n")


def test_queued_merges_still_returns_the_pr_url_of_a_queued_merge_sh_launched_from_this_clones_scripts_issue_3364(
        monkeypatch, dispatch):
    import subprocess

    url = "https://github.com/o/r/pull/7"
    mine = dispatch.paths.scripts_of(dispatch.__file__)
    listing = f"sh {mine}/queued-merge.sh {url}\n"

    def ps(argv, **kw):
        return subprocess.CompletedProcess(argv, 0, stdout=listing, stderr="")

    monkeypatch.setattr(dispatch.subprocess, "run", ps)

    assert dispatch.queued_merges() == [url]


def test_queued_merges_omits_a_queued_merge_sh_whose_script_path_is_outside_this_clone_issue_3364(
        monkeypatch, dispatch):
    import subprocess

    listing = "sh /private/tmp/x/queued-merge.sh https://github.com/o/r/pull/7\n"

    def ps(argv, **kw):
        return subprocess.CompletedProcess(argv, 0, stdout=listing, stderr="")

    monkeypatch.setattr(dispatch.subprocess, "run", ps)

    assert dispatch.queued_merges() == []


def test_queued_merges_returns_the_pr_url_of_a_queued_merge_sh_reached_through_a_symlink_to_this_clones_scripts_issue_3364(
        monkeypatch, dispatch, tmp_path):
    import os
    import subprocess

    url = "https://github.com/o/r/pull/7"
    link = tmp_path / "skills-link"
    os.symlink(dispatch.paths.scripts_of(dispatch.__file__), link)
    listing = f"sh {link}/queued-merge.sh {url}\n"

    def ps(argv, **kw):
        return subprocess.CompletedProcess(argv, 0, stdout=listing, stderr="")

    monkeypatch.setattr(dispatch.subprocess, "run", ps)

    assert dispatch.queued_merges() == [url]


def test_queued_merges_returns_the_pr_url_of_a_python_process_running_this_clones_queued_merge_py_issue_3403(
        monkeypatch, dispatch):
    import subprocess

    url = "https://github.com/o/r/pull/7"
    mine = dispatch.paths.scripts_of(dispatch.__file__)
    listing = f"/usr/bin/python3 {mine}/veri/queued_merge.py {url} /wt branch -\n"

    def ps(argv, **kw):
        return subprocess.CompletedProcess(argv, 0, stdout=listing, stderr="")

    monkeypatch.setattr(dispatch.subprocess, "run", ps)

    assert dispatch.queued_merges() == [url]


def test_queued_merges_still_returns_a_pre_exec_queued_merge_sh_beside_a_post_exec_queued_merge_py_issue_3403(
        monkeypatch, dispatch):
    import subprocess

    pre = "https://github.com/o/r/pull/7"
    post = "https://github.com/o/r/pull/8"
    mine = dispatch.paths.scripts_of(dispatch.__file__)
    listing = (f"sh {mine}/queued-merge.sh {pre} /wt branch -\n"
               f"/usr/bin/python3 {mine}/veri/queued_merge.py {post} /wt2 branch -\n")

    def ps(argv, **kw):
        return subprocess.CompletedProcess(argv, 0, stdout=listing, stderr="")

    monkeypatch.setattr(dispatch.subprocess, "run", ps)

    assert dispatch.queued_merges() == [pre, post]


def test_queued_merges_ignores_an_editor_or_grep_naming_queued_merge_py_as_a_later_argument_issue_3403(
        monkeypatch, dispatch):
    import subprocess

    mine = dispatch.paths.scripts_of(dispatch.__file__)
    listing = (f"vim {mine}/veri/queued_merge.py https://github.com/o/r/pull/7\n"
               f"grep -n {mine}/veri/queued_merge.py https://github.com/o/r/pull/8\n")

    def ps(argv, **kw):
        return subprocess.CompletedProcess(argv, 0, stdout=listing, stderr="")

    monkeypatch.setattr(dispatch.subprocess, "run", ps)

    assert dispatch.queued_merges() == []


def test_queued_merges_ignores_a_python_process_running_queued_merge_py_from_another_clones_path_beside_this_clones_issue_3403(
        monkeypatch, dispatch):
    import subprocess

    mine_url = "https://github.com/o/r/pull/7"
    foreign_url = "https://github.com/o/r/pull/8"
    mine = dispatch.paths.scripts_of(dispatch.__file__)
    listing = (f"/usr/bin/python3 {mine}/veri/queued_merge.py {mine_url} /wt branch -\n"
               f"/usr/bin/python3 /private/tmp/x/veri/queued_merge.py {foreign_url} /wt2 branch -\n")

    def ps(argv, **kw):
        return subprocess.CompletedProcess(argv, 0, stdout=listing, stderr="")

    monkeypatch.setattr(dispatch.subprocess, "run", ps)

    assert dispatch.queued_merges() == [mine_url]


def test_main_does_not_report_stalled_when_events_are_older_than_the_stall_window_but_the_conductor_log_is_newer_issue_3360(
        monkeypatch, capsys, tmp_path, dispatch):
    import os
    tdd = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    tdd.mkdir(parents=True)
    events = tdd / "events.jsonl"
    events.write_text('{"event": "leaf-start"}\n')
    os.utime(events, (1000, 1000))
    log = tdd / "conductor-7.log"
    log.write_text("working\n")
    os.utime(log, (1002, 1002))
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setenv("VERI_DISPATCH_STALL", "2")
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: 1003, raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["7"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out) == (None, "")


def test_main_does_not_report_stalled_when_events_are_older_than_the_stall_window_but_a_detached_command_output_is_newer_issue_3360(
        monkeypatch, capsys, tmp_path, dispatch):
    import os
    tdd = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    tdd.mkdir(parents=True)
    events = tdd / "events.jsonl"
    events.write_text('{"event": "leaf-start"}\n')
    os.utime(events, (1000, 1000))
    out = tdd / "tip-full.out"
    out.write_text("running suite\n")
    os.utime(out, (1002, 1002))
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setenv("VERI_DISPATCH_STALL", "2")
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: 1003, raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["7"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out) == (None, "")


def test_main_prints_stalled_and_exits_0_when_the_events_conductor_log_and_detached_command_output_are_all_older_than_the_stall_window_issue_3360(
        monkeypatch, capsys, tmp_path, dispatch):
    import os
    tdd = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    tdd.mkdir(parents=True)
    for name in ("events.jsonl", "conductor-7.log", "tip-full.out"):
        (tdd / name).write_text("x\n")
        os.utime(tdd / name, (1000, 1000))
    waits = []

    def wait():
        waits.append(1)
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setenv("VERI_DISPATCH_STALL", "2")
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "clock", lambda: 1003, raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["7"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out) == (0, "stalled 7\n")


def test_main_launches_exactly_one_at_target_4_once_a_restarted_run_is_live_again_beside_a_live_run_and_a_never_seen_restarting_run_issue_3495(
        monkeypatch, capsys, tmp_path, dispatch):
    import os
    marker = tmp_path / ".tdd" / "wt" / "9" / ".tdd" / "restart-pending"
    marker.parent.mkdir(parents=True)
    marker.write_text(f"{os.getpid()}\n")
    launches = []
    waits = []

    def launch(issue):
        launches.append(issue)
        ledger = tmp_path / ".tdd" / "wt" / issue / ".tdd" / f"issue-{issue}.md"
        ledger.parent.mkdir(parents=True)
        ledger.write_text("- [ ] step\n")

    def wait():
        waits.append(1)
        if len(waits) == 3:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["7", "8"] + launches, raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues",
                        lambda: [i for i in ["12", "15"] if i not in launches], raising=False)
    monkeypatch.setattr(dispatch, "launch", launch, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "4"])
    except _StopWaiting:
        code = None

    assert (code, capsys.readouterr().out, launches) == (None, "", ["12"])


def test_main_launches_the_next_issue_at_target_2_beside_one_live_run_and_a_worktree_whose_restart_marker_names_a_dead_restarter_issue_3495(
        monkeypatch, tmp_path, dispatch):
    marker = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "restart-pending"
    marker.parent.mkdir(parents=True)
    marker.write_text("4242\n")
    launches = []

    def dead(pid, sig):
        raise ProcessLookupError(pid)

    def wait():
        raise _StopWaiting

    monkeypatch.setattr(dispatch.os, "kill", dead)
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "2"])

    assert launches == ["12"]


_REAL = {}


@pytest.fixture(autouse=True)
def no_open_run_prs(monkeypatch, dispatch):
    _REAL.update({name: getattr(dispatch, name, None) for name in ("run_pr_paths", "issue_paths")})
    monkeypatch.setattr(dispatch, "run_pr_paths", lambda: {}, raising=False)
    monkeypatch.setattr(dispatch, "issue_paths", lambda issue: [], raising=False)


def _overlap_case(monkeypatch, tmp_path, dispatch, solvable, named, prs, waits_before_stop=1):
    (tmp_path / ".tdd").mkdir(exist_ok=True)
    launches = []
    waits = []

    def wait():
        waits.append(list(launches))
        if len(waits) == waits_before_stop:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-09T10:00:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", solvable, raising=False)
    monkeypatch.setattr(dispatch, "issue_paths", lambda issue: named.get(issue, []), raising=False)
    monkeypatch.setattr(dispatch, "run_pr_paths", prs, raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)
    return launches, waits


def test_main_skips_a_solvable_issue_naming_a_path_an_open_run_draft_pr_changes_and_launches_the_next_without_overlap_issue_3478(
        monkeypatch, tmp_path, dispatch):
    launches, _ = _overlap_case(
        monkeypatch, tmp_path, dispatch, lambda: ["12", "15"],
        {"12": ["skills/tdd/scripts/veri/dispatch.py"], "15": ["skills/tdd/scripts/veri/status.py"]},
        lambda: {"https://github.com/o/r/pull/90": ["skills/tdd/scripts/veri/dispatch.py"]})

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    assert launches == ["15"]


def test_main_launches_an_issue_skipped_for_overlap_at_a_later_pass_once_no_open_run_draft_pr_changes_its_paths_issue_3478(
        monkeypatch, tmp_path, dispatch):
    open_prs = [{"https://github.com/o/r/pull/90": ["skills/tdd/scripts/veri/dispatch.py"]}, {}, {}]
    launched = []
    launches, waits = _overlap_case(
        monkeypatch, tmp_path, dispatch, lambda: [i for i in ["12", "15"] if i not in launched],
        {"12": ["skills/tdd/scripts/veri/dispatch.py"], "15": ["skills/tdd/scripts/veri/status.py"]},
        lambda: open_prs[len(waits)], waits_before_stop=2)

    def launch(issue):
        launched.append(issue)
        launches.append(issue)
        ledger = tmp_path / ".tdd" / "wt" / issue / ".tdd" / f"issue-{issue}.md"
        ledger.parent.mkdir(parents=True)
        ledger.write_text("- [ ] step\n")

    monkeypatch.setattr(dispatch, "launch", launch, raising=False)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "2"])

    assert waits == [["15"], ["15", "12"]]


def test_main_prints_one_line_per_skip_naming_the_skipped_issue_the_overlapping_path_and_the_pr_issue_3478(
        monkeypatch, capsys, tmp_path, dispatch):
    _overlap_case(
        monkeypatch, tmp_path, dispatch, lambda: ["12", "15"],
        {"12": ["skills/tdd/SCRIPTS.md", "skills/tdd/scripts/veri/dispatch.py"], "15": ["skills/tdd/scripts/veri/status.py"]},
        lambda: {"https://github.com/o/r/pull/90": ["skills/tdd/scripts/veri/dispatch.py"]})

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    assert capsys.readouterr().out == "skip 12 skills/tdd/scripts/veri/dispatch.py https://github.com/o/r/pull/90\n"


def test_main_launches_nothing_and_keeps_waiting_never_reporting_queue_empty_when_every_solvable_issue_overlaps_issue_3478(
        monkeypatch, capsys, tmp_path, dispatch):
    launches, waits = _overlap_case(
        monkeypatch, tmp_path, dispatch, lambda: ["12", "15"],
        {"12": ["skills/tdd/scripts/veri/dispatch.py"], "15": ["skills/tdd/SCRIPTS.md"]},
        lambda: {"https://github.com/o/r/pull/90": ["skills/tdd/scripts/veri/dispatch.py", "skills/tdd/SCRIPTS.md"]},
        waits_before_stop=2)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    assert (launches, len(waits), "queue-empty" in capsys.readouterr().out) == ([], 2, False)


def test_main_exits_2_naming_the_failure_and_launches_nothing_when_gh_pr_diff_of_an_open_run_draft_pr_fails_issue_3478(
        monkeypatch, capsys, tmp_path, dispatch):
    import subprocess
    launches, _ = _overlap_case(
        monkeypatch, tmp_path, dispatch, lambda: ["12"], {"12": ["skills/tdd/scripts/veri/dispatch.py"]},
        _REAL["run_pr_paths"])
    monkeypatch.setattr(dispatch.handoff_state, "open_prs", lambda fields, *extra: [
        {"number": 90, "url": "https://github.com/o/r/pull/90", "isDraft": True, "headRefName": "tdd/80-other"}])
    monkeypatch.setattr(dispatch.github.subprocess, "run",
                        lambda argv, **kw: subprocess.CompletedProcess(argv, 1, stdout="", stderr="HTTP 502: Bad Gateway\n"))

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    err = capsys.readouterr().err
    assert (code, launches, "90" in err and "HTTP 502" in err) == (2, [], True)


def test_main_prints_a_skip_line_once_per_issue_pr_and_path_for_the_life_of_the_process_not_on_every_pass_issue_3478(
        monkeypatch, capsys, tmp_path, dispatch):
    _overlap_case(
        monkeypatch, tmp_path, dispatch, lambda: ["12"], {"12": ["skills/tdd/scripts/veri/dispatch.py"]},
        lambda: {"https://github.com/o/r/pull/90": ["skills/tdd/scripts/veri/dispatch.py"]}, waits_before_stop=3)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    assert capsys.readouterr().out == "skip 12 skills/tdd/scripts/veri/dispatch.py https://github.com/o/r/pull/90\n"


def test_main_while_every_solvable_issue_overlaps_reads_each_issue_body_once_each_pr_diff_once_per_head_sha_and_the_pr_list_once_per_poll_window_issue_3478(
        monkeypatch, tmp_path, dispatch):
    times = [0, 10, 70, 80, 140]
    listed, diffed, viewed = [], [], []
    _, waits = _overlap_case(
        monkeypatch, tmp_path, dispatch, lambda: ["12", "15"], {}, _REAL["run_pr_paths"], waits_before_stop=len(times))
    monkeypatch.setattr(dispatch, "issue_paths", _REAL["issue_paths"])
    monkeypatch.setattr(dispatch, "clock", lambda: times[len(waits)])

    def open_prs(fields, *extra):
        listed.append(1)
        return [{"number": 90, "url": "https://github.com/o/r/pull/90", "isDraft": True,
                 "headRefName": "tdd/80-other", "headRefOid": "bbb" if times[len(waits)] >= 140 else "aaa"}]

    def diff(number):
        diffed.append(number)
        return ["skills/tdd/scripts/veri/dispatch.py", "skills/tdd/SCRIPTS.md"]

    def view(issue, field):
        viewed.append(issue)
        return {"12": "Touches `skills/tdd/scripts/veri/dispatch.py`.", "15": "Edits `skills/tdd/SCRIPTS.md`."}[issue]

    monkeypatch.setattr(dispatch.handoff_state, "open_prs", open_prs)
    monkeypatch.setattr(dispatch.github, "gh_pr_diff_names", diff)
    monkeypatch.setattr(dispatch.github, "gh_issue_view", view)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    assert (len(listed), diffed, viewed) == (3, [90, 90], ["12", "15"])


@pytest.mark.parametrize("poll", ["soon", "-5"])
def test_main_with_a_bad_overlap_poll_window_prints_the_usage_on_stderr_and_exits_2_before_any_launch_issue_3478(
        monkeypatch, tmp_path, run_cli, dispatch, poll):
    (tmp_path / ".tdd").mkdir()
    launches = []

    monkeypatch.setenv("VERI_DISPATCH_OVERLAP_POLL", poll)
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", lambda: (_ for _ in ()).throw(_StopWaiting), raising=False)

    code, out, err = run_cli(dispatch, ["--target", "1"])

    assert (code, out, err, launches) == (2, "", "usage: dispatch.sh [--target <N>]  (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing; with no --target, N and the launch order come from .tdd/role-dev.state in the main working tree: its last n= line, overridden by an unexpired timed-n line, and each override line pulls the issue it names to the front; exit 2 if that file is unreadable, has no n= line, or has a malformed n=, timed-n or override line)\n", [])


def _real_overlap_reads(monkeypatch, dispatch, prs, bodies, diffs):
    monkeypatch.setattr(dispatch, "run_pr_paths", _REAL["run_pr_paths"])
    monkeypatch.setattr(dispatch, "issue_paths", _REAL["issue_paths"])
    monkeypatch.setattr(dispatch.handoff_state, "open_prs", lambda fields, *extra: prs)
    monkeypatch.setattr(dispatch.github, "gh_pr_diff_names", lambda number: diffs[number])
    monkeypatch.setattr(dispatch.github, "gh_issue_view", lambda issue, field: bodies[issue])


def test_main_counts_only_a_path_an_issue_body_names_in_backticks_not_one_it_names_in_prose_issue_3478(
        monkeypatch, capsys, tmp_path, dispatch):
    path = "skills/tdd/scripts/veri/dispatch.py"
    launches, _ = _overlap_case(monkeypatch, tmp_path, dispatch, lambda: ["12", "15", "18"], {}, None)
    _real_overlap_reads(monkeypatch, dispatch,
                        [{"number": 90, "url": "https://github.com/o/r/pull/90", "isDraft": True,
                          "headRefName": "tdd/80-other", "headRefOid": "aaa"}],
                        {"12": f"Change `{path}` and the `conductor` wording.\n",
                         "15": f"Touches {path} too, named in prose; run `make test`.\n",
                         "18": "Nothing named.\n"},
                        {90: [path, "conductor"]})

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    assert (launches, capsys.readouterr().out) == (["15"], f"skip 12 {path} https://github.com/o/r/pull/90\n")


def test_main_counts_only_an_open_draft_pr_on_a_tdd_branch_as_a_run_pr_issue_3478(
        monkeypatch, tmp_path, dispatch):
    path, other = "skills/tdd/scripts/veri/dispatch.py", "skills/tdd/SCRIPTS.md"

    def pr(number, draft, head):
        return {"number": number, "url": f"https://github.com/o/r/pull/{number}", "isDraft": draft,
                "headRefName": head, "headRefOid": "aaa"}

    launches, _ = _overlap_case(monkeypatch, tmp_path, dispatch, lambda: ["15", "12"], {}, None)
    _real_overlap_reads(monkeypatch, dispatch,
                        [pr(90, True, "tdd/80-run"), pr(91, False, "tdd/81-ready"), pr(92, True, "fix-by-hand")],
                        {"12": f"Change `{path}`.\n", "15": f"Change `{other}`.\n"},
                        {90: [other], 91: [path], 92: [path]})

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    assert launches == ["12"]


def test_main_reads_the_queue_at_most_once_per_overlap_poll_window_while_everything_overlaps_yet_reports_a_conductor_exit_on_the_next_pass_issue_3478(
        monkeypatch, tmp_path, dispatch):
    times = [0, 10, 70, 80, 90]
    queue_reads = []
    _, waits = _overlap_case(
        monkeypatch, tmp_path, dispatch, lambda: queue_reads.append(times[len(waits)]) or ["12"],
        {"12": ["skills/tdd/scripts/veri/dispatch.py"]},
        lambda: {"https://github.com/o/r/pull/90": ["skills/tdd/scripts/veri/dispatch.py"]}, waits_before_stop=len(times))
    (tmp_path / ".tdd" / "wt" / "5").mkdir(parents=True)
    monkeypatch.setattr(dispatch, "clock", lambda: times[len(waits)])
    monkeypatch.setattr(dispatch, "live_conductors", lambda: ["5"] if len(waits) < 4 else [])
    monkeypatch.setattr(dispatch, "last_comment", lambda issue: "### ✅ Done — https://github.com/o/r/pull/9\n")

    code = dispatch.main(["--target", "2"])

    assert (code, queue_reads, len(waits)) == (0, [0, 70], 4)


_RATE_LIMITED = "gh: API rate limit exceeded for user ID 1. (HTTP 403)\n"


def _gh_rest(monkeypatch, dispatch, times, waits, limited_until, limited_read, reads, refusal=_RATE_LIMITED):
    """Fake gh at the process boundary over REST, handing back a refusal's stderr only to a caller that pipes it,
    as subprocess does: the open-PR list (one run draft PR changing other.py),
    issue 12's body naming dispatch.py and the PR's diff; <limited_read> is refused as rate-limited until
    <limited_until>, and every read of it is recorded in <reads>."""
    import subprocess

    def run(argv, **kw):
        if argv[:3] == ["gh", "api", "rate_limit"]:
            return subprocess.CompletedProcess(argv, 0, stdout=f"{limited_until}\n", stderr="")
        what = "diff" if argv[:3] == ["gh", "pr", "diff"] else "list" if "/pulls" in argv[2] else "body"
        if what == limited_read and not argv[2].endswith("page=2"):
            reads.append(times[len(waits)])
            if times[len(waits)] < limited_until:
                if kw.get("stderr") != subprocess.PIPE:
                    sys.stderr.write(refusal)
                return subprocess.CompletedProcess(argv, 1, stdout='{"message": "API rate limit exceeded"}',
                                                   stderr=refusal if kw.get("stderr") == subprocess.PIPE else None)
        if what == "list":
            page = '[{"number": 90, "html_url": "https://github.com/o/r/pull/90", "draft": true,' \
                   ' "head": {"ref": "tdd/80-other", "sha": "aaa"}}]'
            return subprocess.CompletedProcess(argv, 0, stdout=page if argv[2].endswith("page=1") else "[]", stderr="")
        if what == "diff":
            return subprocess.CompletedProcess(argv, 0, stdout="skills/tdd/SCRIPTS.md\n", stderr="")
        body = '{"body": "Change `skills/tdd/scripts/veri/dispatch.py`.", "labels": []}'
        return subprocess.CompletedProcess(argv, 0, stdout=body, stderr="")

    monkeypatch.setattr(dispatch.github.subprocess, "run", run)
    monkeypatch.setattr(dispatch, "run_pr_paths", _REAL["run_pr_paths"])
    monkeypatch.setattr(dispatch, "issue_paths", _REAL["issue_paths"])
    monkeypatch.setattr(dispatch, "clock", lambda: times[len(waits)])


@pytest.mark.parametrize("limited_read", ["list", "body"])
def test_main_with_a_rate_limited_pr_list_or_issue_body_read_waits_for_the_reset_then_reads_again_and_launches_issue_3478(
        monkeypatch, capsys, tmp_path, dispatch, limited_read):
    times = [0, 50, 100]
    reads = []
    launches, waits = _overlap_case(monkeypatch, tmp_path, dispatch, lambda: ["12"], {}, None,
                                    waits_before_stop=len(times))
    _gh_rest(monkeypatch, dispatch, times, waits, 100, limited_read, reads)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    assert (code, reads, launches) == (None, [0, 100], ["12"])


@pytest.mark.parametrize("failed_read, named", [("list", "the open PR list"), ("body", "issue 12's body")])
def test_main_exits_2_naming_a_failed_pr_list_or_issue_body_read_and_launches_nothing_issue_3478(
        monkeypatch, capsys, tmp_path, dispatch, failed_read, named):
    times = [0, 50]
    launches, waits = _overlap_case(monkeypatch, tmp_path, dispatch, lambda: ["12"], {}, None,
                                    waits_before_stop=len(times))
    _gh_rest(monkeypatch, dispatch, times, waits, 100, failed_read, [], refusal="gh: HTTP 502: Bad Gateway\n")

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

    err = capsys.readouterr().err
    assert (code, launches, f"reading {named} failed: gh: HTTP 502: Bad Gateway" in err) == (2, [], True)


def test_main_skips_an_overlap_read_through_the_rest_pr_shape_naming_its_html_url_and_rereads_the_diff_when_its_head_sha_changes_issue_3478(
        monkeypatch, capsys, tmp_path, dispatch):
    import subprocess
    path = "skills/tdd/scripts/veri/dispatch.py"
    times = [0, 70]
    diff_reads = []
    launches, waits = _overlap_case(monkeypatch, tmp_path, dispatch, lambda: ["12"], {}, None,
                                    waits_before_stop=len(times))

    def run(argv, **kw):
        if argv[:3] == ["gh", "pr", "diff"]:
            diff_reads.append(times[len(waits)])
            return subprocess.CompletedProcess(argv, 0, stdout=path + "\n", stderr="")
        if "/pulls" in argv[2]:
            sha = "aaa" if times[len(waits)] < 70 else "bbb"
            page = '[{"number": 90, "html_url": "https://github.com/o/r/pull/90", "draft": true,' \
                   ' "head": {"ref": "tdd/80-other", "sha": "%s"}}]' % sha
            return subprocess.CompletedProcess(argv, 0, stdout=page if argv[2].endswith("page=1") else "[]", stderr="")
        return subprocess.CompletedProcess(argv, 0, stdout='{"body": "Change `%s`.", "labels": []}' % path, stderr="")

    monkeypatch.setattr(dispatch.github.subprocess, "run", run)
    monkeypatch.setattr(dispatch, "run_pr_paths", _REAL["run_pr_paths"])
    monkeypatch.setattr(dispatch, "issue_paths", _REAL["issue_paths"])
    monkeypatch.setattr(dispatch, "clock", lambda: times[len(waits)])

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    assert (launches, diff_reads, capsys.readouterr().out) == (
        [], [0, 70], f"skip 12 {path} https://github.com/o/r/pull/90\n")


def test_main_prints_no_second_skip_line_for_the_same_overlap_seen_again_after_the_poll_hold_expires_issue_3478(
        monkeypatch, capsys, tmp_path, dispatch):
    times = [0, 70, 140]
    queue_reads = []
    _, waits = _overlap_case(
        monkeypatch, tmp_path, dispatch, lambda: queue_reads.append(times[len(waits)]) or ["12"],
        {"12": ["skills/tdd/scripts/veri/dispatch.py"]},
        lambda: {"https://github.com/o/r/pull/90": ["skills/tdd/scripts/veri/dispatch.py"]}, waits_before_stop=len(times))
    monkeypatch.setattr(dispatch, "clock", lambda: times[len(waits)])

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    assert (queue_reads, capsys.readouterr().out) == (
        [0, 70, 140], "skip 12 skills/tdd/scripts/veri/dispatch.py https://github.com/o/r/pull/90\n")


def test_main_at_target_3_launches_nothing_with_three_live_pid_files_one_hand_launched_issue_3525(
        monkeypatch, tmp_path, dispatch):
    import pid_file
    (tmp_path / ".tdd").mkdir()
    parents = {101: "500", 102: "500", 103: "501"}
    commands = {"500": "python3 veri/run_conductor.py 1", "501": "bash run-conductor.sh 3"}
    for pid, issue in ((101, "1"), (102, "2"), (103, "3")):
        run = tmp_path / ".tdd" / "wt" / issue / ".tdd"
        run.mkdir(parents=True)
        (run / "conductor.pid").write_text(f"{pid}\nstarted-at\n")
    launches = []

    def ps(field, pid):
        return {"lstart": "started-at", "ppid": parents[int(pid)], "command": "claude"}[field] \
            if int(pid) in parents else commands[str(pid)]

    def wait():
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch.status, "branch_of", lambda run: "")
    monkeypatch.setattr(pid_file.os, "kill", lambda pid, sig: None)
    monkeypatch.setattr(pid_file, "_ps", ps)
    monkeypatch.setattr(pid_file, "_conductors", lambda: [])
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [])
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["99"])
    monkeypatch.setattr(dispatch, "run_pr_paths", lambda: {})
    monkeypatch.setattr(dispatch, "launch", launches.append)
    monkeypatch.setattr(dispatch, "wait", wait)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "3"])

    assert (launches, (tmp_path / ".tdd" / "dispatch.log").exists()) == ([], False)


def test_main_at_target_1_launches_nothing_with_a_live_pid_file_whose_ledger_and_journal_exist_but_whose_process_tree_does_not_match_issue_3525(
        monkeypatch, tmp_path, dispatch):
    import pid_file
    run = tmp_path / ".tdd" / "wt" / "1" / ".tdd"
    run.mkdir(parents=True)
    (run / "conductor.pid").write_text("101\nstarted-at\n")
    (run / "issue-1.md").write_text("# Plan for #1 — title\n- [ ] step\n")
    (run / "events.jsonl").write_text('{"event": "leaf-start", "ts": 1000}\n')
    launches = []

    def ps(field, pid):
        return {"lstart": "started-at", "ppid": "500", "command": "vim notes"}[field] if int(pid) == 101 \
            else "bash unrelated.sh"

    def wait():
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch.status, "branch_of", lambda run: "")
    monkeypatch.setattr(pid_file.os, "kill", lambda pid, sig: None)
    monkeypatch.setattr(pid_file, "_ps", ps)
    monkeypatch.setattr(pid_file, "_conductors", lambda: [])
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [])
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["99"])
    monkeypatch.setattr(dispatch, "run_pr_paths", lambda: {})
    monkeypatch.setattr(dispatch, "launch", launches.append)
    monkeypatch.setattr(dispatch, "wait", wait)

    with pytest.raises(_StopWaiting):
        dispatch.main(["--target", "1"])

    assert launches == []


def _fake_one_pass(monkeypatch, dispatch, tmp_path, state, solvable, launches):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text(state)

    def wait():
        raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "now", lambda: "2026-11-07T10:30:00", raising=False)
    monkeypatch.setattr(dispatch, "live_conductors", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "queued_merges", lambda: [], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: solvable, raising=False)
    monkeypatch.setattr(dispatch, "launch", launches.append, raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)


def test_main_with_no_target_and_an_override_line_of_fewer_than_4_fields_exits_2_naming_the_line_and_launches_nothing(
        run_cli, monkeypatch, tmp_path, dispatch):
    launches = []
    _fake_one_pass(monkeypatch, dispatch, tmp_path, "n=1\noverride dev-1 2026-11-07T10:00:00\n", ["12"], launches)
    code, out, err = run_cli(dispatch, [])
    assert (code, out, launches) == (2, "", [])
    assert "override dev-1 2026-11-07T10:00:00" in err


def test_prioritize_moves_an_issue_two_override_lines_name_to_the_front_once(dispatch):
    lines = ["n=2", "override dev-1 2026-11-07T10:00:00 take #15 first", "override dev-2 2026-11-07T10:01:00 take #12 next",
             "override dev-3 2026-11-07T10:02:00 take #15 again"]
    assert dispatch.prioritize(["12", "15", "20"], lines) == ["12", "15", "20"]


def test_main_with_no_target_and_a_role_dev_state_file_that_exists_but_is_unreadable_exits_2_naming_the_file_and_launches_nothing(
        run_cli, dispatch, monkeypatch, tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text("n=1\n")
    launches = []
    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch.os, "access", lambda path, mode: False)
    monkeypatch.setattr(dispatch, "launch", launches.append)
    code, out, err = run_cli(dispatch, [])
    assert (code, out, launches) == (2, "", [])
    assert str(tmp_path / ".tdd" / "role-dev.state") in err


def test_main_with_no_target_and_a_role_dev_state_file_with_no_n_line_exits_2_naming_the_file_and_launches_nothing(
        run_cli, monkeypatch, tmp_path, dispatch):
    launches = []
    _fake_one_pass(monkeypatch, dispatch, tmp_path, "override dev-1 2026-11-07T10:00:00 take #12 first\n", ["12"], launches)
    code, out, err = run_cli(dispatch, [])
    assert (code, out, launches) == (2, "", [])
    assert "no n= line" in err
    assert str(tmp_path / ".tdd" / "role-dev.state") in err


def test_main_with_no_target_and_a_malformed_timed_n_line_exits_2_naming_the_line_and_launches_nothing(
        run_cli, monkeypatch, tmp_path, dispatch):
    launches = []
    _fake_one_pass(monkeypatch, dispatch, tmp_path, "n=1\ntimed-n dev-1 2026-11-07T10:00:00\n", ["12"], launches)
    code, out, err = run_cli(dispatch, [])
    assert (code, out, launches) == (2, "", [])
    assert "malformed timed-n line" in err
    assert "timed-n dev-1 2026-11-07T10:00:00" in err
