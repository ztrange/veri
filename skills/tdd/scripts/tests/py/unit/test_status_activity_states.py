"""Characterization cases for status.run_activity: one per state, text and --json document."""
import importlib
import json
import re
import time

import pytest


def _run(tmp_path, events):
    run = tmp_path / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    now = int(time.time())
    (run / ".tdd" / "events.jsonl").write_text("".join(
        json.dumps({"ts": now - 100 + i, "issue": "7", **e}) + "\n" for i, e in enumerate(events)))
    return run


LAUNCH = {"event": "launch", "step": "1", "phase": "red", "actor": "developer", "name": "develop-red"}

CASES = {
    "done": ([LAUNCH, {"event": "done", "pr": "#12"}], "done #12", {"state": "done", "pr": "#12"}),
    "stopped": ([LAUNCH, {"event": "stop", "mode": "now"}], "stopped now", {"state": "stopped", "stop_mode": "now"}),
    "bailed": ([LAUNCH, {"event": "bail", "phase": "red", "classification": "process"}], "bailed red process",
               {"state": "bailed", "bail_phase": "red", "classification": "process"}),
    "refused": ([{"event": "preflight-refused", "check": "baseline red"}], "refused baseline red",
                {"state": "refused"}),
    "stale": ([LAUNCH], "stale", {"state": "stale", "cause": "unknown"}),
}


@pytest.mark.parametrize("name", CASES)
def test_a_run_ending_in_each_mark_reports_that_state_in_text_and_json(tmp_path, name):
    status = importlib.import_module("veri.status")
    events, tail, fields = CASES[name]
    run = _run(tmp_path, events)

    text = status.run_activity(str(run))
    obj = json.loads(status.run_activity(str(run), True))

    assert text.endswith("  " + tail), text
    assert {k: obj[k] for k in fields} == fields
    if name != "refused":
        assert re.match(r"red  developer  develop-red 1\d\d?s  attempt 1  \$0\.00  0 tokens  ", text), text


def test_a_run_with_a_live_conductor_and_no_end_mark_is_running(tmp_path, monkeypatch):
    from conftest import live_conductor
    status = importlib.import_module("veri.status")
    run = _run(tmp_path, [LAUNCH])
    live_conductor(monkeypatch, run / ".tdd", 7)

    obj = json.loads(status.run_activity(str(run), True))

    assert (obj["state"], obj["attempts"], obj["leaf"], obj["cause"]) == ("running", 1, "develop-red", "")
    assert status.run_activity(str(run)).endswith("  running")


def test_a_closed_issue_overrides_the_state_in_text_and_json(tmp_path):
    status = importlib.import_module("veri.status")
    run = _run(tmp_path, [LAUNCH, {"event": "done", "pr": "#12"}])

    assert status.run_activity(str(run), False, True).endswith("  closed")
    assert json.loads(status.run_activity(str(run), True, True))["state"] == "closed"


def test_a_second_launch_of_the_same_step_counts_attempts_and_a_new_step_resets_them(tmp_path):
    status = importlib.import_module("veri.status")
    run = _run(tmp_path, [LAUNCH, LAUNCH, {**LAUNCH, "step": "2"}, {**LAUNCH, "step": "2"}, {**LAUNCH, "step": "2"}])

    assert json.loads(status.run_activity(str(run), True))["attempts"] == 3
