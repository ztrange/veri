"""Small cases for stop-reason.sh's report, driven in-process through run_cli."""
import importlib
import json
import os


def test_a_run_whose_events_log_ends_with_a_done_event_prints_done_and_that_events_pr(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    events = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl"
    events.parent.mkdir(parents=True)
    events.write_text("".join(json.dumps(e) + "\n" for e in (
        {"ts": 100, "issue": "7", "event": "step-done"},
        {"ts": 200, "issue": "7", "event": "done", "pr": "https://github.com/o/r/pull/9"})))

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out) == (0, "done https://github.com/o/r/pull/9\n")


def test_a_run_whose_events_log_ends_with_a_bail_or_a_stop_event_prints_that_events_fields(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    for issue, last in (
            ("7", {"ts": 200, "issue": "7", "event": "bail", "phase": "red", "classification": "process"}),
            ("8", {"ts": 200, "issue": "8", "event": "stop", "mode": "graceful"})):
        events = tmp_path / ".tdd" / "wt" / issue / ".tdd" / "events.jsonl"
        events.parent.mkdir(parents=True)
        events.write_text("".join(json.dumps(e) + "\n" for e in (
            {"ts": 100, "issue": issue, "event": "step-done"}, last)))

    bailed = run_cli(stop_reason, ["7"], cwd=tmp_path)
    stopped = run_cli(stop_reason, ["8"], cwd=tmp_path)

    assert (bailed[0], bailed[1], stopped[0], stopped[1]) == (
        0, "bailed red process\n", 0, "stopped graceful\n")


def test_a_run_with_a_live_conductor_and_no_end_event_prints_running(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    run = tmp_path / ".tdd" / "wt" / "7" / ".tdd"
    run.mkdir(parents=True)
    (run / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "7", "event": "step-done"}) + "\n")
    (run / "conductor.pid").write_text("%d\n" % os.getpid())

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out) == (0, "running\n")
