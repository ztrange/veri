"""Small cases for veri.status reading a preflight-refused end mark."""
import importlib
import json


def test_2481_a_run_ending_in_a_preflight_refused_event_with_no_launch_is_refused_with_its_check_in_text_and_json(tmp_path):
    status = importlib.import_module("veri.status")
    run = tmp_path / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "events.jsonl").write_text(json.dumps(
        {"ts": 100, "issue": "7", "event": "preflight-refused", "check": "full-tier baseline red",
         "cause": "preflight-refused", "classification": "system"}) + "\n")

    text = status.run_activity(str(run))
    obj = json.loads(status.run_activity(str(run), True) or "{}")

    assert ((text or "").endswith("  refused full-tier baseline red"), obj.get("state")) == (True, "refused")
