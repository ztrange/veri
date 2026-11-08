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

    captured = capsys.readouterr()
    assert (code, captured.out, "7" in captured.err) == (2, "", True)


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
