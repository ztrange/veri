"""Small cases for veri.status --report: a Running block's model per role."""
import importlib
import json
import os
import subprocess


def test_2750_report_running_block_shows_the_model_each_role_ran_on_from_its_launch_events(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    started = "Mon Nov  2 10:00:00 2026"
    def launch(n, name, actor, model):
        return {"ts": 1793613600 + n, "awake": n, "event": "launch", "step": "1", "phase": "red", "actor": actor,
                "name": name, "model": model}
    events = [{"ts": 1793613600, "awake": 0, "event": "conductor-start", "pid": os.getpid(), "started": started},
              launch(1, "conductor-1", "conductor", "opus"),
              launch(2, "develop-red", "developer", "sonnet"),
              launch(3, "revise-red", "developer", "fable"),
              launch(4, "verify-red", "verifier", "haiku")]
    (runs / "2750.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    tags = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    ps = subprocess.CompletedProcess([], 0, stdout=started + "\n", stderr="")
    monkeypatch.setattr(status.subprocess, "run",
                        lambda cmd, *a, **k: ps if cmd and cmd[0] == "ps" else tags)

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    running = lines[lines.index("Running") + 1:lines.index("Queue")]
    block = " ".join(x for x in running if x.startswith("#2750"))
    wanted = ["developer sonnet", "revise fable", "verifier haiku", "conductor opus"]
    assert (code, [w for w in wanted if w not in block]) == (0, []), running


def test_2750_report_running_block_skips_a_launch_event_with_no_model_field(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    started = "Mon Nov  2 10:00:00 2026"
    def launch(n, name, actor, model=None):
        e = {"ts": 1793613600 + n, "awake": n, "event": "launch", "step": "1", "phase": "red", "actor": actor,
             "name": name}
        if model:
            e["model"] = model
        return e
    events = [{"ts": 1793613600, "awake": 0, "event": "conductor-start", "pid": os.getpid(), "started": started},
              launch(1, "develop-red", "developer", "sonnet"),
              launch(2, "verify-red", "verifier")]
    (runs / "2750.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    tags = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    ps = subprocess.CompletedProcess([], 0, stdout=started + "\n", stderr="")
    monkeypatch.setattr(status.subprocess, "run",
                        lambda cmd, *a, **k: ps if cmd and cmd[0] == "ps" else tags)

    code, out, err = run_cli(status, ["--report"])

    assert code == 0, err
    lines = [line.strip() for line in out.splitlines()]
    running = lines[lines.index("Running") + 1:lines.index("Queue")]
    block = " ".join(x for x in running if x.startswith("#2750"))
    assert (code, "developer sonnet" in block, "verifier" in block) == (0, True, False), (running, err)
