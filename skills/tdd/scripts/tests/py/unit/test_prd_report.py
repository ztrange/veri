"""Cases for veri/prd_report.py."""
import datetime
import importlib
import json
import re


def test_report_with_a_snapshot_states_the_snapshots_age_on_its_first_line(run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    issue_worktree = importlib.import_module("issue_worktree")
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
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


def test_report_prints_one_block_per_open_prd_ordered_by_prd_number(run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    issue_worktree = importlib.import_module("issue_worktree")
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
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


def test_report_solved_line_counts_closed_children_and_those_closed_in_the_last_7_days(run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    issue_worktree = importlib.import_module("issue_worktree")
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
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
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
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
    assert re.search(r"held by no lane\D*\b2\b", left[0], re.I), left


def test_report_left_line_counts_as_waiting_the_open_children_with_an_open_blocker_and_names_each_blocker(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
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
    assert re.search(r"held by no lane\D*\b4\b", left[0], re.I), left


def test_report_left_line_waiting_count_is_the_distinct_open_children_with_an_open_blocker(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
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
    assert re.search(r"held by no lane\D*\b5\b", left[0], re.I), left


def test_report_left_line_names_a_blocker_shared_by_several_waiting_children_once(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
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
    assert re.search(r"held by no lane\D*\b3\b", left[0], re.I), left


def test_report_left_line_counts_as_held_by_no_lane_the_open_children_with_no_opt_in_label_and_no_branch_on_origin(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(solvable_issues, "solvable", lambda label, priority="priority", repo=None: (0, []))
    branches = {"tdd/23": "tdd/23-has-a-branch"}
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: branches.get(n, ""))

    def issue(number, title, label=None):
        return {"number": number, "title": title, "state": "OPEN", "labels": [{"name": label}] if label else [],
                "closedAt": None, "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": [], "links": [],
                "wallSeconds": 0, "lane": None}

    issues = [issue(5, "PRD 014: reports", label="ready-for-agent:mu"),
              issue(22, "PRD 014: no label, no branch"),
              issue(23, "PRD 014: no label, but a branch on origin"),
              issue(24, "PRD 014: opted in", label="ready-for-agent:mu"),
              issue(99, "PRD 015: other prd head"),
              issue(100, "PRD 015: other no label, no branch"),
              issue(101, "PRD 015: another no label, no branch")]
    fetched = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": fetched, "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    lines = out.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("PRD 014"))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("PRD ")), len(lines))
    left = [line for line in lines[start:end] if line.lower().startswith("left")]
    assert code == 0
    assert len(left) == 1 and re.search(r"held by no lane\D*\b1\b", left[0], re.I), left



def test_report_eta_line_says_no_rate_yet_only_when_the_holding_lanes_have_fewer_than_three_issues_closed_in_the_last_7_days(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(solvable_issues, "solvable", lambda label, priority="priority", repo=None: (0, []))
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
    now = datetime.datetime.now(datetime.timezone.utc)

    def stamp(days):
        return (now - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def issue(number, title, state="OPEN", label=None, closed=None, lane=None):
        return {"number": number, "title": title, "state": state, "labels": [{"name": label}] if label else [],
                "closedAt": closed, "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": [], "links": [],
                "wallSeconds": 3600 if closed else 0, "lane": lane}

    issues = [issue(5, "PRD 014: reports"),
              issue(7, "PRD 014: open child", label="ready-for-agent:mu", lane="mu"),
              issue(20, "PRD 014: first closed", "CLOSED", closed=stamp(1), lane="mu"),
              issue(21, "PRD 014: second closed", "CLOSED", closed=stamp(2), lane="mu"),
              issue(22, "PRD 014: third closed", "CLOSED", closed=stamp(3), lane="mu"),
              issue(6, "PRD 015: other"),
              issue(8, "PRD 015: open child", label="ready-for-agent:zz", lane="zz"),
              issue(30, "PRD 015: first closed", "CLOSED", closed=stamp(1), lane="zz"),
              issue(31, "PRD 015: second closed", "CLOSED", closed=stamp(2), lane="zz"),
              issue(32, "PRD 015: closed too long ago", "CLOSED", closed=stamp(9), lane="zz")]
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": stamp(0), "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    lines = out.splitlines()
    first = next(i for i, line in enumerate(lines) if line.startswith("PRD 014"))
    second = next(i for i, line in enumerate(lines) if line.startswith("PRD 015"))
    eta_014 = [line for line in lines[first:second] if line.lower().startswith("eta")]
    eta_015 = [line for line in lines[second:] if line.lower().startswith("eta")]
    assert code == 0
    assert len(eta_014) == 1 and "no rate yet" not in eta_014[0], out
    assert len(eta_015) == 1 and "no rate yet" in eta_015[0], out


def test_report_eta_lower_bound_is_the_left_count_over_the_fastest_rate_so_it_changes_when_the_left_count_does(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(solvable_issues, "solvable", lambda label, priority="priority", repo=None: (0, []))
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
    now = datetime.datetime.now(datetime.timezone.utc)

    def stamp(days):
        return (now - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def issue(number, title, state="OPEN", closed=None, lane=None, wall=0):
        return {"number": number, "title": title, "state": state, "labels": [], "closedAt": closed,
                "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": [], "links": [],
                "wallSeconds": wall, "lane": lane}

    def eta_line(open_children):
        issues = [issue(5, "PRD 014: reports")]
        issues += [issue(10 + i, "PRD 014: open child %d" % i, lane="mu") for i in range(open_children)]
        issues += [issue(20 + i, "PRD 014: closed %d" % i, "CLOSED", closed=stamp(1 + i), lane="mu",
                         wall=3600 * (i + 1)) for i in range(4)]
        issues.append(issue(40, "unlaned closed", "CLOSED", closed=stamp(1), lane=None, wall=60))
        (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
            {"cache_format": 2, "fetched_at": stamp(0), "issues": issues}))
        code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)
        assert code == 0
        return [line for line in out.splitlines() if line.lower().startswith("eta")]

    two = eta_line(2)
    four = eta_line(4)

    assert len(two) == 1 and len(four) == 1, (two, four)
    assert "no rate yet" not in two[0] and re.search(r"\d", two[0]), two
    assert "no rate yet" not in four[0] and re.search(r"\d", four[0]), four
    assert two[0] != four[0], (two, four)


def test_report_eta_lower_bound_divides_the_left_count_by_the_highest_lane_rate_at_its_fastest_wall_quartile(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(solvable_issues, "solvable", lambda label, priority="priority", repo=None: (0, []))
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
    now = datetime.datetime.now(datetime.timezone.utc)
    closed_at = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def issue(number, title, state="OPEN", lane=None, wall=0):
        return {"number": number, "title": title, "state": state, "labels": [],
                "closedAt": closed_at if state == "CLOSED" else None,
                "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": [], "links": [],
                "wallSeconds": wall, "lane": lane}

    issues = [issue(5, "PRD 014: reports"),
              issue(10, "PRD 014: open a1", lane="a"), issue(11, "PRD 014: open a2", lane="a"),
              issue(12, "PRD 014: open b", lane="b")]
    issues += [issue(20 + i, "lane a closed %d" % i, "CLOSED", lane="a", wall=w)
               for i, w in enumerate([10000, 20000, 30000, 40000, 50000])]
    issues.append(issue(30, "lane b closed", "CLOSED", lane="b", wall=40000))
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    eta = [line for line in out.splitlines() if line.startswith("ETA")]
    assert code == 0
    assert len(eta) == 1 and eta[0].startswith("ETA: 0.93"), out


def test_report_eta_upper_bound_divides_the_left_count_by_the_lowest_lane_rate_at_its_slowest_wall_quartile_after_the_lower_bound(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(solvable_issues, "solvable", lambda label, priority="priority", repo=None: (0, []))
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
    now = datetime.datetime.now(datetime.timezone.utc)
    closed_at = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def issue(number, title, state="OPEN", lane=None, wall=0):
        return {"number": number, "title": title, "state": state, "labels": [],
                "closedAt": closed_at if state == "CLOSED" else None,
                "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": [], "links": [],
                "wallSeconds": wall, "lane": lane}

    issues = [issue(5, "PRD 014: reports"),
              issue(10, "PRD 014: open a1", lane="a"), issue(11, "PRD 014: open a2", lane="a"),
              issue(12, "PRD 014: open b", lane="b")]
    issues += [issue(20 + i, "lane a closed %d" % i, "CLOSED", lane="a", wall=w)
               for i, w in enumerate([10000, 20000, 30000, 40000, 40000])]
    issues.append(issue(30, "lane b closed", "CLOSED", lane="b", wall=40000))
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    eta = [line for line in out.splitlines() if line.startswith("ETA")]
    assert code == 0
    assert len(eta) == 1 and "0.93" in eta[0] and "1.85" in eta[0], out
    assert eta[0].index("0.93") < eta[0].index("1.85"), eta


def test_report_eta_upper_bound_uses_the_slowest_lane_at_its_slowest_wall_quartile_not_its_maximum_wall(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(solvable_issues, "solvable", lambda label, priority="priority", repo=None: (0, []))
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
    now = datetime.datetime.now(datetime.timezone.utc)
    closed_at = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def issue(number, title, state="OPEN", lane=None, wall=0):
        return {"number": number, "title": title, "state": state, "labels": [],
                "closedAt": closed_at if state == "CLOSED" else None,
                "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": [], "links": [],
                "wallSeconds": wall, "lane": lane}

    issues = [issue(5, "PRD 014: reports")]
    issues += [issue(10 + i, "PRD 014: open %d" % i, lane="abc"[i]) for i in range(3)]
    number = 20
    for lane, walls in (("a", [10000, 20000, 30000, 40000, 100000]),
                        ("b", [50000, 50000, 50000]),
                        ("c", [45000, 45000, 45000])):
        for w in walls:
            issues.append(issue(number, "closed %d" % number, "CLOSED", lane=lane, wall=w))
            number += 1
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    eta = [line for line in out.splitlines() if line.startswith("ETA")]
    assert code == 0
    assert eta == ["ETA: 0.93 to 2.31 days"], out


def test_report_eta_line_says_no_lane_no_eta_for_a_prd_whose_open_children_no_lane_holds(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(solvable_issues, "solvable", lambda label, priority="priority", repo=None: (0, []))
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
    now = datetime.datetime.now(datetime.timezone.utc)
    closed_at = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def issue(number, title, state="OPEN", lane=None, wall=0):
        return {"number": number, "title": title, "state": state, "labels": [],
                "closedAt": closed_at if state == "CLOSED" else None,
                "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": [], "links": [],
                "wallSeconds": wall, "lane": lane}

    issues = [issue(5, "PRD 014: reports"),
              issue(10, "PRD 014: open, no lane"), issue(11, "PRD 014: open, no lane either")]
    issues += [issue(20 + i, "lane a closed %d" % i, "CLOSED", lane="a", wall=3600) for i in range(4)]
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    eta = [line for line in out.splitlines() if line.startswith("ETA")]
    assert code == 0
    assert eta == ["ETA: no lane: no ETA"], out


def test_report_eta_upper_bound_is_the_slowest_blockedby_chain_over_the_slowest_lane_rate(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(solvable_issues, "solvable", lambda label, priority="priority", repo=None: (0, []))
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
    now = datetime.datetime.now(datetime.timezone.utc)
    closed_at = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def issue(number, title, state="OPEN", lane=None, wall=0, blocked_by=()):
        return {"number": number, "title": title, "state": state, "labels": [],
                "closedAt": closed_at if state == "CLOSED" else None,
                "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": list(blocked_by),
                "links": [], "wallSeconds": wall, "lane": lane}

    issues = [issue(5, "PRD 014: reports"),
              issue(10, "PRD 014: open child", lane="a", blocked_by=[40]),
              issue(40, "open middle of the chain", blocked_by=[41]),
              issue(41, "open head of the chain")]
    issues += [issue(20 + i, "lane a closed %d" % i, "CLOSED", lane="a", wall=8640) for i in range(4)]
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    eta = [line for line in out.splitlines() if line.startswith("ETA")]
    assert code == 0
    assert len(eta) == 1 and eta[0].endswith("to 0.30 days"), out


def test_report_eta_range_survives_an_open_child_blocked_by_a_closed_or_uncached_issue(
        run_cli, tmp_path, monkeypatch):
    prd_report = importlib.import_module("veri.prd_report")
    solvable_issues = importlib.import_module("solvable_issues")
    issue_worktree = importlib.import_module("issue_worktree")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(solvable_issues, "solvable", lambda label, priority="priority", repo=None: (0, []))
    monkeypatch.setattr(issue_worktree, "remote_issue_branch", lambda n: "")
    now = datetime.datetime.now(datetime.timezone.utc)
    closed_at = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def issue(number, title, state="OPEN", lane=None, wall=0, blocked_by=()):
        return {"number": number, "title": title, "state": state, "labels": [],
                "closedAt": closed_at if state == "CLOSED" else None,
                "updatedAt": "2026-11-01T10:00:00Z", "body": "", "blockedBy": list(blocked_by),
                "links": [], "wallSeconds": wall, "lane": lane}

    issues = [issue(5, "PRD 014: reports"),
              issue(10, "PRD 014: open child", lane="a", blocked_by=[30, 99]),
              issue(30, "closed blocker", "CLOSED", wall=8640)]
    issues += [issue(20 + i, "lane a closed %d" % i, "CLOSED", lane="a", wall=8640) for i in range(4)]
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(
        {"cache_format": 2, "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "issues": issues}))

    code, out, _ = run_cli(prd_report, ["--report"], cwd=tmp_path)

    eta = [line for line in out.splitlines() if line.startswith("ETA")]
    assert code == 0
    assert eta == ["ETA: 0.20 to 0.20 days"], out
