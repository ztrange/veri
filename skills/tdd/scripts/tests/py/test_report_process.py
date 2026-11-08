"""Cases for report.sh that start the real entry point."""
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("report.sh run as a real /bin/sh shim with no argument")
def test_no_argument_prints_the_usage_line_on_stderr_and_exits_2():
    ran = subprocess.run([str(SCRIPTS / "report.sh")], capture_output=True, text=True, stdin=subprocess.DEVNULL)

    assert ran.returncode == 2
    assert ran.stdout == ""
    assert "report.sh" in ran.stderr
    assert "--report" in ran.stderr


@pytest.mark.process("report.sh run as a real shim with a refusing gh on PATH, in a real git repository")
def test_report_with_gh_refusing_and_a_snapshot_present_exits_0_and_prints_the_report(tmp_path, monkeypatch):
    import datetime
    import json
    import os

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "gh").write_text("#!/bin/sh\necho 'gh: refused' >&2\nexit 1\n")
    (bin_dir / "gh").chmod(0o755)
    work = tmp_path / "work"
    (work / ".tdd").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=work, check=True, stdin=subprocess.DEVNULL)
    fetched = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3, minutes=10)

    def issue(number, title, state, labels):
        return {"number": number, "title": title, "state": state, "labels": [{"name": n} for n in labels],
                "closedAt": None, "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": [],
                "links": [], "wallSeconds": 0, "lane": None}

    issues = [issue(5, "PRD 014: reports", "OPEN", []), issue(6, "A step", "OPEN", ["ready-for-agent:mu"])]
    (work / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": issues}))
    (work / ".tdd" / "report-owed.json").write_text(json.dumps(
        {"014": {"updatedAt": "2026-11-01T10:00:00Z", "answer": {"count": 0, "sections": []}}}))
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    monkeypatch.delenv("VERI_GH_JSON", raising=False)

    ran = subprocess.run([str(SCRIPTS / "report.sh"), "--report"], cwd=work, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL)

    lines = ran.stdout.splitlines()
    assert ran.returncode == 0, ran.stderr
    assert lines[0] == "snapshot age: 3 hours"
    assert "PRD 014 (#5) — PRD 014: reports" in lines
    assert "owed: none" in lines
