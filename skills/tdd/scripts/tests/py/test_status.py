"""In-process cases for veri/status.py, the module status.sh is a shim over."""
import importlib
import json
import pathlib
import sys
import time

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def write_events(path, events):
    path.write_text("".join(json.dumps(event) + "\n" for event in events))


def test_run_activity_reports_the_last_launch_its_attempts_usage_and_state(tmp_path, monkeypatch):
    def ev(ts, phase, step, event, attempt, **rest):
        return {"ts": ts, "issue": "9", "actor": "developer", "phase": phase, "step": step,
                "event": event, "attempt": attempt, "skill_commit": "abc", **rest}

    events = tmp_path / "events.jsonl"
    write_events(events, [
        ev(9700, "red", "a cog exists", "launch", "1", name="develop-red"),
        ev(9750, "red", "a cog exists", "usage", "1", total_cost_usd="0.50",
           input_tokens="1000", output_tokens="200", cache_read_input_tokens="3000",
           cache_creation_input_tokens="500"),
        ev(9800, "green", "two cogs mesh", "launch", "1", name="develop-green"),
        ev(9850, "green", "two cogs mesh", "usage", "1", total_cost_usd="1.25",
           input_tokens="2000", output_tokens="300", cache_read_input_tokens="4000",
           cache_creation_input_tokens="0"),
        ev(9900, "green", "two cogs mesh", "launch", "2", name="develop-green"),
        ev(9950, "green", "two cogs mesh", "done", "2", pr="77"),
    ])
    monkeypatch.setattr(time, "time", lambda: 10000)
    monkeypatch.delenv("STATUS_JSON", raising=False)

    status = importlib.import_module("veri.status")
    line = status.run_activity(str(events), str(tmp_path / "conductor.pid"), 900)

    assert line == "green  developer  develop-green 100s  attempt 2  $1.75  11000 tokens  done 77"


def test_scope_totals_sums_attempts_outcomes_wall_and_dollars_over_the_runs(tmp_path, monkeypatch):
    def ev(ts, event, **rest):
        return {"ts": ts, "issue": "9", "actor": "developer", "phase": "red", "step": "a cog exists",
                "event": event, "attempt": "1", "skill_commit": "abc", **rest}

    finished, bailed = tmp_path / "finished.jsonl", tmp_path / "bailed.jsonl"
    write_events(finished, [
        ev(100, "launch", name="develop-red"),
        ev(200, "usage", total_cost_usd="0.50", input_tokens="10", output_tokens="2",
           cache_read_input_tokens="0", cache_creation_input_tokens="0"),
        ev(400, "done", pr="77"),
    ])
    write_events(bailed, [
        ev(1000, "launch", name="develop-red"),
        ev(1100, "usage", total_cost_usd="1.25", input_tokens="20", output_tokens="3",
           cache_read_input_tokens="0", cache_creation_input_tokens="0"),
        ev(1600, "bail", classification="process"),
    ])
    monkeypatch.delenv("STATUS_JSON", raising=False)

    status = importlib.import_module("veri.status")
    line = status.scope_totals("veri", "4", [str(finished), str(bailed)])

    assert line == "scope veri  attempted 2  done 1  bailed 1  wall 900s  $1.75  solvable 4"


def test_run_object_merges_the_ledger_fields_with_the_activity_object():
    activity = json.dumps({"phase": "green", "actor": "developer", "state": "running"})

    status = importlib.import_module("veri.status")
    obj = status.run_object("9", "a cog — meshes", "tdd/9-cog", "2 of 3", activity)

    assert obj == ('{"issue": "9", "title": "a cog \\u2014 meshes", "branch": "tdd/9-cog", '
                   '"step": "2 of 3", "phase": "green", "actor": "developer", "state": "running"}')
