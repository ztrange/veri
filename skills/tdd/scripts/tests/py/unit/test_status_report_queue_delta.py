"""Small cases for veri.status --report: Queue's counts carry their delta since status-last."""
import datetime
import importlib
import json
import subprocess


def test_2750_report_queue_count_carries_its_delta_against_the_counts_recorded_in_status_last(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    monkeypatch.setenv("VERI_LABEL", "agent-ok")
    fetched = datetime.datetime.now(datetime.timezone.utc)

    def issue(number):
        return {"number": number, "title": "t%d" % number, "state": "OPEN", "labels": [{"name": "agent-ok"}],
                "closedAt": None, "updatedAt": "2026-11-01T00:00:00Z", "links": [], "blockedBy": []}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"),
         "issues": [issue(1), issue(2)]}))
    (tmp_path / ".tdd" / "status-last").write_text(json.dumps(
        {"time": "2026-11-02T10:00:00Z", "queue": {"agent-ok": 1}}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines[lines.index("Queue") + 1:lines.index("Waiting")]
    assert (code, any(line.split()[:3] == ["2", "agent-ok", "+1"] for line in queue if line)) == (0, True), queue


def test_2750_report_queue_count_with_no_entry_in_status_last_prints_no_delta(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    monkeypatch.setenv("VERI_LABEL", "agent-ok")
    fetched = datetime.datetime.now(datetime.timezone.utc)
    issue = {"number": 1, "title": "t1", "state": "OPEN", "labels": [{"name": "agent-ok"}],
             "closedAt": None, "updatedAt": "2026-11-01T00:00:00Z", "links": [], "blockedBy": []}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": [issue]}))
    (tmp_path / ".tdd" / "status-last").write_text(json.dumps(
        {"time": "2026-11-02T10:00:00Z", "queue": {"other-label": 5}}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines[lines.index("Queue") + 1:lines.index("Waiting")]
    counts = [line.split() for line in queue if line.split()[:2] == ["1", "agent-ok"]]
    assert (code, counts) == (0, [["1", "agent-ok"]]), queue


def test_2750_report_queue_with_status_last_holding_no_queue_key_prints_no_delta_and_exits_0(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    monkeypatch.setenv("VERI_LABEL", "agent-ok")
    fetched = datetime.datetime.now(datetime.timezone.utc)
    issue = {"number": 1, "title": "t1", "state": "OPEN", "labels": [{"name": "agent-ok"}],
             "closedAt": None, "updatedAt": "2026-11-01T00:00:00Z", "links": [], "blockedBy": []}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": [issue]}))
    (tmp_path / ".tdd" / "status-last").write_text(json.dumps({"time": "2026-11-02T10:00:00Z"}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines[lines.index("Queue") + 1:lines.index("Waiting")]
    counts = [line.split() for line in queue if line.split()[:2] == ["1", "agent-ok"]]
    assert (code, counts) == (0, [["1", "agent-ok"]]), queue
