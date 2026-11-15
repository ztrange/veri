"""Small cases for veri.status --report: a Running block's verdict counts."""
import importlib
import json
import os


def test_2750_report_running_block_shows_pass_and_reject_verdict_counts_from_verdict_events(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    started = "Mon Nov  2 10:00:00 2026"
    def verdict(n, v):
        return {"ts": 1793613600 + n, "awake": n, "event": "verdict", "step": "1", "phase": "verify-green", "verdict": v}
    events = [{"ts": 1793613600, "awake": 0, "event": "conductor-start", "pid": os.getpid(), "started": started},
              verdict(1, "PASS"), verdict(2, "REJECT"), verdict(3, "PASS"), verdict(4, "PASS")]
    (runs / "2750.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    fake_processes.answers({"ps ": (0, started + "\n", "")}, default=(0, "", ""))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    running = lines[lines.index("Running") + 1:lines.index("Queue")]
    assert (code, ["PASS 3" in x and "REJECT 1" in x for x in running if x.startswith("#2750")]) == (0, [True]), running
