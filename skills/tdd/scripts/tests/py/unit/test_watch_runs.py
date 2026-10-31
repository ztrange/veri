"""In-process cases for veri/watch_runs.py, the module watch-runs.sh is a shim over."""
import importlib
import itertools
import json
import os
import subprocess

import pytest


@pytest.fixture
def watch_runs():
    return importlib.import_module("veri.watch_runs")


def test_main_prints_exited_with_the_first_word_of_the_state_when_a_conductor_live_at_start_exits(
        monkeypatch, capsys, watch_runs):
    listings = iter([["5", "7"], ["5", "7"], ["7"]])
    waits = []
    monkeypatch.setattr(watch_runs, "live_conductors", lambda: next(listings))
    monkeypatch.setattr(watch_runs, "run_state", lambda issue: {"5": "bailed red tests-pass", "7": "running"}[issue])
    monkeypatch.setattr(watch_runs, "wait", lambda: waits.append(1))

    code = watch_runs.main([])

    assert (code, capsys.readouterr().out) == (0, "exited 5 bailed\n")
    assert len(waits) == 2


def test_main_with_target_prints_slot_free_with_the_first_solvable_issue_when_fewer_than_target_are_live(
        monkeypatch, capsys, watch_runs):
    waits = []

    def wait():
        waits.append(1)
        if len(waits) > 3:
            raise RuntimeError("never printed slot-free")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["5"])
    monkeypatch.setattr(watch_runs, "solvable_issues", lambda: ["12", "15"], raising=False)
    monkeypatch.setattr(watch_runs, "wait", wait)

    code = watch_runs.main(["--target", "2"])

    assert (code, capsys.readouterr().out) == (0, "slot-free 1/2 next 12\n")


def test_main_with_max_wait_prints_timeout_and_returns_3_when_nothing_actionable_happens_within_the_wait(
        monkeypatch, capsys, watch_runs):
    now = [100.0]
    waits = []

    def wait():
        waits.append(1)
        now[0] += 4
        if len(waits) > 10:
            raise RuntimeError("never printed timeout")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["5"])
    monkeypatch.setattr(watch_runs, "clock", lambda: now[0], raising=False)
    monkeypatch.setattr(watch_runs, "wait", wait)

    code = watch_runs.main(["--max-wait", "10"])

    assert (code, capsys.readouterr().out) == (3, "timeout\n")


def test_main_prints_nothing_across_polls_in_which_no_conductor_exits_and_no_slot_frees(
        monkeypatch, capsys, watch_runs):
    listings = iter([["5", "7"]] * 5 + [["7"]])
    printed_during_waits = []

    def wait():
        printed_during_waits.append(capsys.readouterr().out)

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: next(listings))
    monkeypatch.setattr(watch_runs, "run_state", lambda issue: "done")
    monkeypatch.setattr(watch_runs, "wait", wait)

    code = watch_runs.main([])

    assert (code, printed_during_waits, capsys.readouterr().out) == (0, [""] * 5, "exited 5 done\n")


def test_main_returns_2_with_a_usage_line_before_any_listing_when_target_or_max_wait_is_not_a_whole_number_of_at_least_1(
        monkeypatch, capsys, watch_runs):
    listings = []

    def live_conductors():
        listings.append(1)
        raise RuntimeError("listed before validating the arguments")

    monkeypatch.setattr(watch_runs, "live_conductors", live_conductors)
    monkeypatch.setattr(watch_runs, "wait", lambda: listings.append("wait"))

    outcomes = []
    for argv in (["--target", "0"], ["--target", "-1"], ["--max-wait", "abc"], ["--max-wait", ""], ["--target"]):
        code = watch_runs.main(argv)
        captured = capsys.readouterr()
        outcomes.append((argv, code, captured.out, captured.err.lower().startswith("usage")))

    assert outcomes == [(argv, 2, "", True) for argv, *_ in outcomes]
    assert listings == []


