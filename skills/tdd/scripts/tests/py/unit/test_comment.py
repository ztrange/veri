"""In-process cases for veri/comment.py, the module comment.sh is a shim over."""
import importlib
import json
import re

from conftest import SCRIPTS

USAGE = "usage: comment.sh <issue> <kind> [--note-file <path>]\n"


def test_no_argument_prints_the_usage_line_on_stderr_and_exits_2(run_cli):
    comment = importlib.import_module("veri.comment")

    code, out, err = run_cli(comment, [])

    assert (code, out, err) == (2, "", USAGE)
    shim = (SCRIPTS / "comment.sh").read_text()
    assert shim.startswith("#!/bin/sh\n")
    assert "# usage: comment.sh <issue> <kind> [--note-file <path>]\n" in shim


def test_step_done_posts_the_heading_naming_the_last_done_step_and_appends_a_comment_event_with_the_url(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-99"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text(
        "# Plan for #7\n\n- [x] first step alpha\n- [x] second step bravo\n- [ ] third step charlie\n")

    code, out, err = run_cli(comment, ["7", "step-done"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    number, body = posted[0]
    assert number == "7"
    assert body.splitlines()[0] == "### ✅ Step done"
    assert "second step bravo" in body
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e["kind"], e["url"]) for e in events] == [("comment", "step-done", url)]


def test_step_done_note_file_text_is_appended_under_the_rendered_comment(monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] second step bravo\n")
    note = tmp_path / "note.txt"
    note.write_text("the operator note zulu\n")

    code, out, err = run_cli(comment, ["7", "step-done", "--note-file", str(note)], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    body = posted[0]
    assert body.splitlines()[0] == "### ✅ Step done"
    assert body.rstrip("\n").endswith("the operator note zulu")
    assert body.index("second step bravo") < body.index("the operator note zulu")


def test_an_argument_after_kind_that_is_not_note_file_exits_2_with_usage_posting_and_journaling_nothing(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] second step bravo\n")

    code, out, err = run_cli(comment, ["7", "step-done", "--bogus"], cwd=tmp_path)

    assert code == 2
    assert err == USAGE
    assert posted == []
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_note_file_without_exactly_one_path_exits_2_with_usage_posting_and_journaling_nothing(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] second step bravo\n")
    (tmp_path / "note.txt").write_text("the operator note zulu\n")

    for extra in (["--note-file"], ["--note-file", "note.txt", "extra"]):
        code, out, err = run_cli(comment, ["7", "step-done", *extra], cwd=tmp_path)

        assert (code, err) == (2, USAGE), extra
    assert posted == []
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_four_arguments_whose_third_is_not_note_file_exit_2_with_usage_posting_and_journaling_nothing(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] second step bravo\n")
    (tmp_path / "x").write_text("the operator note zulu\n")

    code, out, err = run_cli(comment, ["7", "step-done", "--bogus", "x"], cwd=tmp_path)

    assert (code, out, err) == (2, "", USAGE)
    assert posted == []
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_step_done_exits_2_with_one_stderr_line_and_journals_nothing_when_github_gives_no_answer(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    github = importlib.import_module("github")

    def no_answer(number, body):
        raise github.NoAnswer("")

    monkeypatch.setattr(github, "gh_issue_comment", no_answer)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] second step bravo\n")

    code, out, err = run_cli(comment, ["7", "step-done"], cwd=tmp_path)

    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_step_done_heading_line_is_byte_for_byte_the_hand_composed_one_and_matches_its_metrics_family(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    metrics = importlib.import_module("metrics")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] second step bravo\n")

    code, out, err = run_cli(comment, ["7", "step-done"], cwd=tmp_path)

    assert code == 0
    heading = posted[0].splitlines()[0].encode()
    assert heading == b"### \xe2\x9c\x85 Step done"
    pattern = dict(metrics.COMMENT_FAMILIES)["\u2705 Step done"]
    assert re.search(pattern, heading.decode())


def test_an_issue_with_no_kind_exits_2_with_usage_posting_and_journaling_nothing(monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] second step bravo\n")

    code, out, err = run_cli(comment, ["7"], cwd=tmp_path)

    assert (code, out, err) == (2, "", USAGE)
    assert posted == []
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_the_comment_event_url_is_the_posted_html_url_with_its_trailing_newline_stripped(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-99"
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: url + "\n")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] second step bravo\n")

    code, out, err = run_cli(comment, ["7", "step-done"], cwd=tmp_path)

    assert code == 0
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [e["url"] for e in events] == [url]


def test_step_done_note_file_text_follows_the_rendered_comment_after_a_blank_line(monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] second step bravo\n")
    note = tmp_path / "note.txt"
    note.write_text("the operator note zulu\n")

    code, out, err = run_cli(comment, ["7", "step-done", "--note-file", str(note)], cwd=tmp_path)

    assert code == 0
    assert "second step bravo\n\nthe operator note zulu" in posted[0]


def test_an_unknown_kind_exits_2_with_usage_posting_and_journaling_nothing(monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] second step bravo\n")

    code, out, err = run_cli(comment, ["7", "bogus-kind"], cwd=tmp_path)

    assert (code, out, err) == (2, "", USAGE)
    assert posted == []
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_done_posts_the_done_heading_with_the_pr_url_then_the_metrics_file_verbatim_and_appends_a_comment_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-5"
    pr = "https://github.com/o/r/pull/12"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(json.dumps({"event": "done", "pr": pr}) + "\n")
    metrics = "### 📊 Metrics\n\n| phase | cost |\n|---|---|\n| red | $0.10 |\n"
    (tmp_path / ".tdd" / "issue-7-metrics.md").write_text(metrics)

    code, out, err = run_cli(comment, ["7", "done"], cwd=tmp_path)

    assert code == 0
    assert posted == [("7", f"### ✅ Done — {pr}\n\n{metrics}")]
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e.get("kind"), e.get("url")) for e in events[1:]] == [("comment", "done", url)]
