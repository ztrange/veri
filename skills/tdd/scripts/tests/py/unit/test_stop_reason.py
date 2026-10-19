"""Small cases for stop-reason.sh's report, driven in-process through run_cli."""
import importlib
import json


def test_a_run_whose_events_log_ends_with_a_done_event_prints_done_and_that_events_pr(tmp_path, run_cli):
    stop_reason = importlib.import_module("veri.stop_reason")
    events = tmp_path / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl"
    events.parent.mkdir(parents=True)
    events.write_text("".join(json.dumps(e) + "\n" for e in (
        {"ts": 100, "issue": "7", "event": "step-done"},
        {"ts": 200, "issue": "7", "event": "done", "pr": "https://github.com/o/r/pull/9"})))

    code, out, err = run_cli(stop_reason, ["7"], cwd=tmp_path)

    assert (code, out) == (0, "done https://github.com/o/r/pull/9\n")
