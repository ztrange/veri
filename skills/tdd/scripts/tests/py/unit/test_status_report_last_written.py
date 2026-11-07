"""Small cases for veri.status --report: status-last records the report's time and queue counts."""
import calendar
import datetime
import importlib
import json
import subprocess
import time


def test_2750_report_writes_status_last_holding_the_report_time_and_its_queue_counts(tmp_path, monkeypatch, run_cli):
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
    before = time.time()

    code, _out, _ = run_cli(status, ["--report"])

    path = tmp_path / ".tdd" / "status-last"
    last = json.loads(path.read_text()) if path.exists() else None
    written = calendar.timegm(time.strptime(last["time"], "%Y-%m-%dT%H:%M:%SZ")) if last else None
    assert (code, last and last.get("queue"), written is not None and before - 2 <= written <= time.time() + 2) == (
        0, {"agent-ok": 2}, True), last
