"""Small cases for veri.status --report: Queue's ETAs as quartile ranges."""
import datetime
import importlib
import json
import subprocess


def test_2750_report_queue_etas_are_ranges_from_the_fastest_to_the_slowest_quartile_of_finished_runs(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    monkeypatch.setenv("VERI_LABEL", "agent-ok")
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    for n, hours in zip(range(11, 19), (1, 1, 1, 1, 4, 4, 4, 4)):
        wall = hours * 3600
        events = [{"ts": 1793613600, "awake": 0, "event": "conductor-start", "pid": 99999999, "started": "x"},
                  {"ts": 1793613600 + wall, "awake": wall, "event": "done", "pr": str(n)},
                  {"ts": 1793613700 + wall, "awake": wall + 100, "event": "merged"}]
        (runs / ("%d.jsonl" % n)).write_text("".join(json.dumps(e) + "\n" for e in events))
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    fetched = datetime.datetime.now(datetime.timezone.utc)
    issue = {"number": 1, "title": "t1", "state": "OPEN", "labels": [{"name": "agent-ok"}],
             "closedAt": None, "updatedAt": "2026-11-01T00:00:00Z", "links": [], "blockedBy": []}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": [issue]}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines[lines.index("Queue") + 1:lines.index("Waiting")]
    etas = [line for line in queue if "ETA" in line]
    assert (code, bool(etas), all("no rate yet" not in line and "1h" in line and "4h" in line for line in etas)) == (0, True, True), queue


def test_2750_report_queue_eta_range_scales_each_quartile_by_the_number_of_queued_issues(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    monkeypatch.setenv("VERI_LABEL", "agent-ok")
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    for n, hours in zip(range(11, 19), (1, 1, 1, 1, 4, 4, 4, 4)):
        wall = hours * 3600
        events = [{"ts": 1793613600, "awake": 0, "event": "conductor-start", "pid": 99999999, "started": "x"},
                  {"ts": 1793613600 + wall, "awake": wall, "event": "done", "pr": str(n)},
                  {"ts": 1793613700 + wall, "awake": wall + 100, "event": "merged"}]
        (runs / ("%d.jsonl" % n)).write_text("".join(json.dumps(e) + "\n" for e in events))
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    fetched = datetime.datetime.now(datetime.timezone.utc)
    issues = [{"number": n, "title": "t%d" % n, "state": "OPEN", "labels": [{"name": "agent-ok"}],
               "closedAt": None, "updatedAt": "2026-11-01T00:00:00Z", "links": [], "blockedBy": []}
              for n in (1, 2, 3)]
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": issues}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines[lines.index("Queue") + 1:lines.index("Waiting")]
    etas = [line for line in queue if "ETA" in line]
    assert (code, etas) == (0, ["ETA 3h 0m–12h 0m"]), queue


def test_2750_report_queue_eta_skips_journals_without_a_done_event_and_an_empty_queue_prints_no_eta(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    home = tmp_path / "home"
    monkeypatch.setenv("VERI_HOME", str(home))
    monkeypatch.setenv("VERI_LABEL", "agent-ok")
    runs = home / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    for n in (11, 12):
        events = [{"ts": 1793613600, "awake": 0, "event": "conductor-start", "pid": 99999999, "started": "x"},
                  {"ts": 1793617200, "awake": 3600, "event": "done", "pr": str(n)}]
        (runs / ("%d.jsonl" % n)).write_text("".join(json.dumps(e) + "\n" for e in events))
    (runs / "13.jsonl").write_text(json.dumps(
        {"ts": 1793613600, "awake": 0, "event": "conductor-start", "pid": 99999999, "started": "x"}) + "\n")
    done = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", lambda *a, **k: done)
    fetched = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    issue = {"number": 1, "title": "t1", "state": "OPEN", "labels": [{"name": "agent-ok"}],
             "closedAt": None, "updatedAt": "2026-11-01T00:00:00Z", "links": [], "blockedBy": []}
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"

    def queue_section(issues):
        cache.write_text(json.dumps({"cache_format": 2, "fetched_at": fetched, "issues": issues}))
        code, out, _ = run_cli(status, ["--report"])
        lines = [line.strip() for line in out.splitlines()]
        return code, [line for line in lines[lines.index("Queue") + 1:lines.index("Waiting")] if "ETA" in line]

    assert (queue_section([issue]), queue_section([])) == ((0, ["ETA no rate yet"]), (0, []))
