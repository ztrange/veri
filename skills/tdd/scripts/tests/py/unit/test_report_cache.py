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
