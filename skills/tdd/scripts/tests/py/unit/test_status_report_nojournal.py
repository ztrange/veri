"""Small cases for veri.status --report: a live run with no journal is named in a note."""
import importlib
import json
import os
import subprocess


def test_2750_report_notes_a_live_conductor_pid_run_with_no_journal(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    (tmp_path / "home" / "runs" / "acme-widgets").mkdir(parents=True)
    live = tmp_path / ".tdd" / "wt" / "2760" / ".tdd"
    live.mkdir(parents=True)
    (live / "conductor.pid").write_text("%d\n" % os.getpid())
    dead = tmp_path / ".tdd" / "wt" / "2761" / ".tdd"
    dead.mkdir(parents=True)
    (dead / "conductor.pid").write_text("%d\n" % (2 ** 22 + 7))
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)

    code, out, err = run_cli(status, ["--report"])

    notes = [l.strip() for l in out.splitlines() if "journal" in l]
    assert (code, [("2760" in n, "2761" in n) for n in notes]) == (0, [(True, False)]), (out, err)


def test_2750_report_does_not_note_a_live_conductor_pid_run_that_has_a_journal(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    for n in ("2760", "2762"):
        live = tmp_path / ".tdd" / "wt" / n / ".tdd"
        live.mkdir(parents=True)
        (live / "conductor.pid").write_text("%d\n" % os.getpid())
    start = {"ts": 100, "issue": "2762", "event": "conductor-start", "pid": os.getpid(), "started": "x", "awake": 0}
    (runs / "2762.jsonl").write_text(json.dumps(start) + "\n")
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)

    code, out, err = run_cli(status, ["--report"])

    notes = [l.strip() for l in out.splitlines() if "journal" in l]
    assert (code, [("2760" in n, "2762" in n) for n in notes]) == (0, [(True, False)]), (out, err)
