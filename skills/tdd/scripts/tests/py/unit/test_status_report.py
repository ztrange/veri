"""Small cases for veri.status --report."""
import datetime
import importlib
import json
import subprocess


def fake_tags(monkeypatch, status, stdout="v0.2 Second capability\nv0.1 First capability\n"):
    done = subprocess.CompletedProcess([], 0, stdout=stdout, stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)


def landed(out):
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    return lines[lines.index("Landed") + 1:lines.index("Running")]


def test_2750_report_exits_0_and_prints_landed_running_queue_waiting_in_that_order(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    fake_tags(monkeypatch, status)

    code, out, _ = run_cli(status, ["--report"])

    headings = [line.strip() for line in out.splitlines()
                if line.strip() in ("Landed", "Running", "Queue", "Waiting")]
    assert (code, headings, landed(out)) == (
        0, ["Landed", "Running", "Queue", "Waiting"], ["v0.2 Second capability", "v0.1 First capability"])


def test_2750_report_without_snapshot_says_so_under_queue_and_still_prints_the_other_sections(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    fake_tags(monkeypatch, status)

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
    fake_tags(monkeypatch, status, stdout="")

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    first_after = {h: ([x for x in lines[lines.index(h) + 1:] if x] or [""])[0]
                   for h in ("Landed", "Running", "Waiting")}
    assert (code, first_after) == (0, {"Landed": "none", "Running": "none", "Waiting": "none"})


def test_2750_report_with_a_snapshot_states_its_age_from_fetched_at_on_queues_first_line(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    fake_tags(monkeypatch, status)
    fetched = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2, minutes=3)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": []}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    first = ([x for x in lines[lines.index("Queue") + 1:] if x] or [""])[0]
    assert (code, "2h" in first, "no snapshot" in first.lower()) == (0, True, False), first


def test_2750_report_queue_counts_the_snapshots_open_opted_in_issues_by_label(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    fake_tags(monkeypatch, status)
    monkeypatch.setenv("VERI_LABEL", "agent-ok")
    fetched = datetime.datetime.now(datetime.timezone.utc)

    def issue(number, state, *labels):
        return {"number": number, "title": "t%d" % number, "state": state,
                "labels": [{"name": name} for name in labels], "closedAt": None,
                "updatedAt": "2026-11-01T00:00:00Z", "links": [], "blockedBy": []}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"),
         "issues": [issue(1, "OPEN", "agent-ok"), issue(2, "OPEN", "agent-ok", "bug"),
                    issue(3, "CLOSED", "agent-ok"), issue(4, "OPEN", "bug")]}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines[lines.index("Queue") + 1:lines.index("Waiting")]
    assert (code, any("2 agent-ok" in line for line in queue)) == (0, True), queue
