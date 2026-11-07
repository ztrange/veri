"""Small cases for veri.status --report: a Running block's refactor figures."""
import importlib
import json
import os
import subprocess


def test_3236_report_running_block_shows_no_refactor_text_when_the_journal_has_no_refactor_or_structural_pass_event(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    started = "Mon Nov  2 10:00:00 2026"
    events = [{"ts": 1793613600, "awake": 0, "event": "conductor-start", "pid": os.getpid(), "started": started},
              {"ts": 1793613601, "awake": 1, "event": "plan", "steps": 2},
              {"ts": 1793613602, "awake": 2, "event": "launch", "step": "1", "phase": "red", "actor": "developer",
               "name": "develop-red", "model": "sonnet"},
              {"ts": 1793613603, "awake": 3, "event": "verdict", "step": "1", "phase": "red", "verdict": "PASS"}]
    (runs / "3236.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    tags = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    ps = subprocess.CompletedProcess([], 0, stdout=started + "\n", stderr="")
    monkeypatch.setattr(status.subprocess, "run",
                        lambda cmd, *a, **k: ps if cmd and cmd[0] == "ps" else tags)

    code, out, err = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    running = lines[lines.index("Running") + 1:lines.index("Queue")]
    block = " ".join(x for x in running if x.startswith("#3236"))
    assert (code, bool(block), "refactor" in block) == (0, True, False), (running, err)
