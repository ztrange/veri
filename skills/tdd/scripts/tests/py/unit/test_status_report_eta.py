"""Small cases for veri.status --report: Queue's ETAs with too few finished runs."""
import datetime
import importlib
import json
import subprocess


def test_2750_report_queue_etas_all_read_no_rate_yet_when_the_journals_hold_fewer_than_three_finished_runs(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    monkeypatch.setenv("VERI_LABEL", "agent-ok")
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    for n in (11, 12):
        events = [{"ts": 1793613600, "awake": 0, "event": "conductor-start", "pid": 99999999, "started": "x"},
                  {"ts": 1793617200, "awake": 3600, "event": "done", "pr": str(n)},
                  {"ts": 1793617300, "awake": 3700, "event": "merged"}]
        (runs / ("%d.jsonl" % n)).write_text("".join(json.dumps(e) + "\n" for e in events))
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    fetched = datetime.datetime.now(datetime.timezone.utc)
    issue = {"number": 1, "title": "t1", "state": "OPEN", "labels": [{"name": "agent-ok"}],
             "closedAt": None, "updatedAt": "2026-11-01T00:00:00Z", "links": [], "blockedBy": []}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": [issue]}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines[lines.index("Queue") + 1:lines.index("Waiting")]
    etas = [line for line in queue if "ETA" in line]
    assert (code, bool(etas), all("no rate yet" in line for line in etas)) == (0, True, True), queue
