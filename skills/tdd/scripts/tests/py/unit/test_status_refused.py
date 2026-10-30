"""Small cases for veri.status reading a preflight-refused end mark."""
import importlib
import json
import os
import time

import run_end


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


def test_2545_a_run_whose_ledger_vanishes_between_the_check_and_the_read_is_absent_not_a_crash(tmp_path, monkeypatch):
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    ledger = run / ".tdd" / "issue-7.md"
    ledger.write_text("# Plan for #7 — t\n")
    real_isfile = os.path.isfile

    def isfile_then_removal(path):
        found = real_isfile(path)
        if str(path) == str(ledger) and found:
            ledger.unlink()
        return found

    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")
    monkeypatch.setattr(os.path, "isfile", isfile_then_removal)

    try:
        code, _ = status.json_document(scope="", read_states=False)
    except FileNotFoundError:
        code = "FileNotFoundError"

    assert code in (0, 3)


def _unledgered_run(tmp_path, monkeypatch, status, issue, *events):
    run = tmp_path / ".tdd" / "wt" / issue
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "tdd/" + os.path.basename(run))
    monkeypatch.setattr(status, "solvable_count", lambda name: "0")
    return run


REFUSED = {"ts": 100, "issue": "7", "event": "preflight-refused", "check": "baseline",
           "cause": "preflight-refused", "classification": "system"}
PREFLIGHT = {"ts": int(time.time()), "issue": "8", "event": "skill-repin"}


def test_2700_a_refused_run_with_no_ledger_is_listed_in_text_and_json(tmp_path, monkeypatch, capsys):
    status = importlib.import_module("veri.status")
    _unledgered_run(tmp_path, monkeypatch, status, "7", REFUSED)

    assert status.render(False, "", read_states=False) == 0
    text = capsys.readouterr().out
    document = json.loads(status.json_document(scope="", read_states=False)[1])

    assert (text.startswith("#7  "), "refused baseline" in text) == (True, True)
    run = document["runs"][0]
    assert (run["issue"], run["state"], run["step"], run["title"]) == ("7", "refused", "", "")


def test_2700_a_run_in_preflight_with_a_live_conductor_and_no_ledger_is_listed_as_running(tmp_path, monkeypatch, capsys):
    status = importlib.import_module("veri.status")
    _unledgered_run(tmp_path, monkeypatch, status, "8", PREFLIGHT)
    monkeypatch.setattr(run_end, "live_conductor", lambda run: True)

    assert status.render(False, "", read_states=False) == 0
    text = capsys.readouterr().out
    document = json.loads(status.json_document(scope="", read_states=False)[1])

    assert (text.startswith("#8  "), text.rstrip().endswith("running")) == (True, True)
    run = document["runs"][0]
    assert (run["issue"], run["state"], run["step"], run["title"]) == ("8", "running", "", "")


def test_2700_a_run_with_an_empty_event_log_and_no_ledger_is_listed_without_a_crash(tmp_path, monkeypatch, capsys):
    status = importlib.import_module("veri.status")
    _unledgered_run(tmp_path, monkeypatch, status, "9")
    monkeypatch.setattr(run_end, "live_conductor", lambda run: True)

    document = json.loads(status.json_document(scope="", read_states=False)[1])

    assert [(run["issue"], run["state"]) for run in document["runs"]] == [("9", "running")]


def test_2700_the_scope_totals_count_exactly_the_runs_listed(tmp_path, monkeypatch, capsys):
    status = importlib.import_module("veri.status")
    _unledgered_run(tmp_path, monkeypatch, status, "7", REFUSED)
    ledgered = tmp_path / ".tdd" / "wt" / "5"
    (ledgered / ".tdd").mkdir(parents=True)
    (ledgered / ".tdd" / "issue-5.md").write_text("# Plan for #5 — t\n\n- [ ] a\n")
    (tmp_path / ".tdd" / "wt" / "6" / ".tdd").mkdir(parents=True)

    document = json.loads(status.json_document(scope="s", read_states=False)[1])

    assert (sorted(run["issue"] for run in document["runs"]), document["scope"]["attempted"]) == (["5", "7"], 2)
