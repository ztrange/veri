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
    with log.open("a") as resumed:
        resumed.write('{"ts": 1, "issue": "7", "event": "resume"}\n')
    second = run_cli(preflight_refused, ["7", "fast-tier baseline red"], cwd=run)
    events = [json.loads(text) for text in log.read_text().splitlines() if '"resume"' not in text]

    assert (first[0], second[0]) == (0, 0)
    assert [(e["event"], e["check"], e["cause"], e["classification"]) for e in events] == [
        ("preflight-refused", "full-tier baseline red", "preflight-refused", "system"),
        ("preflight-refused", "fast-tier baseline red", "preflight-refused", "system"),
    ]
    for argv in ([], ["7"], ["7", ""]):
        assert run_cli(preflight_refused, argv, cwd=main) == (2, "", USAGE)
    assert len(log.read_text().splitlines()) == 3


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
    with (run / ".tdd" / "events.jsonl").open("a") as resumed:
        resumed.write('{"ts": 1, "issue": "7", "event": "resume"}\n')
    refused = run_cli(preflight_refused, ["7", "refused check"], cwd=resume)
    assert refused[0] == 2


def test_2557_an_empty_issue_number_exits_2_with_the_usage_line_writes_no_event_and_posts_no_comment(
        tmp_path, monkeypatch, run_cli):
    preflight_refused = importlib.import_module("veri.preflight_refused")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)))
    main = tmp_path / "main"
    (main / ".git").mkdir(parents=True)

    result = run_cli(preflight_refused, ["", "baseline-full-red"], cwd=main)

    assert result == (2, "", USAGE)
    assert not (main / ".tdd").exists()
    assert posted == []


def test_2557_a_missing_or_empty_check_exits_2_with_the_usage_line_writes_no_event_and_posts_no_comment(
        tmp_path, monkeypatch, run_cli):
    preflight_refused = importlib.import_module("veri.preflight_refused")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)))
    main = tmp_path / "main"
    (main / ".git").mkdir(parents=True)

    results = [run_cli(preflight_refused, argv, cwd=main) for argv in ([], ["7"], ["7", ""])]

    assert results == [(2, "", USAGE)] * 3
    assert not (main / ".tdd").exists()
    assert posted == []


def test_2557_both_arguments_given_writes_exactly_one_event_in_the_issue_run_and_posts_exactly_one_comment(
        tmp_path, monkeypatch, run_cli):
    preflight_refused = importlib.import_module("veri.preflight_refused")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)))
    main = tmp_path / "main"
    (main / ".git").mkdir(parents=True)

    code = run_cli(preflight_refused, ["7", "baseline-full-red"], cwd=main)[0]

    log = main / ".tdd" / "wt" / "7" / ".tdd" / "events.jsonl"
    assert code == 0
    assert [json.loads(text)["event"] for text in log.read_text().splitlines()] == ["preflight-refused"]
    assert not (main / ".tdd" / "wt" / ".tdd").exists()
    assert [(n, body.splitlines()[0]) for n, body in posted] == [("7", "### ⛔ Preflight refused — baseline-full-red")]


def test_2481_c_a_second_refusal_of_a_refused_run_writes_no_event_posts_no_comment_and_exits_3(
        tmp_path, monkeypatch, run_cli):
    preflight_refused = importlib.import_module("veri.preflight_refused")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)))
    main = tmp_path / "main"
    (main / ".git").mkdir(parents=True)
    run = main / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)

    first = run_cli(preflight_refused, ["7", "full-tier baseline red"], cwd=main)
    second = run_cli(preflight_refused, ["7", "fast-tier baseline red"], cwd=main)
    events = [json.loads(text) for text in (run / ".tdd" / "events.jsonl").read_text().splitlines()]

    assert (first[0], second[0]) == (0, 3)
    assert [e["check"] for e in events] == ["full-tier baseline red"]
    assert [body.splitlines()[0] for _, body in posted] == ["### ⛔ Preflight refused — full-tier baseline red"]


def test_2557_no_argument_combination_creates_a_tdd_directory_in_wt_and_the_run_is_named_after_the_issue(
        tmp_path, monkeypatch, run_cli):
    preflight_refused = importlib.import_module("veri.preflight_refused")
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment", lambda number, body: None)
    main = tmp_path / "main"
    (main / ".git").mkdir(parents=True)

    for argv in ([], [""], ["", ""], ["", "baseline-full-red"], ["7"], ["7", ""], ["7", "baseline-full-red"]):
        run_cli(preflight_refused, argv, cwd=main)

    wt = main / ".tdd" / "wt"
    assert sorted(path.name for path in wt.iterdir()) == ["7"]
    assert (wt / "7" / ".tdd" / "events.jsonl").is_file()


def test_2700_a_refusal_of_a_run_already_marked_refused_whose_conductor_is_live_writes_no_event_posts_no_comment_and_exits_3(
        tmp_path, monkeypatch, run_cli):
    from conftest import live_conductor
    preflight_refused = importlib.import_module("veri.preflight_refused")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)))
    main = tmp_path / "main"
    (main / ".git").mkdir(parents=True)
    run = main / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    first = run_cli(preflight_refused, ["7", "full-tier baseline red"], cwd=main)
    live_conductor(monkeypatch, run / ".tdd", 7)

    second = run_cli(preflight_refused, ["7", "fast-tier baseline red"], cwd=main)
    events = [json.loads(text) for text in (run / ".tdd" / "events.jsonl").read_text().splitlines()]

    assert (first[0], second[0]) == (0, 3)
    assert [e["check"] for e in events] == ["full-tier baseline red"]
    assert len(posted) == 1
