"""Small cases for veri.status --report: a Running block's cost."""
import importlib
import json
import os
import subprocess


def test_2750_report_running_block_shows_the_runs_cost_as_the_total_row_dollars_summed_from_usage_events(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    started = "Mon Nov  2 10:00:00 2026"
    def usage(n, dollars):
        return {"ts": 1793613600 + n, "awake": n, "event": "usage", "step": "1", "phase": "red", "actor": "developer",
                "total_cost_usd": dollars, "num_turns": 3}
    events = [{"ts": 1793613600, "awake": 0, "event": "conductor-start", "pid": os.getpid(), "started": started},
              usage(1, 0.5), usage(2, 0.25)]
    (runs / "2750.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    tags = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    ps = subprocess.CompletedProcess([], 0, stdout=started + "\n", stderr="")
    monkeypatch.setattr(status.subprocess, "run",
                        lambda cmd, *a, **k: ps if cmd and cmd[0] == "ps" else tags)

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    running = lines[lines.index("Running") + 1:lines.index("Queue")]
    assert (code, ["0.75" in x for x in running if x.startswith("#2750")]) == (0, [True]), running


def test_2750_report_running_block_labels_the_summed_dollars_with_the_total_row_label(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    started = "Mon Nov  2 10:00:00 2026"
    def usage(n, dollars):
        return {"ts": 1793613600 + n, "awake": n, "event": "usage", "step": "1", "phase": "red", "actor": "developer",
                "total_cost_usd": dollars, "num_turns": 3}
    events = [{"ts": 1793613600, "awake": 0, "event": "conductor-start", "pid": os.getpid(), "started": started},
              usage(1, 0.5), usage(2, 0.25)]
    (runs / "2750.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    tags = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    ps = subprocess.CompletedProcess([], 0, stdout=started + "\n", stderr="")
    monkeypatch.setattr(status.subprocess, "run",
                        lambda cmd, *a, **k: ps if cmd and cmd[0] == "ps" else tags)

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    running = lines[lines.index("Running") + 1:lines.index("Queue")]
    assert (code, ["| total | $0.75" in x for x in running if x.startswith("#2750")]) == (0, [True]), running
