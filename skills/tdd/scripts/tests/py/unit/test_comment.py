"""In-process cases for veri/comment.py, the module comment.sh is a shim over."""
import importlib
import json

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
