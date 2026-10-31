"""Small cases for veri.status reading a preflight-refused end mark."""
import importlib
import json
import os


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


def test_2700_text_lists_a_run_with_events_but_no_ledger_whose_only_event_is_preflight_refused_as_its_issue_and_refused_check(tmp_path, monkeypatch, capsys):
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "events.jsonl").write_text(json.dumps(
        {"ts": 100, "issue": "7", "event": "preflight-refused", "check": "baseline",
         "cause": "preflight-refused", "classification": "system"}) + "\n")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")

    status.render(False, "", False)

    lines = capsys.readouterr().out.splitlines()
    assert [line for line in lines if line.startswith("#7") and line.endswith("refused baseline")] != []


def test_2700_text_lists_a_run_with_no_ledger_and_no_launch_or_end_mark_and_a_live_conductor_as_its_issue_and_running(tmp_path, monkeypatch, capsys):
    from conftest import live_conductor
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "events.jsonl").write_text(json.dumps(
        {"ts": 100, "issue": "7", "event": "preflight-start"}) + "\n")
    live_conductor(monkeypatch, run / ".tdd", 7)
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")

    status.render(False, "", False)

    lines = capsys.readouterr().out.splitlines()
    assert [line for line in lines if line.startswith("#7") and line.endswith("running")] != []


def test_2700_json_scope_totals_attempted_equals_the_runs_listed_when_a_ledgerless_run_has_an_empty_events_log_and_no_live_conductor(tmp_path, monkeypatch):
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "events.jsonl").write_text("")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")
    monkeypatch.setattr(status, "solvable_count", lambda name: "0")

    _, out = status.json_document(scope="s", read_states=False)

    document = json.loads(out)
    assert document["scope"]["attempted"] == len(document["runs"])


def test_2700_text_lists_a_run_with_no_ledger_and_a_live_conductor_whose_only_event_is_an_earlier_preflight_refused_as_running(tmp_path, monkeypatch, capsys):
    from conftest import live_conductor
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "events.jsonl").write_text(json.dumps(
        {"ts": 100, "issue": "7", "event": "preflight-refused", "check": "baseline",
         "cause": "preflight-refused", "classification": "system"}) + "\n")
    live_conductor(monkeypatch, run / ".tdd", 7)
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")

    status.render(False, "", False)

    lines = capsys.readouterr().out.splitlines()
    assert [line for line in lines if line.startswith("#7") and line.endswith("running")] != []


def test_2700_text_lists_a_run_with_no_ledger_and_no_launch_or_end_mark_and_no_live_conductor_as_its_issue_and_stale(tmp_path, monkeypatch, capsys):
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "events.jsonl").write_text(json.dumps(
        {"ts": 100, "issue": "7", "event": "preflight-start"}) + "\n")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")

    status.render(False, "", False)

    lines = capsys.readouterr().out.splitlines()
    assert [line for line in lines if line.startswith("#7") and line.endswith("stale")] != []


def test_2700_text_lists_a_run_with_no_ledger_an_empty_events_log_and_a_live_conductor_as_its_issue_and_running(tmp_path, monkeypatch, capsys):
    from conftest import live_conductor
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "events.jsonl").write_text("")
    live_conductor(monkeypatch, run / ".tdd", 7)
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")

    code = status.render(False, "", False)

    lines = capsys.readouterr().out.splitlines()
    assert (code, [line for line in lines if line.startswith("#7") and line.endswith("running")] != []) == (0, True)


def test_2700_json_lists_a_run_with_no_ledger_whose_only_event_is_preflight_refused_as_its_directory_name_refused_with_empty_step_and_title(tmp_path, monkeypatch):
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "events.jsonl").write_text(json.dumps(
        {"ts": 100, "issue": "7", "event": "preflight-refused", "check": "baseline",
         "cause": "preflight-refused", "classification": "system"}) + "\n")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")

    _, out = status.json_document(read_states=False)

    listed = [(r.get("issue"), r.get("state"), r.get("step"), r.get("title")) for r in json.loads(out)["runs"]]
    assert listed == [("7", "refused", "", "")]