@pytest.mark.parametrize("argv", [
    pytest.param(["--max-wiat", "3"], id="unknown-flag"),
    pytest.param(["--target", "2", "junk"], id="trailing-junk"),
    pytest.param(["--target", "2", "--target", "3"], id="repeated-flag"),
    pytest.param(["--target", "2", "--max-wait"], id="second-flag-missing-its-value"),
])
def test_main_exits_2_with_the_usage_line_before_any_listing_on_an_argument_list_outside_the_accepted_shapes_1930(
        monkeypatch, capsys, watch_runs, argv):
    listings = []

    def wait():
        raise RuntimeError("polled")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: listings.append(1) or [])
    monkeypatch.setattr(watch_runs, "solvable_issues", lambda: [], raising=False)
    monkeypatch.setattr(watch_runs, "wait", wait)

    try:
        code = watch_runs.main(argv)
    except RuntimeError:
        code = "polled"

    assert (code, capsys.readouterr().err.startswith("usage: watch-runs.sh"), listings) == (2, True, [])


@pytest.mark.parametrize("argv", [
    pytest.param(["--target", "5", "--max-wait", "3"], id="target-first"),
    pytest.param(["--max-wait", "3", "--target", "5"], id="max-wait-first"),
])
def test_main_with_target_and_max_wait_in_either_order_prints_timeout_and_returns_3_when_the_wait_elapses_before_a_slot_frees_1930(
        monkeypatch, capsys, watch_runs, argv):
    now = [100.0]
    waits = []

    def wait():
        waits.append(1)
        now[0] += 1
        if len(waits) > 10:
            raise RuntimeError("never printed timeout")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["5"])
    monkeypatch.setattr(watch_runs, "solvable_issues", lambda: [], raising=False)
    monkeypatch.setattr(watch_runs, "clock", lambda: now[0], raising=False)
    monkeypatch.setattr(watch_runs, "wait", wait)

    code = watch_runs.main(argv)

    assert (code, capsys.readouterr().out) == (3, "timeout\n")


@pytest.mark.parametrize("argv", [
    pytest.param(["--target", "2", "--max-wait", "30"], id="target-first"),
    pytest.param(["--max-wait", "30", "--target", "2"], id="max-wait-first"),
])
def test_main_with_target_and_max_wait_in_either_order_prints_slot_free_and_returns_0_when_a_slot_frees_before_the_wait_elapses_1930(
        monkeypatch, capsys, watch_runs, argv):
    now = [100.0]
    waits = []

    def wait():
        waits.append(1)
        now[0] += 1
        if len(waits) > 10:
            raise RuntimeError("never printed slot-free")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["5"])
    monkeypatch.setattr(watch_runs, "solvable_issues", lambda: ["12", "15"], raising=False)
    monkeypatch.setattr(watch_runs, "clock", lambda: now[0], raising=False)
    monkeypatch.setattr(watch_runs, "wait", wait)

    code = watch_runs.main(argv)

    assert (code, capsys.readouterr().out) == (0, "slot-free 1/2 next 12\n")


def test_main_with_target_exits_2_and_passes_on_stderr_when_solvable_issues_exits_non_zero_1930(
        monkeypatch, capsys, watch_runs):
    waits = []

    def wait():
        waits.append(1)
        if len(waits) > 3:
            raise RuntimeError("waited on after the queue read failed")

    def run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 1, stdout="", stderr="gh: not logged in\n")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["5"])
    monkeypatch.setattr(watch_runs.subprocess, "run", run)
    monkeypatch.setattr(watch_runs, "wait", wait)

    try:
        code = watch_runs.main(["--target", "2"])
    except RuntimeError:
        code = "waited on"

    captured = capsys.readouterr()
    assert (code, captured.out, "gh: not logged in" in captured.err) == (2, "", True)


