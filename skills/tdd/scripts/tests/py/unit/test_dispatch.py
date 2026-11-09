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

    def wait():
        waits.append(1)
        if len(waits) == 2:
            raise _StopWaiting

    monkeypatch.setattr(dispatch.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(dispatch, "live_conductors", lambda: lives.pop(0) if len(lives) > 1 else lives[0], raising=False)
    monkeypatch.setattr(dispatch, "solvable_issues", lambda: ["12"], raising=False)
    monkeypatch.setattr(dispatch, "launch", lambda issue: None, raising=False)
    monkeypatch.setattr(dispatch, "last_comment", lambda issue: "### 🔧 Working on it\n\nbody", raising=False)
    monkeypatch.setattr(dispatch, "wait", wait, raising=False)

    try:
        code = dispatch.main(["--target", "1"])
    except _StopWaiting:
        code = None

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

    assert (code, out, err, launches) == (2, "", "usage: dispatch.sh --target <N>\n", [])


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

    results = [run_cli(dispatch, argv) for argv in (["--target", "0"], ["--target", "abc"], ["--target"])]

    usage = (2, "", "usage: dispatch.sh --target <N>\n")
    assert (results, launches) == ([usage, usage, usage], [])


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

    assert (code, out, err, launches) == (2, "", "usage: dispatch.sh --target <N>\n", [])


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

    assert (code, out, err, launches) == (2, "", "usage: dispatch.sh --target <N>\n", [])


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

    assert (code, out, err, launches, reads) == (0, "usage: dispatch.sh --target <N>\n", "", [], [])


def test_main_with_help_writes_exactly_one_usage_line_to_the_stdout_descriptor_and_nothing_to_stderr(
        run_cli, dispatch):
    code, out, err = run_cli(dispatch, ["--help"])

    assert (code, out, err) == (0, "usage: dispatch.sh --target <N>\n", "")


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
