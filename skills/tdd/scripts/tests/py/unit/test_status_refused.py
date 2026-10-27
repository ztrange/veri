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


def test_2545_a_run_whose_events_log_vanishes_between_the_check_and_the_read_is_absent_not_a_crash(tmp_path, monkeypatch):
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "issue-7.md").write_text("# Plan for #7 — t\n")
    (run / ".tdd" / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "7", "event": "launch"}) + "\n")
    real_read_events = status.read_events

    def read_after_removal(path, *args, **kwargs):
        (run / ".tdd" / "events.jsonl").unlink()
        return real_read_events(path, *args, **kwargs)

    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")
    monkeypatch.setattr(status, "read_events", read_after_removal)

    try:
        code, _ = status.json_document(scope="", read_states=False)
    except FileNotFoundError:
        code = "FileNotFoundError"

    assert code in (0, 3)