def test_main_keeps_watching_a_conductor_live_at_start_that_vanished_from_the_run_listing_while_its_conductor_pid_answers_kill_0_1930(
        monkeypatch, capsys, tmp_path, watch_runs):
    import os
    (tmp_path / ".tdd" / "wt" / "5" / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "wt" / "5" / ".tdd" / "conductor.pid").write_text("%d\n" % os.getpid())
    listings = iter([["5", "7"]])
    ticks = iter([0])
    monkeypatch.setattr(watch_runs.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(watch_runs, "live_conductors", lambda: next(listings, ["7"]))
    monkeypatch.setattr(watch_runs, "run_state", lambda issue: "")
    monkeypatch.setattr(watch_runs, "wait", lambda: None)
    monkeypatch.setattr(watch_runs, "clock", lambda: next(ticks, 10))

    code = watch_runs.main(["--max-wait", "5"])

    assert (code, capsys.readouterr().out) == (3, "timeout\n")


def test_main_with_no_flags_and_no_live_conductor_at_start_prints_nothing_to_watch_and_returns_3_without_blocking_1930(
        monkeypatch, capsys, watch_runs):
    waits = []

    def wait():
        waits.append(1)
        if len(waits) > 3:
            raise RuntimeError("blocked with nothing to watch")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: [])
    monkeypatch.setattr(watch_runs, "wait", wait)

    try:
        code = watch_runs.main([])
    except RuntimeError:
        code = "blocked"

    out = capsys.readouterr().out
    assert (code, "nothing to watch" in out) == (3, True)


def test_main_keeps_watching_when_a_conductor_live_at_start_drops_out_of_the_run_listing_while_its_conductor_pid_answers_kill_0_1930(
        monkeypatch, capsys, tmp_path, watch_runs):
    import os
    (tmp_path / ".tdd" / "wt" / "5" / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "wt" / "5" / ".tdd" / "conductor.pid").write_text("%d\n" % os.getpid())
    both = {"runs": [{"issue": 5, "state": "running"}, {"issue": 7, "state": "running"}]}
    only_7 = {"runs": [{"issue": 7, "state": "running"}]}
    documents = iter([both])
    ticks = iter([0])
    waits = []

    def wait():
        waits.append(1)
        if len(waits) > 3:
            raise RuntimeError("never timed out")

    monkeypatch.setattr(watch_runs.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(watch_runs.status, "json_document",
                        lambda scope=None, read_states=True: (0, json.dumps(next(documents, only_7))))
    monkeypatch.setattr(watch_runs, "_starting", lambda: [])
    monkeypatch.setattr(watch_runs, "wait", wait)
    monkeypatch.setattr(watch_runs, "clock", lambda: next(ticks, 10))

    code = watch_runs.main(["--max-wait", "5"])

    assert (code, capsys.readouterr().out) == (3, "timeout\n")


def test_solvable_issues_asks_the_solvable_issues_script_beside_watch_runs_through_an_unresolved_symlinked_directory(
        monkeypatch, tmp_path):
    import importlib.util
    import pathlib
    real_scripts = pathlib.Path(__file__).resolve().parents[3]
    link = tmp_path / "scripts"
    link.symlink_to(real_scripts)
    spec = importlib.util.spec_from_file_location("watch_runs_via_symlink", link / "veri" / "watch_runs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    module.solvable_issues()

    assert calls == [[f"{link}/veri/../solvable-issues.sh", "--not-running"]]


def test_2545_main_keeps_watching_when_a_run_not_live_at_start_has_its_worktree_removed_mid_read(
        monkeypatch, capsys, tmp_path, watch_runs):
    status = watch_runs.status
    run = tmp_path / ".tdd" / "wt" / "9"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "issue-9.md").write_text("# Plan for #9 — t\n")
    (run / ".tdd" / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "9", "event": "launch"}) + "\n")
    real_read_events = status.read_events
    polls = []

    def read_after_removal(path, *args, **kwargs):
        if polls:
            (run / ".tdd" / "events.jsonl").unlink(missing_ok=True)
        return real_read_events(path, *args, **kwargs)

    ticks = iter([0, 1])
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")
    monkeypatch.setattr(status, "issue_states", lambda: {})
    monkeypatch.setattr(status, "read_events", read_after_removal)
    monkeypatch.setattr(watch_runs, "wait", lambda: polls.append(1))
    monkeypatch.setattr(watch_runs, "clock", lambda: next(ticks) * 10)

    try:
        code = watch_runs.main(["--max-wait", "5"])
    except FileNotFoundError:
        code = "FileNotFoundError"

    assert (code, capsys.readouterr().out) == (3, "timeout\n")


