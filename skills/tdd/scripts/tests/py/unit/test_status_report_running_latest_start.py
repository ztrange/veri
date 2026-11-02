"""Small cases for veri.status --report: Running judges a run by its latest conductor-start."""
import importlib
import json
import os
import subprocess


def test_2750_report_running_omits_a_run_whose_latest_conductor_start_pid_is_dead_though_an_earlier_one_is_alive(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    started = "Mon Nov  2 10:00:00 2026"
    starts = [{"event": "conductor-start", "ts": "2026-11-02T10:00:00Z", "awake": 0,
               "pid": os.getpid(), "started": started},
              {"event": "conductor-start", "ts": "2026-11-02T11:00:00Z", "awake": 60,
               "pid": 2 ** 22 + 12345, "started": started}]
    (runs / "2750.jsonl").write_text("".join(json.dumps(e) + "\n" for e in starts))
    tags = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    ps = subprocess.CompletedProcess([], 0, stdout=started + "\n", stderr="")
    monkeypatch.setattr(status.subprocess, "run",
                        lambda cmd, *a, **k: ps if cmd and cmd[0] == "ps" else tags)

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    listed = [x for x in lines[lines.index("Running") + 1:lines.index("Queue")] if x.startswith("#")]
    assert (code, listed) == (0, []), listed


def test_2750_report_running_lists_a_live_run_whose_conductor_start_is_followed_by_other_events_and_a_blank_line(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    started = "Mon Nov  2 10:00:00 2026"
    events = [{"event": "conductor-start", "ts": "2026-11-02T10:00:00Z", "awake": 60,
               "pid": os.getpid(), "started": started},
              {"event": "step-start", "ts": "2026-11-02T10:05:00Z", "awake": 360}]
    text = json.dumps(events[0]) + "\n\n" + json.dumps(events[1]) + "\n\n"
    (runs / "2750.jsonl").write_text(text)
    tags = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    ps = subprocess.CompletedProcess([], 0, stdout=started + "\n", stderr="")
    monkeypatch.setattr(status.subprocess, "run",
                        lambda cmd, *a, **k: ps if cmd and cmd[0] == "ps" else tags)

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    running = lines[lines.index("Running") + 1:lines.index("Queue")]
    listed = [x.split()[0] for x in running if x.startswith("#") and "5m" in x.split()]
    assert (code, listed) == (0, ["#2750"]), listed
