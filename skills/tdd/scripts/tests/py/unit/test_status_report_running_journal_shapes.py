"""Small cases for veri.status --report: Running reads journals as event.py writes them."""
import importlib
import json
import os
import subprocess


def _setup(tmp_path, monkeypatch, started):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    tags = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    ps = subprocess.CompletedProcess([], 0, stdout=started + "\n", stderr="")
    monkeypatch.setattr(status.subprocess, "run",
                        lambda cmd, *a, **k: ps if cmd and cmd[0] == "ps" else tags)
    return status, runs


def _write(path, events):
    path.write_text("".join(json.dumps(e) + "\n" for e in events))


def test_report_running_lists_a_live_run_whose_journal_stores_pid_and_cost_as_strings(tmp_path, monkeypatch, run_cli):
    started = "Mon Nov  2 10:00:00 2026"
    status, runs = _setup(tmp_path, monkeypatch, started)
    _write(runs / "2750.jsonl", [
        {"event": "conductor-start", "ts": 1793602103, "awake": 60,
         "pid": str(os.getpid()), "started": started},
        {"event": "usage", "ts": 1793602200, "awake": 240, "total_cost_usd": "0.5"},
        {"event": "usage", "ts": 1793602300, "awake": 240, "total_cost_usd": "0.25"}])

    code, out, err = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    listed = [x for x in lines[lines.index("Running") + 1:lines.index("Queue")] if x.startswith("#")]
    assert (code, [x.split()[0] for x in listed], ["$0.75" in x.split() for x in listed]) == (0, ["#2750"], [True]), (out, err)


def test_report_running_skips_a_journal_with_no_conductor_start_event(tmp_path, monkeypatch, run_cli):
    started = "Mon Nov  2 10:00:00 2026"
    status, runs = _setup(tmp_path, monkeypatch, started)
    _write(runs / "2750.jsonl", [{"event": "step-start", "ts": 1793602103, "awake": 60}])
    _write(runs / "2751.jsonl", [
        {"event": "conductor-start", "ts": 1793602103, "awake": 60,
         "pid": str(os.getpid()), "started": started}])

    code, out, err = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    listed = [x.split()[0] for x in lines[lines.index("Running") + 1:lines.index("Queue")] if x.startswith("#")]
    assert (code, listed) == (0, ["#2751"]), (out, err)
