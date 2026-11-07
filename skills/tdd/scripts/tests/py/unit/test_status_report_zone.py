"""Small cases for veri.status --report: the first line names the local zone once."""
import datetime
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


def test_3059_report_queue_snapshot_line_shows_fetched_at_in_the_local_zone(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_SNAPSHOT_MAX_AGE", "86400")
    (tmp_path / "home" / "runs" / "acme-widgets").mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text('{"fetched_at": "2026-01-14T21:52:00Z", "issues": []}')
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

    assert (code, "snapshot 2h 8m old, fetched 15:52" in out) == (0, True), (out, err)


def test_3059_report_landed_line_shows_the_tag_date_in_the_local_zone_not_the_taggers_offset(tmp_path, monkeypatch, run_cli):
    import re
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    unix = 1768426200
    tagger = datetime.timezone(datetime.timedelta(hours=9))

    def expand(fmt):
        def one(m):
            name = m.group(1)
            if name == "refname:short":
                return "v0.2"
            if name == "contents:subject":
                return "Second capability"
            if name == "creatordate:unix":
                return str(unix)
            if name.startswith("creatordate:format-local:"):
                return time.strftime(name[len("creatordate:format-local:"):], time.localtime(unix))
            if name.startswith("creatordate:format:"):
                return datetime.datetime.fromtimestamp(unix, tagger).strftime(name[len("creatordate:format:"):])
            return datetime.datetime.fromtimestamp(unix, tagger).isoformat(" ")
        return re.sub(r"%\(([^)]*)\)", one, fmt)

    def run(args, *a, **k):
        fmt = "".join(x[len("--format="):] for x in args if x.startswith("--format="))
        out = expand(fmt) + "\n" if fmt else ""
        return subprocess.CompletedProcess([], 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)
    monkeypatch.setenv("TZ", "America/Chicago")
    time.tzset()
    monkeypatch.setattr(status.time, "time", lambda: 1768435200)

    try:
        code, out, err = run_cli(status, ["--report"])
    finally:
        monkeypatch.undo()
        time.tzset()

    lines = [l.strip() for l in out.splitlines()]
    landed = lines[lines.index("Landed") + 1]
    assert (code, landed.split()) == (0, ["v0.2", "2026-01-14", "15:30", "Second", "capability"]), (out, err)


def test_3059_report_shows_the_zone_on_the_first_line_only_and_no_time_carries_its_own_zone(tmp_path, monkeypatch, run_cli):
    import re
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("VERI_SNAPSHOT_MAX_AGE", "86400")
    (tmp_path / "home" / "runs" / "acme-widgets").mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "status-last").write_text('{"time": "2026-01-14T22:30:00Z", "queue": {}}')
    (tmp_path / ".tdd" / "report-cache.json").write_text('{"fetched_at": "2026-01-14T21:52:00Z", "issues": []}')
    unix = 1768426200
    tagger = datetime.timezone(datetime.timedelta(hours=9))

    def expand(fmt):
        def one(m):
            name = m.group(1)
            if name == "refname:short":
                return "v0.2"
            if name == "contents:subject":
                return "Second capability"
            if name == "creatordate:unix":
                return str(unix)
            if name.startswith("creatordate:format-local:"):
                return time.strftime(name[len("creatordate:format-local:"):], time.localtime(unix))
            if name.startswith("creatordate:format:"):
                return datetime.datetime.fromtimestamp(unix, tagger).strftime(name[len("creatordate:format:"):])
            return datetime.datetime.fromtimestamp(unix, tagger).isoformat(" ")
        return re.sub(r"%\(([^)]*)\)", one, fmt)

    def run(args, *a, **k):
        fmt = "".join(x[len("--format="):] for x in args if x.startswith("--format="))
        out = expand(fmt) + "\n" if fmt else ""
        return subprocess.CompletedProcess([], 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)
    monkeypatch.setenv("TZ", "America/Chicago")
    time.tzset()
    monkeypatch.setattr(status.time, "time", lambda: 1768435200)

    try:
        code, out, err = run_cli(status, ["--report"])
    finally:
        monkeypatch.undo()
        time.tzset()

    lines = out.splitlines()
    zoned = [l for l in lines[1:] if re.search(r"CST|UTC|\d{2}:\d{2}(:\d{2})?\s*(Z\b|[+\-−]\d{2}:?\d{2}\b)", l)]
    assert (code, "CST (UTC−6)" in lines[0], zoned) == (0, True, []), (out, err)
