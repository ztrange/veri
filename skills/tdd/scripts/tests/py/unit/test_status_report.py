"""Small cases for veri.status --report."""
import datetime
import importlib
import json
import os
import subprocess


TAGS = (("v0.2", 1762000000, "Second capability"), ("v0.1", 1761000000, "First capability"))


def fake_tags(monkeypatch, status, tags=TAGS):
    def run(args, *a, **k):
        fmt = "".join(x for x in args if x.startswith("--format="))
        if not fmt:
            out = ""
        elif "creatordate" in fmt:
            out = "".join("%d %s\n" % (unix, name) for name, unix, _ in tags)
        else:
            out = "".join("%s  %s\n" % (name, subject) for name, _, subject in tags)
        return subprocess.CompletedProcess([], 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)


def landed(out):
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    return [tuple(line.split("  ", 1)) for line in lines[lines.index("Landed") + 1:lines.index("Running")]]


def test_2750_report_exits_0_and_prints_landed_running_queue_waiting_in_that_order(tmp_path, monkeypatch, run_cli):
    import re
    import time
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    tagger = datetime.timezone(datetime.timedelta(hours=9))
    tags = {"v0.2": (1768426200, "Second capability"), "v0.1": (1768339800, "First capability")}

    def expand(fmt, name):
        unix, subject = tags[name]

        def one(m):
            field = m.group(1)
            if field == "refname:short":
                return name
            if field == "contents:subject":
                return subject
            if field == "creatordate:unix":
                return str(unix)
            if field.startswith("creatordate:format-local:"):
                return time.strftime(field[len("creatordate:format-local:"):], time.localtime(unix))
            if field.startswith("creatordate:format:"):
                return datetime.datetime.fromtimestamp(unix, tagger).strftime(field[len("creatordate:format:"):])
            return datetime.datetime.fromtimestamp(unix, tagger).isoformat(" ")
        return re.sub(r"%\(([^)]*)\)", one, fmt)

    def run(args, *a, **k):
        fmt = "".join(x[len("--format="):] for x in args if x.startswith("--format="))
        out = "".join(expand(fmt, name) + "\n" for name in tags) if fmt else ""
        return subprocess.CompletedProcess([], 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)
    monkeypatch.setenv("TZ", "America/Chicago")
    time.tzset()

    try:
        code, out, _ = run_cli(status, ["--report"])
    finally:
        monkeypatch.undo()
        time.tzset()

    headings = [line.strip() for line in out.splitlines()
                if line.strip() in ("Landed", "Running", "Queue", "Waiting")]
    assert (code, headings, landed(out)) == (
        0, ["Landed", "Running", "Queue", "Waiting"],
        [("v0.2", "2026-01-14 15:30  Second capability"), ("v0.1", "2026-01-13 15:30  First capability")])


def test_2750_report_without_snapshot_says_so_under_queue_and_still_prints_the_other_sections(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    fake_tags(monkeypatch, status)

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines.index("Queue")
    after_queue = [line for line in lines[queue + 1:] if line][:1]
    headings = [line for line in lines if line in ("Landed", "Running", "Queue", "Waiting")]
    assert (code, headings, "no snapshot" in " ".join(after_queue).lower()) == (
        0, ["Landed", "Running", "Queue", "Waiting"], True)


def test_2750_report_empty_landed_running_and_waiting_keep_their_heading_and_say_none(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    fake_tags(monkeypatch, status, tags=())

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    first_after = {h: ([x for x in lines[lines.index(h) + 1:] if x] or [""])[0]
                   for h in ("Landed", "Running", "Waiting")}
    assert (code, first_after) == (0, {"Landed": "none", "Running": "none", "Waiting": "none"})


def test_2750_report_with_a_snapshot_states_its_age_from_fetched_at_on_queues_first_line(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    fake_tags(monkeypatch, status)
    tag_run = status.subprocess.run

    def run_refusing_gh(args, *a, **k):
        if os.path.basename(str(args[0])) == "gh":
            raise AssertionError("--report started gh: %s" % (args,))
        return tag_run(args, *a, **k)
    monkeypatch.setattr(status.subprocess, "run", run_refusing_gh)
    fetched = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2, minutes=3)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": []}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    first = ([x for x in lines[lines.index("Queue") + 1:] if x] or [""])[0]
    assert (code, "2h" in first, "no snapshot" in first.lower()) == (0, True, False), first


def test_2750_report_queue_counts_the_snapshots_open_opted_in_issues_by_label(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    fake_tags(monkeypatch, status)
    monkeypatch.setenv("VERI_LABEL", "agent-ok")
    fetched = datetime.datetime.now(datetime.timezone.utc)

    def issue(number, state, *labels):
        return {"number": number, "title": "t%d" % number, "state": state,
                "labels": [{"name": name} for name in labels], "closedAt": None,
                "updatedAt": "2026-11-01T00:00:00Z", "links": [], "blockedBy": []}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"),
         "issues": [issue(1, "OPEN", "agent-ok"), issue(2, "OPEN", "agent-ok", "bug"),
                    issue(3, "CLOSED", "agent-ok"), issue(4, "OPEN", "bug")]}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines[lines.index("Queue") + 1:lines.index("Waiting")]
    assert (code, any("2 agent-ok" in line for line in queue)) == (0, True), queue


def test_2750_report_with_gh_refusing_exits_0_and_prints_the_same_report_as_with_gh_available(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    fake_tags(monkeypatch, status)
    tag_run = status.subprocess.run

    def run_refusing_gh(args, *a, **k):
        if os.path.basename(str(args[0])) == "gh":
            raise AssertionError("--report started gh: %s" % (args,))
        return tag_run(args, *a, **k)
    monkeypatch.setattr(status.subprocess, "run", run_refusing_gh)
    fetched = datetime.datetime.now(datetime.timezone.utc)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": []}))

    def refusing(*args, **kwargs):
        raise status.github.NoAnswer("gh refused")
    monkeypatch.setattr(status.github, "gh_issue_list", lambda *a, **k: "[]")
    available = run_cli(status, ["--report"])
    (tmp_path / ".tdd" / "status-last").unlink()
    monkeypatch.setattr(status.github, "gh_issue_list", refusing)
    refused = run_cli(status, ["--report"])

    assert (refused[0], refused[1]) == (0, available[1])
