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
    before = {"fetched_at": "2026-10-01T00:00:00Z", "cache_format": 2, "issues": [
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
        asked.append([term for i, arg in enumerate(args) if arg == "--search"
                      for term in args[i + 1].split() if term.startswith("updated:>=")])
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
    cache_file.write_text(json.dumps({"fetched_at": "2026-10-01T00:00:00Z", "cache_format": 2, "issues": [
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


def test_refresh_whose_gh_read_is_unparseable_exits_2_with_one_stderr_line_and_leaves_the_cache_byte_identical(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache_file = tmp_path / ".tdd" / "report-cache.json"
    cache_file.write_text(json.dumps({"fetched_at": "2026-10-01T00:00:00Z", "cache_format": 2, "issues": [
        {"number": 7, "title": "kept", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-09-30T10:00:00Z", "blockedBy": [], "wallSeconds": None, "lane": None}]}))
    before = cache_file.read_bytes()

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        return subprocess.CompletedProcess(args, 0, "<html>rate limited</html>", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, out, len(err.splitlines()), err.startswith("report-cache.sh:"), cache_file.read_bytes() == before) == (2, "", 1, True, True)


def test_refresh_reads_the_lane_line_of_the_last_metrics_comment_into_the_issue_lane(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    metrics = "### 📊 Metrics\n\nOutcome: merged.\nLane: %s\nWall time for the issue: 100 s, from the last `resume`.\n"
    issues = [
        {"number": 7, "title": "laned", "state": "CLOSED", "labels": [],
         "closedAt": "2026-10-21T09:00:00Z", "updatedAt": "2026-10-21T09:00:00Z",
         "comments": [{"body": metrics % "old-lane"}, {"body": "thanks"}, {"body": metrics % "fast-lane"}]},
    ]

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    cache = json.loads((tmp_path / ".tdd" / "report-cache.json").read_text())
    lanes = {i["number"]: i.get("lane") for i in cache["issues"]}
    assert (code, lanes) == (0, {7: "fast-lane"})


def test_refresh_reads_through_the_github_port_so_a_bad_gh_driver_exits_2_naming_it_with_no_gh_started(run_cli, monkeypatch, tmp_path):
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    started = []

    def fake_run(args, **kwargs):
        started.append([str(arg) for arg in args])
        return subprocess.CompletedProcess(args, 0, "[]", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setenv("VERI_GH_DRIVER", "bogus")

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, out, "VERI_GH_DRIVER" in err, started, (tmp_path / ".tdd" / "report-cache.json").exists()) == (
        2, "", True, [], False)


def test_refresh_whose_os_replace_raises_leaves_the_previous_cache_byte_identical_and_parseable_2160(run_cli, monkeypatch, tmp_path):
    import json
    import os
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_text(json.dumps({"fetched_at": "2026-10-20T00:00:00Z", "cache_format": 2, "issues": [
        {"number": 7, "title": "old", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-19T10:00:00Z", "blockedBy": [], "wallSeconds": None, "lane": None}]}))
    before = cache.read_bytes()
    issues = [{"number": 8, "title": "new", "state": "OPEN", "labels": [], "closedAt": None,
               "updatedAt": "2026-10-21T10:00:00Z"}]

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    def failing_replace(src, dst):
        raise OSError("interrupted before replace")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(os, "replace", failing_replace)

    try:
        run_cli(report_cache, ["refresh"], cwd=tmp_path)
    except OSError:
        pass

    after = cache.read_bytes()
    assert (after == before, json.loads(after)["issues"][0]["title"]) == (True, "old")


def test_refresh_that_succeeds_leaves_no_temp_file_in_tdd_beside_the_cache_2160(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps({"fetched_at": "2026-10-20T00:00:00Z", "cache_format": 2, "issues": []}))
    issues = [{"number": 8, "title": "new", "state": "OPEN", "labels": [], "closedAt": None,
               "updatedAt": "2026-10-21T10:00:00Z"}]

    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess([str(arg) for arg in args], 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, sorted(p.name for p in (tmp_path / ".tdd").iterdir())) == (0, ["report-cache.json"])


def test_refresh_with_a_stray_temp_file_left_in_tdd_exits_0_and_writes_a_complete_cache_2160(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json.tmp").write_text('{"fetched_at": "2026-10-2')
    issues = [{"number": 8, "title": "new", "state": "OPEN", "labels": [], "closedAt": None,
               "updatedAt": "2026-10-21T10:00:00Z"}]

    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess([str(arg) for arg in args], 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    written = json.loads((tmp_path / ".tdd" / "report-cache.json").read_text())
    assert (code, [i["number"] for i in written["issues"]]) == (0, [8])


def test_refresh_with_a_truncated_cache_names_it_on_stderr_rebuilds_with_a_full_fetch_and_exits_0_2160(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_text('{"fetched_at": "2026-10-20T00:00:00Z", "issues": [{"number": 7, "tit')
    issues = [{"number": 8, "title": "new", "state": "OPEN", "labels": [], "closedAt": None,
               "updatedAt": "2026-10-21T10:00:00Z"}]
    searched = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        searched.append("updated:>=" in " ".join(args))
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, "report-cache.json" in err and "rebuilding" in err, searched) == (0, True, [False])
    assert [i["number"] for i in json.loads(cache.read_text())["issues"]] == [8]


def test_refresh_with_a_cache_lacking_fetched_at_names_it_on_stderr_rebuilds_with_a_full_fetch_and_exits_0_2160(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_text(json.dumps({"issues": [{"number": 7, "title": "old", "state": "OPEN"}]}))
    issues = [{"number": 8, "title": "new", "state": "OPEN", "labels": [], "closedAt": None,
               "updatedAt": "2026-10-21T10:00:00Z"}]
    searched = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        searched.append("updated:>=" in " ".join(args))
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, "report-cache.json" in err and "rebuilding" in err, searched) == (0, True, [False])
    written = json.loads(cache.read_text())
    assert ("fetched_at" in written, [i["number"] for i in written["issues"]]) == (True, [8])


def test_refresh_with_a_cache_lacking_issues_names_it_on_stderr_rebuilds_with_a_full_fetch_and_exits_0_2160(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_text(json.dumps({"fetched_at": "2026-10-20T00:00:00Z"}))
    issues = [{"number": 8, "title": "new", "state": "OPEN", "labels": [], "closedAt": None,
               "updatedAt": "2026-10-21T10:00:00Z"}]
    searched = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        searched.append("updated:>=" in " ".join(args))
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, "report-cache.json" in err and "rebuilding" in err, searched) == (0, True, [False])
    written = json.loads(cache.read_text())
    assert ("fetched_at" in written, [i["number"] for i in written["issues"]]) == (True, [8])


def test_refresh_with_a_cache_that_is_a_json_list_names_it_on_stderr_rebuilds_with_a_full_fetch_and_exits_0_2160(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_text(json.dumps([{"number": 1}]))
    issues = [{"number": 8, "title": "new", "state": "OPEN", "labels": [], "closedAt": None,
               "updatedAt": "2026-10-21T10:00:00Z"}]
    searched = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        searched.append("updated:>=" in " ".join(args))
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, "report-cache.json" in err and "rebuilding" in err, searched) == (0, True, [False])
    written = json.loads(cache.read_text())
    assert ("fetched_at" in written, [i["number"] for i in written["issues"]]) == (True, [8])


def test_refresh_with_a_cache_that_is_a_json_null_names_it_on_stderr_rebuilds_with_a_full_fetch_and_exits_0_2160(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_text("null")
    issues = [{"number": 8, "title": "new", "state": "OPEN", "labels": [], "closedAt": None,
               "updatedAt": "2026-10-21T10:00:00Z"}]
    searched = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        searched.append("updated:>=" in " ".join(args))
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, "report-cache.json" in err and "rebuilding" in err, searched) == (0, True, [False])
    written = json.loads(cache.read_text())
    assert ("fetched_at" in written, [i["number"] for i in written["issues"]]) == (True, [8])


def test_refresh_with_a_corrupt_cache_and_a_failing_gh_issue_list_exits_2_with_the_gh_message_and_leaves_the_corrupt_file_byte_identical_2160(run_cli, monkeypatch, tmp_path):
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_text('{"fetched_at": "2026-10-01T00:00:00Z", "issues": [{"numb')
    before = cache.read_bytes()

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        return subprocess.CompletedProcess(args, 1, "", "gh: HTTP 502")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, out, "gh issue list failed" in err, "HTTP 502" in err, cache.read_bytes() == before) == (2, "", True, True, True)


def test_refresh_with_a_well_formed_cache_searches_updated_since_fetched_at_and_writes_nothing_to_stderr_2160(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_text(json.dumps({"fetched_at": "2026-10-01T00:00:00Z", "cache_format": 2, "issues": [
        {"number": 7, "title": "old", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-09-30T10:00:00Z", "blockedBy": [], "wallSeconds": None, "lane": None}]}))
    calls = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "[]", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    searches = [t for c in calls if "--search" in c for t in c[c.index("--search") + 1].split()
                if t.startswith("updated:>=")]
    assert (code, err, searches) == (0, "", ["updated:>=2026-10-01T00:00:00Z"])


def test_two_refreshes_interleaved_mid_write_leave_a_cache_that_parses_whole_from_one_writer_2160(run_cli, monkeypatch, tmp_path):
    import json
    import os
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    answers = {
        "A": [{"number": 7, "title": "from writer A", "state": "OPEN", "labels": [], "closedAt": None,
               "updatedAt": "2026-10-21T10:00:00Z"}],
        "B": [{"number": n, "title": "from writer B, a longer answer", "state": "OPEN", "labels": [],
               "closedAt": None, "updatedAt": "2026-10-21T11:00:00Z"} for n in (8, 9)],
    }
    writer = ["A"]
    b_code = []
    b_replaces = []
    real_dump, real_replace = json.dump, os.replace

    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess([str(arg) for arg in args], 0, json.dumps(answers[writer[-1]]), "")

    def interleaving_dump(obj, out, **kwargs):
        if writer[-1] == "B":
            return real_dump(obj, out, **kwargs)
        text = json.dumps(obj, **kwargs)
        out.write(text[: len(text) // 2])
        out.flush()
        writer.append("B")
        try:
            b_code.append(report_cache.main(["refresh"]))
        finally:
            writer.pop()
        out.write(text[len(text) // 2:])

    def deferring_replace(src, dst):
        if writer[-1] == "B":
            b_replaces.append((src, dst))
            return None
        return real_replace(src, dst)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(json, "dump", interleaving_dump)
    monkeypatch.setattr(os, "replace", deferring_replace)

    a_code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)
    b_lost = None
    for src, dst in b_replaces:
        try:
            real_replace(src, dst)
        except OSError as failure:
            b_lost = failure

    titles = {i["title"] for i in json.loads(cache.read_text())["issues"]}
    assert (a_code, b_code, b_lost, titles in ({"from writer A"}, {"from writer B, a longer answer"})) == (0, [0], None, True)


def test_refresh_with_a_cache_that_is_not_utf8_names_it_on_stderr_rebuilds_with_a_full_fetch_and_exits_0_2160(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_bytes(b'{"fetched_at": "\xff\xfe\x80", "issues": []}')
    issues = [{"number": 8, "title": "new", "state": "OPEN", "labels": [], "closedAt": None,
               "updatedAt": "2026-10-21T10:00:00Z"}]
    searched = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        searched.append("updated:>=" in " ".join(args))
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, "report-cache.json" in err and "rebuilding" in err, searched) == (0, True, [False])
    assert [i["number"] for i in json.loads(cache.read_text())["issues"]] == [8]


def test_refresh_with_a_cache_whose_fetched_at_is_not_a_string_names_it_on_stderr_rebuilds_with_a_full_fetch_and_exits_0_2160(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_text(json.dumps({"fetched_at": 5, "issues": [{"number": 7, "title": "old", "state": "OPEN"}]}))
    issues = [{"number": 8, "title": "new", "state": "OPEN", "labels": [], "closedAt": None,
               "updatedAt": "2026-10-21T10:00:00Z"}]
    searched = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        searched.append("updated:>=" in " ".join(args))
        return subprocess.CompletedProcess(args, 0, json.dumps(issues), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, "report-cache.json" in err and "rebuilding" in err, searched) == (0, True, [False])
    assert [i["number"] for i in json.loads(cache.read_text())["issues"]] == [8]


def test_refresh_whose_os_replace_raises_removes_its_own_temp_file_2160(run_cli, monkeypatch, tmp_path):
    import json
    import os
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "report-cache.json").write_text(json.dumps({"fetched_at": "2026-10-20T00:00:00Z", "cache_format": 2, "issues": []}))

    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess([str(arg) for arg in args], 0, "[]", "")

    def failing_replace(src, dst):
        raise OSError("interrupted before replace")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(os, "replace", failing_replace)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, "interrupted before replace" in err, sorted(p.name for p in (tmp_path / ".tdd").iterdir())) == (
        2, True, ["report-cache.json"])


def test_refresh_with_no_cache_fetches_in_bounded_pages_and_merges_them_into_the_cache_a_single_answer_would_give_2244(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    everything = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-%02dT%02d:00:00Z" % (1 + n // 24, n % 24)}
        for n in range(1, 251)
    ]
    limits = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        limit = int(args[args.index("--limit") + 1])
        limits.append(limit)
        if limit > 100:
            return subprocess.CompletedProcess(args, 1, "", "HTTP 504: 504 Gateway Timeout (https://api.github.com/graphql)")
        pool = sorted(everything, key=lambda i: i["updatedAt"], reverse=True)
        search = args[args.index("--search") + 1] if "--search" in args else ""
        for bound in search.split():
            if bound.startswith("updated:<="):
                pool = [i for i in pool if i["updatedAt"] <= bound[len("updated:<="):]]
            elif bound.startswith("updated:<"):
                pool = [i for i in pool if i["updatedAt"] < bound[len("updated:<"):]]
        return subprocess.CompletedProcess(args, 0, json.dumps(pool[:limit]), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    written = tmp_path / ".tdd" / "report-cache.json"
    kept = sorted(i["number"] for i in json.loads(written.read_text())["issues"]) if written.exists() else []
    assert (code, kept, max(limits)) == (0, list(range(1, 251)), 100)


def test_refresh_with_no_cache_retries_a_page_whose_gh_read_fails_once_and_still_writes_the_full_cache_2244(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    monkeypatch.setenv("VERI_PAGE_RETRY_SLEEP", "0")
    (tmp_path / ".git").mkdir()
    everything = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-%02dT%02d:00:00Z" % (1 + n // 24, n % 24)}
        for n in range(1, 251)
    ]
    failed = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        limit = int(args[args.index("--limit") + 1])
        search = args[args.index("--search") + 1] if "--search" in args else ""
        if search and not failed:
            failed.append(search)
            return subprocess.CompletedProcess(args, 1, "", "HTTP 504: 504 Gateway Timeout (https://api.github.com/graphql)")
        pool = sorted(everything, key=lambda i: i["updatedAt"], reverse=True)
        for bound in search.split():
            if bound.startswith("updated:<="):
                pool = [i for i in pool if i["updatedAt"] <= bound[len("updated:<="):]]
            elif bound.startswith("updated:<"):
                pool = [i for i in pool if i["updatedAt"] < bound[len("updated:<"):]]
        return subprocess.CompletedProcess(args, 0, json.dumps(pool[:limit]), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    written = tmp_path / ".tdd" / "report-cache.json"
    kept = sorted(i["number"] for i in json.loads(written.read_text())["issues"]) if written.exists() else []
    assert (code, kept) == (0, list(range(1, 251)))


def test_refresh_with_no_cache_whose_page_keeps_failing_exits_2_after_bounded_attempts_and_leaves_nothing_in_tdd_2244(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    monkeypatch.setenv("VERI_PAGE_RETRY_SLEEP", "0")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    first_page = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-%02dT%02d:00:00Z" % (1 + n // 24, n % 24)}
        for n in range(1, 101)
    ]
    failing_calls = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        if "updated:<=" not in " ".join(args):
            return subprocess.CompletedProcess(args, 0, json.dumps(first_page), "")
        failing_calls.append(args)
        if len(failing_calls) > 50:
            raise AssertionError("retried without bound")
        return subprocess.CompletedProcess(args, 1, "", "HTTP 504: 504 Gateway Timeout (https://api.github.com/graphql)")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, out, "504" in err, sorted(p.name for p in (tmp_path / ".tdd").iterdir())) == (2, "", True, [])


def test_refresh_takes_its_page_retry_count_and_sleep_from_the_one_tunable_reader_2244(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    tunables = report_cache.tunables
    values = {"VERI_PAGE_RETRIES": "2", "VERI_PAGE_RETRY_SLEEP": "0"}
    real_read = tunables.read
    monkeypatch.setattr(tunables, "read", lambda name, default="", unless_empty=None:
                        values.get(name) or real_read(name, default, unless_empty))
    monkeypatch.setattr(report_cache.time, "sleep", lambda seconds: None)
    (tmp_path / ".git").mkdir()
    calls = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        calls.append(args)
        if len(calls) > 50:
            raise AssertionError("retried without bound")
        return subprocess.CompletedProcess(args, 1, "", "HTTP 504: 504 Gateway Timeout (https://api.github.com/graphql)")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, len(calls)) == (2, 2)


def test_refresh_with_no_cache_whose_first_page_fails_every_retry_at_100_fetches_it_again_at_a_smaller_limit_and_writes_the_full_cache_2279(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    monkeypatch.setenv("VERI_PAGE_RETRY_SLEEP", "0")
    (tmp_path / ".git").mkdir()
    everything = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-%02dT%02d:00:00Z" % (1 + n // 24, n % 24)}
        for n in range(1, 121)
    ]
    limits = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        limit = int(args[args.index("--limit") + 1])
        limits.append(limit)
        if len(limits) > 100:
            raise AssertionError("retried without bound")
        if limit > 50:
            return subprocess.CompletedProcess(args, 1, "", "HTTP 504: 504 Gateway Timeout (https://api.github.com/graphql)")
        pool = sorted(everything, key=lambda i: i["updatedAt"], reverse=True)
        search = args[args.index("--search") + 1] if "--search" in args else ""
        for bound in search.split():
            if bound.startswith("updated:<="):
                pool = [i for i in pool if i["updatedAt"] <= bound[len("updated:<="):]]
            elif bound.startswith("updated:<"):
                pool = [i for i in pool if i["updatedAt"] < bound[len("updated:<"):]]
        return subprocess.CompletedProcess(args, 0, json.dumps(pool[:limit]), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    written = tmp_path / ".tdd" / "report-cache.json"
    kept = sorted(i["number"] for i in json.loads(written.read_text())["issues"]) if written.exists() else []
    assert (code, kept, limits[0]) == (0, list(range(1, 121)), 100)


def test_refresh_with_no_cache_whose_first_page_fails_at_every_size_exits_2_with_the_gh_message_after_bounded_calls_and_writes_nothing_2279(run_cli, monkeypatch, tmp_path):
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    monkeypatch.setenv("VERI_PAGE_RETRY_SLEEP", "0")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    limits = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        limits.append(int(args[args.index("--limit") + 1]))
        if len(limits) > 50:
            raise AssertionError("retried without bound")
        return subprocess.CompletedProcess(args, 1, "", "HTTP 504: 504 Gateway Timeout (https://api.github.com/graphql)")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, out, "gh issue list failed: HTTP 504" in err, 0 < len(limits) <= 10, sorted(p.name for p in (tmp_path / ".tdd").iterdir())) == (2, "", True, True, [])


def test_refresh_with_a_well_formed_cache_retries_a_failed_gh_read_pages_the_updated_issues_and_merges_them_2279(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    monkeypatch.setenv("VERI_PAGE_RETRY_SLEEP", "0")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_text(json.dumps({"fetched_at": "2026-10-01T00:00:00Z", "cache_format": 2, "issues": [
        {"number": 900, "title": "old", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-09-30T10:00:00Z", "blockedBy": [], "wallSeconds": None, "lane": None}]}))
    updated = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-%02dT%02d:00:00Z" % (1 + n // 24, n % 24)}
        for n in range(1, 251)
    ]
    searches = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        limit = int(args[args.index("--limit") + 1])
        search = args[args.index("--search") + 1] if "--search" in args else ""
        searches.append(search)
        if len(searches) == 1:
            return subprocess.CompletedProcess(args, 1, "", "HTTP 504: 504 Gateway Timeout (https://api.github.com/graphql)")
        pool = sorted(updated, key=lambda i: i["updatedAt"], reverse=True)
        for bound in search.split():
            if bound.startswith("updated:<="):
                pool = [i for i in pool if i["updatedAt"] <= bound[len("updated:<="):]]
        return subprocess.CompletedProcess(args, 0, json.dumps(pool[:limit]), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    kept = sorted(i["number"] for i in json.loads(cache.read_text())["issues"])
    first = [t for t in searches[0].split() if t.startswith("updated:>=")]
    assert (code, first, kept) == (0, ["updated:>=2026-10-01T00:00:00Z"], list(range(1, 251)) + [900])


def test_refresh_with_a_well_formed_cache_bounds_every_later_page_by_fetched_at_so_older_issues_stay_out_2279(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    monkeypatch.setenv("VERI_PAGE_RETRY_SLEEP", "0")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_text(json.dumps({"fetched_at": "2026-10-01T00:00:00Z", "cache_format": 2, "issues": [
        {"number": 900, "title": "kept", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-09-30T10:00:00Z", "blockedBy": [], "wallSeconds": None, "lane": None}]}))
    recent = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-%02dT%02d:00:00Z" % (2 + n // 24, n % 24)}
        for n in range(1, 121)
    ]
    older = [
        {"number": 1000 + n, "title": "older %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-09-%02dT%02d:00:00Z" % (1 + n // 24, n % 24)}
        for n in range(30)
    ]

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        limit = int(args[args.index("--limit") + 1])
        search = args[args.index("--search") + 1] if "--search" in args else ""
        pool = sorted(recent + older, key=lambda i: i["updatedAt"], reverse=True)
        for term in search.split():
            if term.startswith("updated:>="):
                pool = [i for i in pool if i["updatedAt"] >= term[len("updated:>="):]]
            if term.startswith("updated:<="):
                pool = [i for i in pool if i["updatedAt"] <= term[len("updated:<="):]]
        return subprocess.CompletedProcess(args, 0, json.dumps(pool[:limit]), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    kept = sorted(i["number"] for i in json.loads(cache.read_text())["issues"])
    assert (code, kept) == (0, list(range(1, 121)) + [900])


def test_refresh_with_no_cache_and_over_100_issues_sharing_one_updated_at_second_never_exits_0_with_a_partial_cache_2272(run_cli, monkeypatch, tmp_path):
    import json
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    monkeypatch.setenv("VERI_PAGE_RETRY_SLEEP", "0")
    (tmp_path / ".git").mkdir()
    same_second = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-05T12:00:00Z"}
        for n in range(1, 151)
    ]
    older = [
        {"number": 1000 + n, "title": "older %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-09-%02dT00:00:00Z" % (1 + n)}
        for n in range(30)
    ]
    everything = sorted(i["number"] for i in same_second + older)

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        limit = int(args[args.index("--limit") + 1])
        search = args[args.index("--search") + 1] if "--search" in args else ""
        pool = sorted(same_second + older, key=lambda i: i["updatedAt"], reverse=True)
        for term in search.split():
            if term.startswith("updated:<="):
                pool = [i for i in pool if i["updatedAt"] <= term[len("updated:<="):]]
        return subprocess.CompletedProcess(args, 0, json.dumps(pool[:limit]), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    written = tmp_path / ".tdd" / "report-cache.json"
    kept = sorted(i["number"] for i in json.loads(written.read_text())["issues"]) if written.exists() else None
    assert (code, kept) in [(0, everything), (2, None)]


def test_refresh_with_many_page_retries_never_asks_for_limit_0_exits_2_and_writes_no_cache_2286(run_cli, monkeypatch, tmp_path):
    import subprocess

    report_cache = importlib.import_module("veri.report_cache")
    monkeypatch.setenv("VERI_PAGE_RETRIES", "10")
    monkeypatch.setenv("VERI_PAGE_RETRY_SLEEP", "0")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    limits = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:3] != ["gh", "issue", "list"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        limit = int(args[args.index("--limit") + 1])
        limits.append(limit)
        if limit == 0:
            return subprocess.CompletedProcess(args, 0, "[]", "")
        return subprocess.CompletedProcess(args, 1, "", "HTTP 504: 504 Gateway Timeout (https://api.github.com/graphql)")

    monkeypatch.setattr(subprocess, "run", fake_run)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, 0 in limits, sorted(p.name for p in (tmp_path / ".tdd").iterdir())) == (2, False, [])


def test_refresh_with_no_cache_and_150_issues_sharing_one_updated_at_second_writes_all_200_and_exits_0_2324(run_cli, monkeypatch, tmp_path):
    import json

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    same_second = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-05T12:00:00Z", "body": "", "comments": []}
        for n in range(1, 151)
    ]
    older = [
        {"number": 1000 + n, "title": "older %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-09-%02dT00:00:00Z" % (1 + n % 28), "body": "", "comments": []}
        for n in range(50)
    ]

    def fake_gh_issue_list(*args):
        limit = int(args[args.index("--limit") + 1])
        search = args[args.index("--search") + 1] if "--search" in args else ""
        pool = sorted(same_second + older, key=lambda i: (i["updatedAt"], i["number"]), reverse=True)
        for term in search.split():
            if term.startswith("updated:<="):
                pool = [i for i in pool if i["updatedAt"] <= term[len("updated:<="):]]
            elif term.startswith("updated:<"):
                pool = [i for i in pool if i["updatedAt"] < term[len("updated:<"):]]
        return json.dumps(pool[:limit])

    monkeypatch.setattr(report_cache.github, "gh_issue_list", fake_gh_issue_list)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    written = tmp_path / ".tdd" / "report-cache.json"
    kept = sorted(i["number"] for i in json.loads(written.read_text())["issues"]) if written.exists() else None
    assert (code, kept) == (0, sorted(i["number"] for i in same_second + older))


def test_refresh_with_no_cache_over_100_issues_never_repeats_a_gh_issue_list_request_within_the_refresh_2324(run_cli, monkeypatch, tmp_path):
    import json

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    issues = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-%02dT%02d:00:00Z" % (1 + n // 24, n % 24), "body": "", "comments": []}
        for n in range(1, 251)
    ]
    requests = []

    def fake_gh_issue_list(*args):
        limit = int(args[args.index("--limit") + 1])
        terms = (args[args.index("--search") + 1] if "--search" in args else "").split()
        pool = sorted(issues, key=lambda i: (i["updatedAt"], i["number"]), reverse=True)
        for term in terms:
            if term.startswith("updated:<="):
                pool = [i for i in pool if i["updatedAt"] <= term[len("updated:<="):]]
        requests.append((limit, tuple(t for t in terms if t != "sort:updated-desc")))
        return json.dumps(pool[:limit])

    monkeypatch.setattr(report_cache.github, "gh_issue_list", fake_gh_issue_list)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    assert (code, [r for r in requests if requests.count(r) > 1]) == (0, [])


def test_refresh_with_no_cache_and_1700_issues_sharing_one_updated_at_second_under_a_1000_row_search_cap_never_exits_0_with_a_partial_cache_2395(run_cli, monkeypatch, tmp_path):
    import json

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    issues = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-05T12:00:00Z", "body": "", "comments": []}
        for n in range(1, 1701)
    ]

    def fake_gh_issue_list(*args):
        limit = int(args[args.index("--limit") + 1])
        if "--search" in args:
            limit = min(limit, 1000)
        pool = sorted(issues, key=lambda i: (i["updatedAt"], i["number"]), reverse=True)
        for term in (args[args.index("--search") + 1] if "--search" in args else "").split():
            if term.startswith("updated:<="):
                pool = [i for i in pool if i["updatedAt"] <= term[len("updated:<="):]]
        return json.dumps(pool[:limit])

    monkeypatch.setattr(report_cache.github, "gh_issue_list", fake_gh_issue_list)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    written = tmp_path / ".tdd" / "report-cache.json"
    kept = sorted(i["number"] for i in json.loads(written.read_text())["issues"]) if written.exists() else None
    everything = sorted(i["number"] for i in issues)
    assert (code == 0 and kept == everything) or (code != 0 and kept is None), (code, None if kept is None else len(kept))


def test_refresh_with_no_cache_over_one_page_returns_every_issue_when_one_outside_the_first_unsorted_page_was_updated_later_2709(run_cli, monkeypatch, tmp_path):
    import json

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    issues = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-05T%02d:%02d:00Z" % divmod(300 - n, 60), "body": "", "comments": []}
        for n in range(1, 151)
    ]

    def fake_gh_issue_list(*args):
        limit = int(args[args.index("--limit") + 1])
        terms = (args[args.index("--search") + 1] if "--search" in args else "").split()
        if "sort:updated-desc" in terms:
            pool = sorted(issues, key=lambda i: (i["updatedAt"], i["number"]), reverse=True)
        else:
            pool = sorted(issues, key=lambda i: i["number"], reverse=True)
        for term in terms:
            if term.startswith("updated:<="):
                pool = [i for i in pool if i["updatedAt"] <= term[len("updated:<="):]]
        return json.dumps(pool[:limit])

    monkeypatch.setattr(report_cache.github, "gh_issue_list", fake_gh_issue_list)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    written = tmp_path / ".tdd" / "report-cache.json"
    kept = sorted(i["number"] for i in json.loads(written.read_text())["issues"]) if written.exists() else None
    assert (code, kept) == (0, list(range(1, 151)))


def test_refresh_with_a_cache_over_one_page_returns_every_issue_of_its_window_when_one_outside_the_first_unsorted_page_was_updated_later_2709(run_cli, monkeypatch, tmp_path):
    import json

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    cache = tmp_path / ".tdd" / "report-cache.json"
    cache.write_text(json.dumps({"fetched_at": "2026-10-01T00:00:00Z", "cache_format": 2, "issues": [
        {"number": 900, "title": "kept", "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-09-30T10:00:00Z", "blockedBy": [], "wallSeconds": None, "lane": None}]}))
    windowed = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-05T%02d:%02d:00Z" % divmod(300 - n, 60), "body": "", "comments": []}
        for n in range(1, 151)
    ]
    older = [
        {"number": 1000 + n, "title": "older %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-09-%02dT00:00:00Z" % (1 + n), "body": "", "comments": []}
        for n in range(5)
    ]

    def fake_gh_issue_list(*args):
        limit = int(args[args.index("--limit") + 1])
        terms = (args[args.index("--search") + 1] if "--search" in args else "").split()
        if "sort:updated-desc" in terms:
            pool = sorted(windowed + older, key=lambda i: (i["updatedAt"], i["number"]), reverse=True)
        else:
            pool = sorted(windowed + older, key=lambda i: i["number"], reverse=True)
        for term in terms:
            if term.startswith("updated:>="):
                pool = [i for i in pool if i["updatedAt"] >= term[len("updated:>="):]]
            if term.startswith("updated:<="):
                pool = [i for i in pool if i["updatedAt"] <= term[len("updated:<="):]]
        return json.dumps(pool[:limit])

    monkeypatch.setattr(report_cache.github, "gh_issue_list", fake_gh_issue_list)

    code, out, err = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    kept = sorted(i["number"] for i in json.loads(cache.read_text())["issues"])
    assert (code, kept) == (0, list(range(1, 151)) + [900])


def test_refresh_whose_fetch_sees_an_issue_updated_after_it_read_it_leaves_a_window_the_next_refresh_reads_it_from_2709(run_cli, monkeypatch, tmp_path):
    import json
    import types

    report_cache = importlib.import_module("veri.report_cache")
    (tmp_path / ".git").mkdir()
    real = report_cache.datetime
    clock = {"now": real.datetime(2026, 10, 20, 10, 0, 0, tzinfo=real.timezone.utc)}

    class FakeDatetime(real.datetime):
        @classmethod
        def now(cls, tz=None):
            return clock["now"]

    monkeypatch.setattr(report_cache, "datetime", types.SimpleNamespace(datetime=FakeDatetime, timezone=real.timezone))
    issues = [
        {"number": n, "title": "issue %d" % n, "state": "OPEN", "labels": [], "closedAt": None,
         "updatedAt": "2026-10-05T00:00:00Z", "body": "", "comments": []}
        for n in range(1, 4)
    ]
    reads = []

    def fake_gh_issue_list(*args):
        terms = (args[args.index("--search") + 1] if "--search" in args else "").split()
        pool = list(issues)
        for term in terms:
            if term.startswith("updated:>="):
                pool = [i for i in pool if i["updatedAt"] >= term[len("updated:>="):]]
        answer = json.dumps(pool)
        if not reads:
            issues[1]["updatedAt"] = "2026-10-20T10:00:03Z"
            clock["now"] = real.datetime(2026, 10, 20, 10, 0, 5, tzinfo=real.timezone.utc)
        reads.append(terms)
        return answer

    monkeypatch.setattr(report_cache.github, "gh_issue_list", fake_gh_issue_list)

    first = run_cli(report_cache, ["refresh"], cwd=tmp_path)
    clock["now"] = real.datetime(2026, 10, 20, 10, 1, 0, tzinfo=real.timezone.utc)
    second = run_cli(report_cache, ["refresh"], cwd=tmp_path)

    cached = json.loads((tmp_path / ".tdd" / "report-cache.json").read_text())["issues"]
    updated = {i["number"]: i["updatedAt"] for i in cached}
    assert (first[0], second[0], updated[2]) == (0, 0, "2026-10-20T10:00:03Z")
