"""In-process cases for veri/preflight_refused.py, the module preflight-refused.sh is a shim over."""
import importlib
import json

USAGE = "usage: preflight-refused.sh <issue-number> <check>\n"


def test_2481_a_preflight_refusal_writes_one_event_naming_the_check_from_either_checkout(tmp_path, monkeypatch, run_cli):
    preflight_refused = importlib.import_module("veri.preflight_refused")
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment", lambda number, body: None)
    main = tmp_path / "main"
    (main / ".git").mkdir(parents=True)
    run = main / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".git").write_text("gitdir: elsewhere\n")
    log = run / ".tdd" / "events.jsonl"

    first = run_cli(preflight_refused, ["7", "full-tier baseline red"], cwd=main)
    second = run_cli(preflight_refused, ["7", "fast-tier baseline red"], cwd=run)
    events = [json.loads(text) for text in log.read_text().splitlines()]

    assert (first[0], second[0]) == (0, 0)
    assert [(e["event"], e["check"], e["cause"], e["classification"]) for e in events] == [
        ("preflight-refused", "full-tier baseline red", "preflight-refused", "system"),
        ("preflight-refused", "fast-tier baseline red", "preflight-refused", "system"),
    ]
    for argv in ([], ["7"], ["7", ""]):
        assert run_cli(preflight_refused, argv, cwd=main) == (2, "", USAGE)
    assert len(log.read_text().splitlines()) == 2


def test_2481_b_preflight_refusal_posts_one_comment_naming_the_check_and_exits_2_when_github_refuses_it(
        tmp_path, monkeypatch, run_cli):
    preflight_refused = importlib.import_module("veri.preflight_refused")
    github = importlib.import_module("github")
    posted = []
    monkeypatch.setattr(github, "gh_issue_comment", lambda number, body: posted.append((str(number), body)))
    first_launch = tmp_path / "first"
    (first_launch / ".git").mkdir(parents=True)
    resume = tmp_path / "resume"
    (resume / ".git").mkdir(parents=True)
    run = resume / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "issue-7.md").write_text("- [x] 1. done\n")

    first = run_cli(preflight_refused, ["7", "full-tier baseline red"], cwd=first_launch)
    second = run_cli(preflight_refused, ["7", "fast-tier baseline red"], cwd=resume)

    assert (first[0], second[0]) == (0, 0)
    assert [(n, body.splitlines()[0]) for n, body in posted] == [
        ("7", "### ⛔ Preflight refused — full-tier baseline red"),
        ("7", "### ⛔ Preflight refused — fast-tier baseline red"),
    ]

    def refuse(number, body):
        raise github.NoAnswer("")

    monkeypatch.setattr(github, "gh_issue_comment", refuse)
    refused = run_cli(preflight_refused, ["7", "refused check"], cwd=resume)
    events = [json.loads(text) for text in (run / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert (refused[0], events[-1]["check"]) == (2, "refused check")
