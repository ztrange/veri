"""Small cases for veri.status --report: status-last records the report's time and queue counts."""
import calendar
import datetime
import importlib
import json
import os
import subprocess
import time


def test_2750_report_writes_status_last_holding_the_report_time_and_its_queue_counts(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    monkeypatch.setenv("VERI_LABEL", "agent-ok")
    fetched = datetime.datetime.now(datetime.timezone.utc)

    def issue(number):
        return {"number": number, "title": "t%d" % number, "state": "OPEN", "labels": [{"name": "agent-ok"}],
                "closedAt": None, "updatedAt": "2026-11-01T00:00:00Z", "links": [], "blockedBy": []}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"),
         "issues": [issue(1), issue(2)]}))
    before = time.time()

    code, _out, _ = run_cli(status, ["--report"])

    path = tmp_path / ".tdd" / "status-last"
    last = json.loads(path.read_text()) if path.exists() else None
    written = calendar.timegm(time.strptime(last["time"], "%Y-%m-%dT%H:%M:%SZ")) if last else None
    assert (code, last and last.get("queue"), written is not None and before - 2 <= written <= time.time() + 2) == (
        0, {"agent-ok": 2}, True), last


def test_2750_report_that_failed_to_print_leaves_status_last_as_it_was(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    monkeypatch.setenv("VERI_LABEL", "agent-ok")

    def broken():
        raise OSError("journal unreadable")
    monkeypatch.setattr(status, "waiting_lines", broken)
    (tmp_path / ".tdd").mkdir()
    path = tmp_path / ".tdd" / "status-last"
    previous = json.dumps({"time": "2026-11-01T00:00:00Z", "queue": {"agent-ok": 7}})
    path.write_text(previous)

    code, out, _ = run_cli(status, ["--report"])

    assert (code != 0, out, path.read_text()) == (True, "", previous)


def test_2750_report_starts_one_detached_refresh_when_the_snapshot_is_older_than_the_max_age(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    started = []

    class Detached:
        pass

    def spy(argv, *a, **k):
        started.append(list(argv))
        return Detached()
    monkeypatch.setattr(status.subprocess, "Popen", spy)
    monkeypatch.setenv("VERI_SNAPSHOT_MAX_AGE", "60")
    stale = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=600)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": stale.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": []}))

    code, _out, err = run_cli(status, ["--report"])

    shapes = [(a[0].rsplit("/", 1)[-1], a[1:]) for a in started if a]
    assert (code, shapes) == (0, [("report-cache.sh", ["refresh"])]), (started, err)


def test_2750_report_starts_no_refresh_when_the_snapshot_is_no_older_than_the_max_age(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    started = []

    class Detached:
        pass

    def spy(argv, *a, **k):
        started.append(list(argv))
        return Detached()
    monkeypatch.setattr(status.subprocess, "Popen", spy)
    monkeypatch.setenv("VERI_SNAPSHOT_MAX_AGE", "60")
    fresh = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=10)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fresh.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": []}))

    code, _out, err = run_cli(status, ["--report"])

    assert (code, started) == (0, []), (started, err)


def test_2750_report_starts_no_refresh_when_a_report_cache_refresh_is_already_running(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    started = []
    sibling = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(status.__file__))), "report-cache.sh")

    def fake_run(argv, *a, **k):
        name = os.path.basename(argv[0]) if argv else ""
        if name == "pgrep":
            return subprocess.CompletedProcess(argv, 0, stdout="4242\n", stderr="")
        if name == "ps":
            return subprocess.CompletedProcess(
                argv, 0, stdout="  PID COMMAND\n 4242 /bin/sh %s refresh\n" % sibling, stderr="")
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", fake_run)

    class Detached:
        pass

    def spy(argv, *a, **k):
        started.append(list(argv))
        return Detached()
    monkeypatch.setattr(status.subprocess, "Popen", spy)
    monkeypatch.setenv("VERI_SNAPSHOT_MAX_AGE", "60")
    stale = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=600)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": stale.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": []}))

    code, _out, err = run_cli(status, ["--report"])

    assert (code, started) == (0, []), (started, err)
