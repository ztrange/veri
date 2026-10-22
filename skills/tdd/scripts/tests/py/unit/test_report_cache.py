"""Cases for veri/report_cache.py."""
import importlib

import pytest


def test_no_subcommand_or_an_unknown_one_exits_2_with_the_usage_on_stderr(run_cli):
    report_cache = importlib.import_module("veri.report_cache")

    results = [run_cli(report_cache, argv) for argv in ([], ["bogus"])]

    assert [(code, out) for code, out, _ in results] == [(2, ""), (2, "")]
    assert all(err.startswith("usage: report-cache.sh") for _, _, err in results)


def test_refresh_with_no_cache_writes_every_issue_open_and_closed_with_fetched_at_and_exits_0(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    issues = [
        {"number": 7, "title": "open one", "state": "OPEN", "labels": [{"name": "bug"}],
         "closedAt": None, "updatedAt": "2026-10-20T10:00:00Z"},
        {"number": 8, "title": "closed one", "state": "CLOSED", "labels": [],
         "closedAt": "2026-10-21T09:00:00Z", "updatedAt": "2026-10-21T09:00:00Z"},
    ]

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    cache = json.loads((tmp_path / ".tdd" / "report-cache.json").read_text())
    kept = {i["number"]: i for i in cache["issues"]}
    assert (code, sorted(kept), kept[8]["state"], kept[8]["closedAt"], kept[7]["title"], bool(cache["fetched_at"])) == (
        0, [7, 8], "CLOSED", "2026-10-21T09:00:00Z", "open one", True)


@pytest.mark.process("git worktree")
def test_refresh_from_a_linked_worktree_writes_the_cache_under_the_main_working_tree(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    real_run = subprocess.run
    main = tmp_path / "main"
    linked = tmp_path / "linked"
    main.mkdir()
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
    real_run(git + ["init", "-q"], cwd=main, check=True)
    real_run(git + ["commit", "-q", "--allow-empty", "-m", "base"], cwd=main, check=True)
    real_run(git + ["worktree", "add", "-q", "--detach", str(linked)], cwd=main, check=True)
    issues = [{"number": 7, "title": "open one", "state": "OPEN", "labels": [],
               "closedAt": None, "updatedAt": "2026-10-20T10:00:00Z"}]

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] == ["gh", "issue", "list"]:
            return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")
        return real_run(args, **kwargs)

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=linked)

    assert (code, (main / ".tdd" / "report-cache.json").is_file(), (linked / ".tdd" / "report-cache.json").exists()) == (0, True, False)


def test_refresh_carries_the_issue_numbers_under_each_blocked_by_section_empty_when_none(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    issues = [
        {"number": 7, "title": "blocked", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-20T10:00:00Z",
         "body": "## Problem\n\nSee #99.\n\n## Blocked by\n\n- #3\n- #5\n\n## Notes\n\n#42\n"},
        {"number": 8, "title": "free", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-20T11:00:00Z", "body": "## Problem\n\nx\n\n## Blocked by\n\nNone.\n"},
    ]

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    cache = json.loads((tmp_path / ".tdd" / "report-cache.json").read_text())
    blockers = {i["number"]: i.get("blockedBy") for i in cache["issues"]}
    assert (code, blockers) == (0, {7: [3, 5], 8: []})


def test_refresh_carries_the_wall_seconds_of_the_last_metrics_comment_null_with_a_null_lane_when_none(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    metrics = "### 📊 Metrics\n\nWall time for the issue: %d s, from the last `resume`.\n"
    issues = [
        {"number": 7, "title": "measured", "state": "CLOSED", "labels": [],
         "closedAt": "2026-10-21T09:00:00Z", "updatedAt": "2026-10-21T09:00:00Z",
         "comments": [{"body": metrics % 100}, {"body": "thanks"}, {"body": metrics % 250}]},
        {"number": 8, "title": "unmeasured", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-20T11:00:00Z", "comments": [{"body": "no report here"}]},
    ]

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    cache = json.loads((tmp_path / ".tdd" / "report-cache.json").read_text())
    walls = {i["number"]: (i.get("wallSeconds"), i.get("lane")) for i in cache["issues"]}
    assert (code, walls) == (0, {7: (250, None), 8: (None, None)})


def test_refresh_reads_the_wall_seconds_from_a_metrics_block_under_another_heading(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    done = "### ✅ Done\n\nMerged.\n\n### 📊 Metrics\n\nWall time for the issue: 321 s, from the last `resume`.\n"
    issues = [
        {"number": 7, "title": "done", "state": "CLOSED", "labels": [],
         "closedAt": "2026-10-21T09:00:00Z", "updatedAt": "2026-10-21T09:00:00Z",
         "comments": [{"body": done}]},
    ]

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    cache = json.loads((tmp_path / ".tdd" / "report-cache.json").read_text())
    walls = {i["number"]: i.get("wallSeconds") for i in cache["issues"]}
    assert (code, walls) == (0, {7: 321})


def test_refresh_with_a_cache_asks_only_for_issues_updated_since_fetched_at_and_merges_them_by_number(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    before = {"fetched_at": "2026-10-01T00:00:00Z", "issues": [
        {"number": 7, "title": "kept", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-09-30T10:00:00Z", "blockedBy": [], "wallSeconds": None, "lane": None},
        {"number": 8, "title": "stale", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-09-30T11:00:00Z", "blockedBy": [], "wallSeconds": None, "lane": None},
    ]}
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps(before))
    received = [
        {"number": 8, "title": "fresh", "state": "CLOSED", "labels": [],
         "closedAt": "2026-10-02T09:00:00Z", "updatedAt": "2026-10-02T09:00:00Z"},
        {"number": 9, "title": "new", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-03T09:00:00Z"},
    ]
    asked = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        asked.append([args[i + 1] for i, arg in enumerate(args) if arg == "--search"])
        return subprocess.CompletedProcess(args, 0, json.dumps(received), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    cache = json.loads((tmp_path / ".tdd" / "report-cache.json").read_text())
    titles = {i["number"]: i["title"] for i in cache["issues"]}
    assert (code, asked, titles, cache["fetched_at"] > before["fetched_at"]) == (
        0, [["updated:>=2026-10-01T00:00:00Z"]], {7: "kept", 8: "fresh", 9: "new"}, True)


def test_refresh_whose_gh_read_fails_exits_2_with_one_stderr_line_and_leaves_the_cache_byte_identical(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache_file = tmp_path / ".tdd" / "report-cache.json"
    cache_file.write_text(json.dumps({"fetched_at": "2026-10-01T00:00:00Z", "issues": [
        {"number": 7, "title": "kept", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-09-30T10:00:00Z", "blockedBy": [], "wallSeconds": None, "lane": None}]}))
    before = cache_file.read_bytes()

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        return subprocess.CompletedProcess(args, 1, "", "gh: HTTP 502")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, out, len(err.splitlines()), "HTTP 502" in err, cache_file.read_bytes() == before) == (2, "", 1, True, True)
