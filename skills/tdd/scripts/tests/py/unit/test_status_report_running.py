"""Small cases for veri.status --report: Running's live runs."""
import importlib
import json
import os
import subprocess


def test_2750_report_running_lists_a_block_for_each_journal_whose_conductor_start_pid_is_alive_with_matching_start(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    started = "Mon Nov  2 10:00:00 2026"

    def journal(number, pid):
        (runs / ("%d.jsonl" % number)).write_text(json.dumps(
            {"event": "conductor-start", "ts": "2026-11-02T10:00:00Z", "awake": 0,
             "pid": pid, "started": started}) + "\n")
    journal(2750, os.getpid())
    journal(2751, 2 ** 22 + 12345)
    tags = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    ps = subprocess.CompletedProcess([], 0, stdout=started + "\n", stderr="")
    monkeypatch.setattr(status.subprocess, "run",
                        lambda cmd, *a, **k: ps if cmd and cmd[0] == "ps" else tags)

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    running = lines[lines.index("Running") + 1:lines.index("Queue")]
    assert (code, [x for x in running if x.startswith("#")]) == (0, ["#2750"]), running


def test_2750_report_running_omits_a_journal_whose_conductor_start_pid_is_alive_but_started_at_another_time(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (runs / "2750.jsonl").write_text(json.dumps(
        {"event": "conductor-start", "ts": "2026-11-02T10:00:00Z", "awake": 0,
         "pid": os.getpid(), "started": "Mon Nov  2 10:00:00 2026"}) + "\n")
    tags = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    ps = subprocess.CompletedProcess([], 0, stdout="Tue Nov  3 09:30:00 2026\n", stderr="")
    monkeypatch.setattr(status.subprocess, "run",
                        lambda cmd, *a, **k: ps if cmd and cmd[0] == "ps" else tags)

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    running = lines[lines.index("Running") + 1:lines.index("Queue")]
    assert (code, [x for x in running if x.startswith("#")]) == (0, []), running