def test_2700_json_lists_a_run_with_no_ledger_no_launch_or_end_mark_and_a_live_conductor_as_its_directory_name_running_with_empty_step_and_title(tmp_path, monkeypatch):
    from conftest import live_conductor
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "events.jsonl").write_text(json.dumps(
        {"ts": 100, "issue": "7", "event": "preflight-start"}) + "\n")
    live_conductor(monkeypatch, run / ".tdd", 7)
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")

    _, out = status.json_document(read_states=False)

    listed = [(r.get("issue"), r.get("state"), r.get("step"), r.get("title")) for r in json.loads(out)["runs"]]
    assert listed == [("7", "running", "", "")]


def test_2700_json_scope_totals_attempted_counts_a_ledgerless_refused_run_once_beside_a_ledger_run_and_both_are_listed(tmp_path, monkeypatch):
    status = importlib.import_module("veri.status")
    ledgered = tmp_path / ".tdd" / "wt" / "6"
    (ledgered / ".tdd").mkdir(parents=True)
    (ledgered / ".tdd" / "issue-6.md").write_text("# Plan for #6 — t\n")
    (ledgered / ".tdd" / "events.jsonl").write_text(json.dumps({"ts": 100, "issue": "6", "event": "launch"}) + "\n")
    refused = tmp_path / ".tdd" / "wt" / "7"
    (refused / ".tdd").mkdir(parents=True)
    (refused / ".tdd" / "events.jsonl").write_text(json.dumps(
        {"ts": 100, "issue": "7", "event": "preflight-refused", "check": "baseline",
         "cause": "preflight-refused", "classification": "system"}) + "\n")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")
    monkeypatch.setattr(status, "solvable_count", lambda name: "0")

    _, out = status.json_document(scope="s", read_states=False)

    document = json.loads(out)
    assert (len(document["runs"]), document["scope"]["attempted"]) == (2, 2)


def test_2700_json_scope_totals_attempted_counts_a_run_with_a_ledger_and_no_events_log_so_it_equals_the_runs_listed(tmp_path, monkeypatch):
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "issue-7.md").write_text("# Plan for #7 — t\n")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")
    monkeypatch.setattr(status, "solvable_count", lambda name: "0")

    _, out = status.json_document(scope="s", read_states=False)

    document = json.loads(out)
    assert (len(document["runs"]), document["scope"]["attempted"]) == (1, 1)


def test_2739_text_and_json_leave_unlisted_a_run_with_no_ledger_no_events_log_and_no_conductor_pid_or_a_dead_one(tmp_path, monkeypatch, capsys):
    status = importlib.import_module("veri.status")
    for issue in ("7", "8"):
        (tmp_path / ".tdd" / "wt" / issue / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "wt" / "8" / ".tdd" / "conductor.pid").write_text("99999999\n")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")

    status.render(False, "", False)
    text = capsys.readouterr().out
    _, out = status.json_document(read_states=False)

    assert (text.count("#7") + text.count("#8"), json.loads(out)["runs"]) == (0, [])


def test_2739_text_lists_a_run_with_a_live_conductor_no_ledger_and_no_events_log_as_its_issue_and_running(tmp_path, monkeypatch, capsys):
    from conftest import live_conductor
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    live_conductor(monkeypatch, run / ".tdd", 7)
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")

    code = status.render(False, "", False)

    lines = capsys.readouterr().out.splitlines()
    assert (code, [line for line in lines if line.startswith("#7") and line.endswith("running")] != []) == (0, True)


def test_2739_json_lists_a_run_with_a_live_conductor_no_ledger_and_no_events_log_as_its_directory_name_running_with_empty_step_and_title(tmp_path, monkeypatch):
    from conftest import live_conductor
    status = importlib.import_module("veri.status")
    run = tmp_path / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    live_conductor(monkeypatch, run / ".tdd", 7)
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(status, "branch_of", lambda run: "b")

    _, out = status.json_document(read_states=False)

    listed = [(r.get("issue"), r.get("state"), r.get("step"), r.get("title")) for r in json.loads(out)["runs"]]
    assert listed == [("7", "running", "", "")]
