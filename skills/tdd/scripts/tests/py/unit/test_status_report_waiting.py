"""Small cases for veri.status --report: Waiting lists the bails since status-last."""
import importlib
import json
import subprocess


def test_2750_report_waiting_lists_each_bail_since_status_last_with_its_cause(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "status-last").write_text(json.dumps({"time": "2026-11-02T10:00:00Z", "queue": {}}))

    def journal(number, ts, cause):
        events = [{"ts": ts - 50, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"},
                  {"ts": ts, "awake": 50, "event": "bail", "cause": cause}]
        (runs / ("%d.jsonl" % number)).write_text("".join(json.dumps(e) + "\n" for e in events))
    journal(2750, 1793700000, "needs-user")
    journal(2751, 1793500000, "stuck")
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    waiting = lines[lines.index("Waiting") + 1:]
    assert (code, [l.split()[:2] for l in waiting if l]) == (0, [["#2750", "needs-user"]]), waiting


def test_2750_report_waiting_lists_every_bail_when_there_is_no_status_last(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()

    def journal(number, ts, cause):
        events = [{"ts": ts - 50, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"},
                  {"ts": ts, "awake": 50, "event": "bail", "cause": cause}]
        (runs / ("%d.jsonl" % number)).write_text("".join(json.dumps(e) + "\n" for e in events))
    journal(2750, 1793700000, "needs-user")
    journal(2751, 1793500000, "stuck")
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)

    code, out, err = run_cli(status, ["--report"])

    assert code == 0, err

    lines = [line.strip() for line in out.splitlines()]
    waiting = lines[lines.index("Waiting") + 1:]
    assert (code, [l.split()[:2] for l in waiting if l]) == (0, [["#2750", "needs-user"], ["#2751", "stuck"]]), waiting