def test_2547_main_reports_a_conductor_exit_without_reading_any_issue_state_from_github(
        monkeypatch, capsys, tmp_path, watch_runs):
    status = watch_runs.status
    run = tmp_path / ".tdd" / "wt" / "9"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "issue-9.md").write_text("# Plan for #9 — t\n")
    (run / ".tdd" / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "9", "event": "launch"}) + "\n")
    github_reads = []
    starting = iter([["9"]])

    def issue_states():
        github_reads.append(1)
        return {}

    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")
    monkeypatch.setattr(status, "issue_states", issue_states)
    monkeypatch.setattr(watch_runs, "_starting", lambda: next(starting, []))
    monkeypatch.setattr(watch_runs, "wait", lambda: None)

    code = watch_runs.main([])

    out = capsys.readouterr().out
    assert (code, out.startswith("exited 9 "), github_reads) == (0, True, [])


def test_2547_main_with_max_wait_shorter_than_one_poll_returns_timeout_within_a_second_of_it(
        monkeypatch, capsys, watch_runs):
    now = [100.0]
    slept = []

    def sleep(seconds):
        slept.append(seconds)
        now[0] += seconds
        if len(slept) > 10:
            raise RuntimeError("never printed timeout")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["5"])
    monkeypatch.setattr(watch_runs, "clock", lambda: now[0])
    monkeypatch.setattr(watch_runs.time, "sleep", sleep)

    code = watch_runs.main(["--max-wait", "1"])

    assert (code, capsys.readouterr().out, now[0] - 100.0 < 2) == (3, "timeout\n", True)


