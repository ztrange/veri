"""Small cases for veri.status --report: the first line names the local zone once."""
import importlib
import subprocess
import time


def test_3059_report_first_line_names_the_local_zone_with_its_utc_offset(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    (tmp_path / "home" / "runs" / "acme-widgets").mkdir(parents=True)
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    monkeypatch.setenv("TZ", "America/Chicago")
    time.tzset()
    monkeypatch.setattr(status.time, "time", lambda: 1768435200)

    try:
        code, out, err = run_cli(status, ["--report"])
    finally:
        monkeypatch.undo()
        time.tzset()

    assert (code, out.splitlines()[0]) == (0, "CST (UTC−6)"), (out, err)


def test_3059_report_first_line_signs_a_zone_east_of_utc_with_plus(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    (tmp_path / "home" / "runs" / "acme-widgets").mkdir(parents=True)
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    monkeypatch.setenv("TZ", "Europe/Berlin")
    time.tzset()
    monkeypatch.setattr(status.time, "time", lambda: 1768435200)

    try:
        code, out, err = run_cli(status, ["--report"])
    finally:
        monkeypatch.undo()
        time.tzset()

    assert (code, out.splitlines()[0]) == (0, "CET (UTC+1)"), (out, err)


def test_3059_report_first_line_opens_with_the_window_from_status_last_in_the_local_zone(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    (tmp_path / "home" / "runs" / "acme-widgets").mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "status-last").write_text('{"time": "2026-01-14T22:30:00Z", "queue": {}}')
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    monkeypatch.setenv("TZ", "America/Chicago")
    time.tzset()
    monkeypatch.setattr(status.time, "time", lambda: 1768435200)

    try:
        code, out, err = run_cli(status, ["--report"])
    finally:
        monkeypatch.undo()
        time.tzset()

    assert (code, out.splitlines()[0]) == (0, "16:30 → 18:00 CST (UTC−6)"), (out, err)
