"""Small cases for veri.status --report: Queue's blocked issues."""
import datetime
import importlib
import json
import subprocess


TAGS = (("v0.2", 1762000000, "Second capability"), ("v0.1", 1761000000, "First capability"))


def fake_tags(monkeypatch, status, tags=TAGS):
    def run(args, *a, **k):
        fmt = [x for x in args if x.startswith("--format=")][0]
        if "creatordate" in fmt:
            out = "".join("%d %s\n" % (unix, name) for name, unix, _ in tags)
        else:
            out = "".join("%s  %s\n" % (name, subject) for name, _, subject in tags)
        return subprocess.CompletedProcess([], 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)


def test_2750_report_queue_lists_each_blocked_opted_in_issue_with_its_open_blocker(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    fake_tags(monkeypatch, status)
    monkeypatch.setenv("VERI_LABEL", "agent-ok")
    fetched = datetime.datetime.now(datetime.timezone.utc)

    def issue(number, state, blocked_by=()):
        return {"number": number, "title": "t%d" % number, "state": state,
                "labels": [{"name": "agent-ok"}], "closedAt": None,
                "updatedAt": "2026-11-01T00:00:00Z", "links": [], "blockedBy": list(blocked_by)}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"),
         "issues": [issue(5, "OPEN", [6]), issue(6, "OPEN"),
                    issue(7, "OPEN", [8]), issue(8, "CLOSED")]}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines[lines.index("Queue") + 1:lines.index("Waiting")]
    blocked = [line for line in queue if "#5" in line or "#7" in line]
    assert (code, len(blocked), "#6" in " ".join(blocked)) == (0, 1, True), queue


def test_2750_report_queue_omits_blocked_issues_that_are_closed_or_not_opted_in(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    fake_tags(monkeypatch, status)
    monkeypatch.setenv("VERI_LABEL", "agent-ok")
    fetched = datetime.datetime.now(datetime.timezone.utc)

    def issue(number, state, blocked_by=(), label="agent-ok"):
        return {"number": number, "title": "t%d" % number, "state": state,
                "labels": [{"name": label}], "closedAt": None,
                "updatedAt": "2026-11-01T00:00:00Z", "links": [], "blockedBy": list(blocked_by)}
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"),
         "issues": [issue(6, "OPEN"),
                    issue(5, "CLOSED", [6]),
                    issue(7, "OPEN", [6], label="other")]}))

    code, out, _ = run_cli(status, ["--report"])

    lines = [line.strip() for line in out.splitlines()]
    queue = lines[lines.index("Queue") + 1:lines.index("Waiting")]
    blocked = [line for line in queue if "blocked by" in line]
    assert (code, blocked) == (0, []), queue
