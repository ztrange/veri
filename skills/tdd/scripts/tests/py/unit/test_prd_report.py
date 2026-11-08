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


def test_report_solved_line_counts_closed_children_and_those_closed_in_the_last_7_days(run_cli, tmp_path):
    prd_report = importlib.import_module("veri.prd_report")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    now = datetime.datetime.now(datetime.timezone.utc)

    def stamp(days):
        return (now - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def issue(number, title, state="CLOSED", closed=None, links=()):
        return {"number": number, "title": title, "state": state, "labels": [], "closedAt": closed,
                "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": [], "links": list(links),
                "wallSeconds": 0, "lane": None}

    issues = [issue(5, "PRD 014: reports", "OPEN", links=[40, 41]),
              issue(20, "PRD 014: recent child", closed=stamp(2)),
              issue(21, "PRD 014: old child", closed=stamp(20)),
              issue(22, "PRD 014: open child", "OPEN"),
              issue(40, "linked child", closed=stamp(1)),
              issue(41, "PRD 015: other prd", closed=stamp(1)),
              issue(42, "PRD 015: other prd child", closed=stamp(1))]
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": stamp(0), "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    solved = [line for line in out.splitlines() if "solved" in line.lower()]
    assert code == 0
    assert len(solved) == 1 and re.search(r"solved\D*3\D+2\b", solved[0], re.I), solved


def test_report_left_line_counts_as_solvable_now_the_open_children_the_opt_in_label_lists_within_its_own_prd_block(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    listed = {"ready-for-agent:mu": [22, 100, 101]}

    def solvable(label, priority="priority", repo=None):
        return 0, listed.get(label, [])

    monkeypatch.setattr(solvable_issues, "solvable", solvable)

    def issue(number, title, state="OPEN", label=None):
        return {"number": number, "title": title, "state": state, "labels": [{"name": label}] if label else [],
                "closedAt": None, "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": [], "links": [],
                "wallSeconds": 0, "lane": None}

    issues = [issue(5, "PRD 014: reports"),
              issue(22, "PRD 014: listed child", label="ready-for-agent:mu"),
              issue(23, "PRD 014: unlisted child", label="ready-for-agent:mu"),
              issue(24, "PRD 014: unlabelled child"),
              issue(99, "PRD 015: other prd child"),
              issue(100, "PRD 015: first listed", label="ready-for-agent:mu"),
              issue(101, "PRD 015: second listed", label="ready-for-agent:mu")]
    fetched = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched, "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    lines = out.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("PRD 014"))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("PRD ")), len(lines))
    left = [line for line in lines[start:end] if line.lower().startswith("left")]
    assert code == 0
    assert len(left) == 1 and re.search(r"solvable now\D*\b1\b", left[0], re.I), left


def test_report_left_line_counts_as_waiting_the_open_children_with_an_open_blocker_and_names_each_blocker(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(solvable_issues, "solvable", lambda label, priority="priority", repo=None: (0, []))

    def issue(number, title, state="OPEN", blocked=()):
        return {"number": number, "title": title, "state": state, "labels": [], "closedAt": None,
                "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": list(blocked), "links": [],
                "wallSeconds": 0, "lane": None}

    issues = [issue(5, "PRD 014: reports"),
              issue(22, "PRD 014: waits on an open blocker", blocked=[50]),
              issue(23, "PRD 014: blocker already closed", blocked=[51]),
              issue(24, "PRD 014: unblocked"),
              issue(50, "the open blocker"),
              issue(51, "the closed blocker", "CLOSED"),
              issue(99, "PRD 015: other prd head"),
              issue(100, "PRD 015: other child", blocked=[52]),
              issue(52, "another open blocker")]
    fetched = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched, "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    lines = out.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("PRD 014"))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("PRD ")), len(lines))
    left = [line for line in lines[start:end] if line.lower().startswith("left")]
    assert code == 0
    assert len(left) == 1 and re.search(r"waiting\D*\b1\b", left[0], re.I), left
    assert "#50" in left[0] and "#51" not in left[0] and "#52" not in left[0], left


def test_report_left_line_waiting_count_is_the_distinct_open_children_with_an_open_blocker(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(solvable_issues, "solvable", lambda label, priority="priority", repo=None: (0, []))

    def issue(number, title, blocked=()):
        return {"number": number, "title": title, "state": "OPEN", "labels": [], "closedAt": None,
                "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": list(blocked), "links": [],
                "wallSeconds": 0, "lane": None}

    issues = [issue(5, "PRD 014: reports"),
              issue(22, "PRD 014: first waiter", blocked=[50]),
              issue(23, "PRD 014: second waiter, same blocker", blocked=[50]),
              issue(24, "PRD 014: third waiter, two blockers", blocked=[50, 52]),
              issue(25, "PRD 014: unblocked"),
              issue(50, "shared blocker"),
              issue(52, "second blocker")]
    fetched = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched, "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    left = [line for line in out.splitlines() if line.lower().startswith("left")]
    assert code == 0
    assert len(left) == 1 and re.search(r"waiting\D*\b3\b", left[0], re.I), left
    assert "#50" in left[0] and "#52" in left[0], left


def test_report_left_line_names_a_blocker_shared_by_several_waiting_children_once(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(solvable_issues, "solvable", lambda label, priority="priority", repo=None: (0, []))

    def issue(number, title, blocked=()):
        return {"number": number, "title": title, "state": "OPEN", "labels": [], "closedAt": None,
                "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": list(blocked), "links": [],
                "wallSeconds": 0, "lane": None}

    issues = [issue(5, "PRD 014: reports"),
              issue(22, "PRD 014: first waiter", blocked=[50]),
              issue(23, "PRD 014: second waiter, same blocker", blocked=[50]),
              issue(50, "shared blocker")]
    fetched = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched, "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    left = [line for line in out.splitlines() if line.lower().startswith("left")]
    assert code == 0
    assert len(left) == 1 and left[0].count("#50") == 1, left
