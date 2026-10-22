"""Cases for veri/report_cache.py."""
import importlib


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
