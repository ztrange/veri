"""Cases for veri/prd_report.py."""
import datetime
import importlib
import json
import re


def test_report_with_a_snapshot_states_the_snapshots_age_on_its_first_line(run_cli, tmp_path):
    prd_report = importlib.import_module("veri.prd_report")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    fetched = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3, minutes=10)
    issue = {"number": 5, "title": "PRD 014: reports", "state": "OPEN", "labels": [], "closedAt": None,
             "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": [], "links": [], "wallSeconds": 0,
             "lane": None}
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": [issue]}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    first = out.splitlines()[0] if out else ""
    assert code == 0
    assert re.search(r"\b3 ?(h|hours?)\b", first), first


def test_report_without_a_snapshot_says_there_is_no_snapshot_and_exits_2(run_cli, tmp_path):
    prd_report = importlib.import_module("veri.prd_report")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()

    code, out, err = run_cli(prd_report, ["--report"], cwd=tmp_path)

    assert code == 2
    assert "no snapshot" in (out + err).lower()


def test_report_prints_one_block_per_open_prd_ordered_by_prd_number(run_cli, tmp_path):
    prd_report = importlib.import_module("veri.prd_report")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()

    def issue(number, title, state="OPEN"):
        return {"number": number, "title": title, "state": state, "labels": [], "closedAt": None,
                "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": [], "links": [],
                "wallSeconds": 0, "lane": None}

    fetched = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    issues = [issue(7, "PRD 020: later"), issue(30, "PRD 003: earlier"), issue(11, "PRD 009: done", "CLOSED"),
              issue(12, "Fix a bug")]
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched, "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    heads = [line for line in out.splitlines() if line.startswith("PRD ")]
    assert heads == ["PRD 003 (#30) — PRD 003: earlier", "PRD 020 (#7) — PRD 020: later"]
