"""Small cases for veri.status --report."""
import datetime
import importlib
import json


def test_2750_report_exits_0_and_prints_landed_running_queue_waiting_in_that_order(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))

    code, out, _ = run_cli(status, ["--report"])

    headings = [line.strip() for line in out.splitlines()
                if line.strip() in ("Landed", "Running", "Queue", "Waiting")]
    assert (code, headings) == (0, ["Landed", "Running", "Queue", "Waiting"])


def test_2750_report_without_snapshot_says_so_under_queue_and_still_prints_the_other_sections(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines.index("Queue")
    after_queue = [line for line in lines[queue + 1:] if line][:1]
    headings = [line for line in lines if line in ("Landed", "Running", "Queue", "Waiting")]
    assert (code, headings, "no snapshot" in " ".join(after_queue).lower()) == (
        0, ["Landed", "Running", "Queue", "Waiting"], True)


def test_2750_report_empty_landed_running_and_waiting_keep_their_heading_and_say_none(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    first_after = {h: ([x for x in lines[lines.index(h) + 1:] if x] or [""])[0]
                   for h in ("Landed", "Running", "Waiting")}
    assert (code, first_after) == (0, {"Landed": "none", "Running": "none", "Waiting": "none"})


def test_2750_report_with_a_snapshot_states_its_age_from_fetched_at_on_queues_first_line(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    fetched = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2, minutes=3)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": []}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    first = ([x for x in lines[lines.index("Queue") + 1:] if x] or [""])[0]
    assert (code, "2h" in first, "no snapshot" in first.lower()) == (0, True, False), first