def test_2597_main_with_no_run_directory_and_no_arguments_prints_nothing_to_watch_and_returns_3_not_2(
        monkeypatch, capsys, tmp_path, watch_runs):
    monkeypatch.setattr(watch_runs.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(watch_runs, "wait", lambda: pytest.fail("blocked with nothing to watch"))

    code = watch_runs.main([])

    assert (code, capsys.readouterr().out) == (3, "nothing to watch\n")


def test_2597_main_with_max_wait_and_no_run_directory_prints_timeout_and_returns_3_not_2(
        monkeypatch, capsys, tmp_path, watch_runs):
    now = [100.0]
    waits = []

    def wait():
        waits.append(1)
        now[0] += 4
        if len(waits) > 10:
            raise RuntimeError("never printed timeout")

    monkeypatch.setattr(watch_runs.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(watch_runs, "clock", lambda: now[0])
    monkeypatch.setattr(watch_runs, "wait", wait)

    code = watch_runs.main(["--max-wait", "10"])

    assert (code, capsys.readouterr().out) == (3, "timeout\n")


def test_2588_main_keeps_watching_a_run_whose_conductor_pid_answers_kill_0_though_it_is_absent_from_the_live_listing(
        monkeypatch, capsys, tmp_path, watch_runs):
    import os
    (tmp_path / ".tdd" / "wt" / "5" / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "wt" / "5" / ".tdd" / "conductor.pid").write_text("%d\n" % os.getpid())
    listings = iter([["5"]])
    ticks = iter([0, 1])
    monkeypatch.setattr(watch_runs.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(watch_runs, "live_conductors", lambda: next(listings, []))
    monkeypatch.setattr(watch_runs, "run_state", lambda issue: "")
    monkeypatch.setattr(watch_runs, "wait", lambda: None)
    monkeypatch.setattr(watch_runs, "clock", lambda: next(ticks) * 10)

    code = watch_runs.main(["--max-wait", "5"])

    assert (code, capsys.readouterr().out) == (3, "timeout\n")


def test_2588_main_still_reports_vanished_when_the_conductor_pid_file_holds_no_pid_that_answers_kill_0(
        monkeypatch, capsys, tmp_path, watch_runs):
    import os
    (tmp_path / ".tdd" / "wt" / "5" / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "wt" / "5" / ".tdd" / "conductor.pid").write_text("4194999\n")
    listings = iter([["5"]])
    ticks = itertools.count(0, 1000)

    def no_such_process(pid, sig):
        raise ProcessLookupError(pid)

    monkeypatch.setattr(os, "kill", no_such_process)
    monkeypatch.setattr(watch_runs.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(watch_runs, "live_conductors", lambda: next(listings, []))
    monkeypatch.setattr(watch_runs, "run_state", lambda issue: "")
    monkeypatch.setattr(watch_runs, "wait", lambda: None)
    monkeypatch.setattr(watch_runs, "clock", lambda: next(ticks))

    code = watch_runs.main(["--max-wait", "1000000000"])

    assert (code, capsys.readouterr().out) == (2, "vanished 5\n")


def _starting_run(monkeypatch, tmp_path, watch_runs, pid_text, lstart, clock=None):
    import os
    (tmp_path / ".tdd" / "wt" / "5" / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "wt" / "5" / ".tdd" / "conductor.pid").write_text(pid_text % os.getpid())
    listings = iter([["5"]])
    ticks = iter([0, 1])
    monkeypatch.setattr(watch_runs.pid_file, "_ps", lambda field, pid: lstart)
    monkeypatch.setattr(watch_runs.status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(watch_runs, "live_conductors", lambda: next(listings, []))
    monkeypatch.setattr(watch_runs, "run_state", lambda issue: "")
    monkeypatch.setattr(watch_runs, "wait", lambda: None)
    monkeypatch.setattr(watch_runs, "clock", clock or (lambda: next(ticks) * 10))


def test_2588_main_reports_vanished_when_the_pid_answers_kill_0_but_its_start_time_differs_from_conductor_pid_line_2(
        monkeypatch, capsys, tmp_path, watch_runs):
    ticks = itertools.count(0, 1000)
    _starting_run(monkeypatch, tmp_path, watch_runs, "%d\nTue Oct 27 13:45:10 2026\n", "Wed Oct 28 09:00:00 2026",
                  clock=lambda: next(ticks))

    code = watch_runs.main(["--max-wait", "1000000000"])

    assert (code, capsys.readouterr().out) == (2, "vanished 5\n")


def test_2588_main_keeps_watching_when_the_pid_start_time_matches_conductor_pid_line_2(
        monkeypatch, capsys, tmp_path, watch_runs):
    _starting_run(monkeypatch, tmp_path, watch_runs, "%d\nTue Oct 27 13:45:10 2026\n", "Tue Oct 27 13:45:10 2026")

    code = watch_runs.main(["--max-wait", "5"])

    assert (code, capsys.readouterr().out) == (3, "timeout\n")


def test_2588_main_keeps_watching_when_conductor_pid_has_no_line_2_yet_whatever_start_time_the_pid_has(
        monkeypatch, capsys, tmp_path, watch_runs):
    _starting_run(monkeypatch, tmp_path, watch_runs, "%d\n", "Wed Oct 28 09:00:00 2026")

    code = watch_runs.main(["--max-wait", "5"])

    assert (code, capsys.readouterr().out) == (3, "timeout\n")


def test_2635_main_reports_a_conductor_exit_when_the_newest_leaf_log_holds_blank_and_prose_lines_after_stream_json(
        monkeypatch, capsys, tmp_path, watch_runs):
    status = watch_runs.status
    tdd = tmp_path / ".tdd" / "wt" / "9" / ".tdd"
    tdd.mkdir(parents=True)
    (tdd / "issue-9.md").write_text("# Plan for #9 — t\n")
    (tdd / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "9", "event": "launch"}) + "\n")
    (tdd / "conductor-9.log").write_text(
        json.dumps({"type": "system", "subtype": "init"}) + "\n"
        + json.dumps({"type": "result", "result": "done"}) + "\n")
    leaf_log = tdd / "develop-exhausted.log"
    leaf_log.write_text(
        json.dumps({"type": "system", "subtype": "init"}) + "\n"
        + json.dumps({"type": "assistant"}) + "\n"
        + "\n\nThe criterion does not hold yet\n\nSTATEMENT: prose\n")
    os.utime(leaf_log, (2_000_000_000, 2_000_000_000))
    starting = iter([["9"]])

    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")
    monkeypatch.setattr(status, "issue_states", lambda: {})
    monkeypatch.setattr(watch_runs, "_starting", lambda: next(starting, []))
    monkeypatch.setattr(watch_runs, "wait", lambda: None)

    try:
        code = watch_runs.main([])
    except ValueError as raised:
        code = "ValueError: %s" % raised

    assert (code, capsys.readouterr().out) == (0, "exited 9 stale\n")


def test_2635_main_reports_a_conductor_exit_when_the_newest_leaf_log_holds_only_a_partial_first_line(
        monkeypatch, capsys, tmp_path, watch_runs):
    status = watch_runs.status
    tdd = tmp_path / ".tdd" / "wt" / "9" / ".tdd"
    tdd.mkdir(parents=True)
    (tdd / "issue-9.md").write_text("# Plan for #9 — t\n")
    (tdd / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "9", "event": "launch"}) + "\n")
    (tdd / "conductor-9.log").write_text(
        json.dumps({"type": "system", "subtype": "init"}) + "\n"
        + json.dumps({"type": "result", "result": "done"}) + "\n")
    leaf_log = tdd / "develop-exhausted.log"
    leaf_log.write_text('{"type": "syst')
    os.utime(leaf_log, (2_000_000_000, 2_000_000_000))
    starting = iter([["9"]])

    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")
    monkeypatch.setattr(status, "issue_states", lambda: {})
    monkeypatch.setattr(watch_runs, "_starting", lambda: next(starting, []))
    monkeypatch.setattr(watch_runs, "wait", lambda: None)

    try:
        code = watch_runs.main([])
    except ValueError as raised:
        code = "ValueError: %s" % raised

    assert (code, capsys.readouterr().out) == (0, "exited 9 stale\n")


def test_2635_main_reports_a_conductor_exit_when_the_conductor_log_holds_a_result_record_then_blank_and_prose_lines(
        monkeypatch, capsys, tmp_path, watch_runs):
    status = watch_runs.status
    tdd = tmp_path / ".tdd" / "wt" / "9" / ".tdd"
    tdd.mkdir(parents=True)
    (tdd / "issue-9.md").write_text("# Plan for #9 — t\n")
    (tdd / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "9", "event": "launch"}) + "\n")
    (tdd / "conductor-9.log").write_text(
        json.dumps({"type": "system", "subtype": "init"}) + "\n"
        + json.dumps({"type": "result", "result": "done"}) + "\n"
        + "\n\nThe criterion does not hold yet\n\nSTATEMENT: prose\n")
    leaf_log = tdd / "develop-exhausted.log"
    leaf_log.write_text(json.dumps({"type": "system", "subtype": "init"}) + "\n")
    os.utime(leaf_log, (2_000_000_000, 2_000_000_000))
    starting = iter([["9"]])

    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")
    monkeypatch.setattr(status, "issue_states", lambda: {})
    monkeypatch.setattr(watch_runs, "_starting", lambda: next(starting, []))
    monkeypatch.setattr(watch_runs, "wait", lambda: None)

    try:
        code = watch_runs.main([])
    except ValueError as raised:
        code = "ValueError: %s" % raised

    assert (code, capsys.readouterr().out) == (0, "exited 9 stale\n")

