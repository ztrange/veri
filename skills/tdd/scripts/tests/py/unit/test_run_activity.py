"""Cases for veri.run_activity: a run's state and activity as plain values."""
import importlib
import json
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

STATES = {
    "done": ([LAUNCH, {"event": "done", "pr": "#12"}], "done"),
    "stopped": ([LAUNCH, {"event": "stop", "mode": "now"}], "stopped"),
    "bailed": ([LAUNCH, {"event": "bail", "phase": "red", "classification": "process"}], "bailed"),
    "refused": ([{"event": "preflight-refused", "check": "baseline red"}], "refused"),
    "stale": ([LAUNCH], "stale"),
}


@pytest.mark.parametrize("name", STATES)
def test_state_names_how_the_run_ended(tmp_path, name):
    run_activity = importlib.import_module("veri.run_activity")
    events, word = STATES[name]

    assert run_activity.state(str(_run(tmp_path, events))) == word


def test_state_is_running_while_a_conductor_is_live(tmp_path, monkeypatch):
    from conftest import live_conductor
    run_activity = importlib.import_module("veri.run_activity")
    run = _run(tmp_path, [LAUNCH])
    live_conductor(monkeypatch, run / ".tdd", 7)

    assert run_activity.state(str(run)) == "running"


def test_activity_carries_the_last_launch_the_attempts_and_the_end_mark(tmp_path):
    run_activity = importlib.import_module("veri.run_activity")
    run = _run(tmp_path, [LAUNCH, LAUNCH, {"event": "bail", "phase": "red", "classification": "process"}])

    a = run_activity.activity(str(run))

    assert (a.state, a.detail, a.phase, a.actor, a.leaf, a.attempts, a.bail_phase, a.classification) == (
        "bailed", "bailed red process", "red", "developer", "develop-red", 2, "red", "process")
    assert 99 <= a.elapsed_seconds < 130


def test_activity_of_a_done_run_names_the_pr(tmp_path):
    run_activity = importlib.import_module("veri.run_activity")
    a = run_activity.activity(str(_run(tmp_path, [LAUNCH, {"event": "done", "pr": "#12"}])))

    assert (a.state, a.detail, a.pr) == ("done", "done #12", "#12")


def test_a_closed_issue_overrides_the_state(tmp_path):
    run_activity = importlib.import_module("veri.run_activity")
    run = str(_run(tmp_path, [LAUNCH, {"event": "done", "pr": "#12"}]))

    a = run_activity.activity(run, closed=True)

    assert (a.state, a.detail) == ("closed", "closed")


def test_a_run_with_no_journal_reads_as_running_with_zero_cost(tmp_path):
    run_activity = importlib.import_module("veri.run_activity")
    run = tmp_path / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)

    a = run_activity.activity(str(run))

    assert (a.state, a.attempts, a.dollars, a.tokens, a.phase) == ("running", 0, 0, 0, "")
