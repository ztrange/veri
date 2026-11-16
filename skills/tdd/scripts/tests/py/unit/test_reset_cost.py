"""In-process cases for veri/reset_cost.py, the module behind reset-cost.sh."""
import importlib
import json
import time
from datetime import datetime, timezone

STAMP = "%Y-%m-%dT%H:%M:%S"
MODEL = "claude-opus-5-5"


def iso(stamp):
    """The UTC timestamp a transcript records for the local `stamp` the role state file writes."""
    moment = datetime.fromtimestamp(time.mktime(time.strptime(stamp, STAMP)), timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def request(msg_id, stamp, input_tokens=0, cache_read=0, cache_write=0, output=0):
    usage = {"input_tokens": input_tokens, "cache_read_input_tokens": cache_read,
             "cache_creation_input_tokens": cache_write, "output_tokens": output}
    return {"type": "assistant", "timestamp": iso(stamp),
            "message": {"id": msg_id, "model": MODEL, "usage": usage}}


def two_resets(tmp_path):
    """A dev session reset twice; at claude-opus-5-5's rates (input 4, cache read 0.2, cache write 5, output 20)
    the first reset costs 25510 + 2760 = 28270 input-token units and grows 2000 over 2 requests after its baseline,
    the second 22755 + 3655 = 26410 and grows 500 over 1."""
    transcript = tmp_path / "home" / "sess-9.jsonl"
    transcript.parent.mkdir(parents=True)
    records = [
        request("m0", "2026-11-13T09:59:00", input_tokens=10, cache_read=90000, output=100),
        request("m1", "2026-11-13T10:01:00", input_tokens=10, cache_write=20000, output=100),
        request("m2", "2026-11-13T10:05:30", input_tokens=10, cache_read=20000, cache_write=1000, output=100),
        request("m2", "2026-11-13T10:05:30", input_tokens=10, cache_read=20000, cache_write=1000, output=100),
        request("m3", "2026-11-13T10:30:00", input_tokens=10, cache_read=21010, cache_write=990, output=100),
        request("m4", "2026-11-13T11:00:00", input_tokens=10, cache_read=22010, cache_write=990, output=100),
        request("m5", "2026-11-13T12:01:00", input_tokens=5, cache_write=18000, output=50),
        request("m6", "2026-11-13T12:04:10", input_tokens=5, cache_read=18000, cache_write=2000, output=50),
        request("m7", "2026-11-13T12:30:00", input_tokens=5, cache_read=20000, cache_write=500, output=50),
    ]
    transcript.write_text("".join(json.dumps(r) + "\n" for r in records))
    state = tmp_path / ".tdd" / "role-dev.state"
    state.parent.mkdir()
    state.write_text(
        "n=2\n"
        "transcript=%s\n"
        "reset-at=2026-11-13T10:00:00\n"
        "recovered-at=2026-11-13T10:05:00\n"
        "session-id=sess-9\n"
        "reset-at=2026-11-13T12:00:00\n"
        "recovered-at=2026-11-13T12:04:00\n"
        "session-id=sess-9\n" % transcript)
    return transcript, state


def test_dev_prints_each_reset_with_its_local_time_its_fixed_cost_and_its_growth_per_request(tmp_path, monkeypatch, run_cli):
    reset_cost = importlib.import_module("veri.reset_cost")
    monkeypatch.setattr(reset_cost.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    two_resets(tmp_path)

    code, out, err = run_cli(reset_cost, ["dev"])

    assert (code, out.splitlines()[:2]) == (0, ["2026-11-13T10:00:00 K=28270 g=1000",
                                                "2026-11-13T12:00:00 K=26410 g=500"]), err


def restarted_conductor(tmp_path):
    """Run 7's conductor relaunched once at 10:30: its first request writes 40000 to the 1-hour cache
    (2 + 80000 + 500 + 50 = 80552 units) and its context then grows 2000 over 2 requests."""
    tdd = tmp_path / ".tdd"
    (tdd / "wt" / "7" / ".tdd").mkdir(parents=True)
    restart = int(time.mktime(time.strptime("2026-11-14T10:30:00", STAMP)))
    (tdd / "wt" / "7" / ".tdd" / "events.jsonl").write_text(
        json.dumps({"event": "conductor-restart", "ts": restart, "growth": 60000, "knob": 70000}) + "\n")
    hour = request("c3", "2026-11-14T10:30:20", input_tokens=2, cache_read=10000, cache_write=40000, output=10)
    hour["message"]["usage"]["cache_creation"] = {"ephemeral_1h_input_tokens": 40000, "ephemeral_5m_input_tokens": 0}
    records = [
        {"type": "system", "subtype": "init"},
        request("c1", "2026-11-14T10:00:00", input_tokens=2, cache_write=30000, output=10),
        request("c2", "2026-11-14T10:10:00", input_tokens=2, cache_read=30000, cache_write=5000, output=10),
        {"type": "system", "subtype": "init"},
        hour,
        request("c4", "2026-11-14T10:40:00", cache_read=51002),
        request("c5", "2026-11-14T10:50:00", cache_read=52002),
    ]
    (tdd / "conductor-7.log").write_text(
        "update-veri.sh: already current\n" + "".join(json.dumps(r) + "\n" for r in records))


def test_conductor_prints_each_restart_with_its_local_time_the_relaunch_first_request_price_and_its_growth_per_request(tmp_path, monkeypatch, run_cli):
    reset_cost = importlib.import_module("veri.reset_cost")
    monkeypatch.setattr(reset_cost.run_dir, "main_tree_from_files", lambda cwd: str(tmp_path))
    restarted_conductor(tmp_path)

    code, out, err = run_cli(reset_cost, ["conductor", "7"])

    assert (code, out.splitlines()[:1]) == (0, ["2026-11-14T10:30:00 K=80552 g=1000"]), err