def test_2635_main_reports_a_conductor_exit_when_the_conductor_log_holds_a_partial_first_line_before_its_result_record(
        monkeypatch, capsys, tmp_path, watch_runs):
    status = watch_runs.status
    tdd = tmp_path / ".tdd" / "wt" / "9" / ".tdd"
    tdd.mkdir(parents=True)
    (tdd / "issue-9.md").write_text("# Plan for #9 — t\n")
    (tdd / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "9", "event": "launch"}) + "\n")
    (tdd / "conductor-9.log").write_text(
        '{"type": "syst\n' + json.dumps({"type": "result", "result": "done"}) + "\n")
    leaf_log = tdd / "develop-exhausted.log"
    leaf_log.write_text(json.dumps({"type": "system", "subtype": "init"}) + "\n")
    os.utime(leaf_log, (2_000_000_000, 2_000_000_000))
    starting = iter([["9"]])

    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")
    monkeypatch.setattr(status, "issue_states", lambda: {})
    monkeypatch.setattr(watch_runs, "_starting", lambda: next(starting, []))
    monkeypatch.setattr(watch_runs, "wait", lambda: None)

    try:
        code = watch_runs.main([])
    except ValueError as raised:
        code = "ValueError: %s" % raised

    assert (code, capsys.readouterr().out) == (0, "exited 9 stale\n")
