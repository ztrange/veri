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
