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
