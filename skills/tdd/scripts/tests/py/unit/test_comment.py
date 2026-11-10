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


def test_done_posts_the_failed_render_line_with_the_exit_code_metrics_returns_when_the_metrics_file_is_absent(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-6"
    pr = "https://github.com/o/r/pull/12"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    monkeypatch.setattr(importlib.import_module("metrics"), "main", lambda argv: 3)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(json.dumps({"event": "done", "pr": pr}) + "\n")

    code, out, err = run_cli(comment, ["7", "done"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    assert posted[0][0] == "7"
    assert posted[0][1].startswith(f"### ✅ Done — {pr}\n\n")
    assert "metrics could not be rendered: metrics.sh exited 3" in posted[0][1]


def test_done_posts_the_failed_render_line_in_place_of_a_metrics_file_whose_first_line_is_not_the_metrics_heading(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-6"
    pr = "https://github.com/o/r/pull/12"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    monkeypatch.setattr(importlib.import_module("metrics"), "main", lambda argv: 3)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(json.dumps({"event": "done", "pr": pr}) + "\n")
    (tmp_path / ".tdd" / "issue-7-metrics.md").write_text("garbled render\n| a | b |\n")

    code, out, err = run_cli(comment, ["7", "done"], cwd=tmp_path)

    assert code == 0
    assert posted == [("7", f"### ✅ Done — {pr}\n\nmetrics could not be rendered: metrics.sh exited 3")]


def test_done_leaves_the_journal_with_its_one_done_event_plus_the_one_comment_event(monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-8"
    pr = "https://github.com/o/r/pull/12"
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment", lambda number, body: url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    done = json.dumps({"event": "done", "pr": pr})
    (tmp_path / ".tdd" / "events.jsonl").write_text(done + "\n")
    (tmp_path / ".tdd" / "issue-7-metrics.md").write_text("### 📊 Metrics\n\n| phase | cost |\n|---|---|\n")

    code, out, err = run_cli(comment, ["7", "done"], cwd=tmp_path)

    assert code == 0
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [e["event"] for e in events] == ["done", "comment"]
    assert events[0] == json.loads(done)


def test_done_carries_the_unverified_phases_line_when_skip_verify_is_non_empty_though_the_metrics_block_lacks_it(
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
    (tmp_path / ".tdd" / "issue-7-metrics.md").write_text("### 📊 Metrics\n\n| phase | cost |\n|---|---|\n| red | $0.10 |\n")
    (tmp_path / ".tdd" / "issue-7-skip-verify").write_text("refactor\n")

    code, out, err = run_cli(comment, ["7", "done"], cwd=tmp_path)

    assert code == 0
    assert "⚠️ Unverified phases: refactor" in posted[0][1].splitlines()


def test_the_posted_done_comment_passes_the_conductors_done_check_and_matches_the_done_metrics_family(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    conductor = importlib.import_module("run_conductor")
    metrics = importlib.import_module("metrics")
    pr = "https://github.com/o/r/pull/12"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-5")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(json.dumps({"event": "done", "pr": pr}) + "\n")
    (tmp_path / ".tdd" / "issue-7-metrics.md").write_text("### 📊 Metrics\n\n| phase | cost |\n|---|---|\n| red | $0.10 |\n")

    code, out, err = run_cli(comment, ["7", "done"], cwd=tmp_path)

    assert code == 0
    thread = [{"body": posted[0], "created_at": "2026-11-08T00:00:00Z"}]
    monkeypatch.setattr(conductor, "last_resume", lambda issue: 0)
    monkeypatch.setattr(conductor.github, "gh_json_page", lambda jq, path: json.dumps(thread))
    assert conductor.done_posted("7") is True
    pattern = dict(metrics.COMMENT_FAMILIES)["✅ Done"]
    assert re.search(pattern, posted[0])


def test_done_still_posts_the_pr_url_when_the_journal_holds_a_torn_line_before_the_done_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-9"
    pr = "https://github.com/o/r/pull/12"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        '{"event": "sta\n\n' + json.dumps({"event": "done", "pr": pr}) + "\n")
    metrics = "### 📊 Metrics\n\n| phase | cost |\n|---|---|\n"
    (tmp_path / ".tdd" / "issue-7-metrics.md").write_text(metrics)

    code, out, err = run_cli(comment, ["7", "done"], cwd=tmp_path)

    assert code == 0
    assert posted == [("7", f"### ✅ Done — {pr}\n\n{metrics}")]


def _done_setup(monkeypatch, tmp_path, events):
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://github.com/o/r/issues/7#issuecomment-9")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    return posted


def test_done_carries_the_block_metrics_renders_when_the_committed_file_is_absent_and_the_render_succeeds(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    pr = "https://github.com/o/r/pull/12"
    posted = _done_setup(monkeypatch, tmp_path, [{"event": "done", "pr": pr}])
    block = "### 📊 Metrics\n\n| phase | cost |\n|---|---|\n| red | $0.10 |\n"

    def render(argv):
        print(block, end="")
        return 0
    monkeypatch.setattr(importlib.import_module("metrics"), "main", render)

    code, out, err = run_cli(comment, ["7", "done"], cwd=tmp_path)

    assert code == 0
    assert posted == [("7", f"### ✅ Done — {pr}\n\n{block}")]
    assert "Metrics" not in out


def test_done_exits_2_with_one_stderr_line_posting_and_journaling_nothing_when_the_journal_has_no_done_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = _done_setup(monkeypatch, tmp_path, [{"event": "start"}])
    (tmp_path / ".tdd" / "issue-7-metrics.md").write_text("### 📊 Metrics\n")

    code, out, err = run_cli(comment, ["7", "done"], cwd=tmp_path)

    assert code == 2
    assert len(err.splitlines()) == 1
    assert posted == []
    assert "comment" not in (tmp_path / ".tdd" / "events.jsonl").read_text()


def test_done_adds_the_stop_arrived_line_when_a_stop_request_is_pending_and_none_otherwise(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    pr = "https://github.com/o/r/pull/12"
    posted = _done_setup(monkeypatch, tmp_path, [{"event": "done", "pr": pr}])
    (tmp_path / ".tdd" / "issue-7-metrics.md").write_text("### 📊 Metrics\n")

    run_cli(comment, ["7", "done"], cwd=tmp_path)
    (tmp_path / ".tdd" / "stop").write_text("at-leaf\n")
    run_cli(comment, ["7", "done"], cwd=tmp_path)

    assert "stop" not in posted[0][1].lower()
    assert "A stop arrived after the last step, so the run finished rather than pausing." in posted[1][1].splitlines()


def test_red_posts_the_red_heading_with_the_test_failure_and_matched_prediction_and_appends_a_comment_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-55"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-red.out").write_text(
        "I wrote the case.\n"
        "TEST_PATH: tests/py/unit/test_widget.py\n"
        "TARGET_TEST: test_widget_spins_clockwise\n"
        "AGAINST_UNMODIFIED: FAILS\n"
        "FAIL_OUTPUT: assert 'ccw' == 'cw'\n"
        "PREDICTED_FAILURE: assert spin == 'cw' fires with 'ccw'\n"
        "PREDICTION: MATCHED\n")

    code, out, err = run_cli(comment, ["7", "red"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    number, body = posted[0]
    assert number == "7"
    assert body.splitlines()[0] == "### 🔴 Red"
    for carried in ("tests/py/unit/test_widget.py", "test_widget_spins_clockwise",
                    "assert 'ccw' == 'cw'", "assert spin == 'cw' fires with 'ccw'",
                    "prediction matched"):
        assert carried in body, carried
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e["kind"], e["url"]) for e in events] == [("comment", "red", url)]


def test_red_posts_prediction_diverged_with_the_prediction_note_in_place_of_prediction_matched(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-56")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-red.out").write_text(
        "TEST_PATH: tests/py/unit/test_widget.py\n"
        "TARGET_TEST: test_widget_spins_clockwise\n"
        "AGAINST_UNMODIFIED: FAILS\n"
        "FAIL_OUTPUT: KeyError: 'spin'\n"
        "PREDICTED_FAILURE: assert spin == 'cw' fires with 'ccw'\n"
        "PREDICTION: DIVERGED\n"
        "PREDICTION_NOTE: the fixture lacked a spin key so a KeyError fired first\n")

    code, out, err = run_cli(comment, ["7", "red"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    body = posted[0]
    assert "prediction diverged" in body.splitlines()
    assert "prediction matched" not in body
    assert "the fixture lacked a spin key so a KeyError fired first" in body
    assert body.index("prediction diverged") < body.index("the fixture lacked a spin key")


def test_red_reads_the_prediction_by_its_first_word_with_trailing_punctuation_stripped(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-57")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    for prediction, diverged in (("DIVERGED.", True), ("DIVERGED, wrong key", True), ("MATCHED", False)):
        (tmp_path / ".tdd" / "develop-red.out").write_text(
            "TEST_PATH: tests/py/unit/test_widget.py\n"
            "TARGET_TEST: test_widget_spins_clockwise\n"
            "AGAINST_UNMODIFIED: FAILS\n"
            "FAIL_OUTPUT: KeyError: 'spin'\n"
            "PREDICTED_FAILURE: assert spin == 'cw' fires with 'ccw'\n"
            f"PREDICTION: {prediction}\n"
            "PREDICTION_NOTE: a KeyError fired first\n")

        code, out, err = run_cli(comment, ["7", "red"], cwd=tmp_path)

        body = posted[-1]
        assert code == 0, prediction
        if diverged:
            assert "prediction diverged" in body.splitlines(), prediction
            assert "prediction matched" not in body, prediction
            assert "a KeyError fired first" in body, prediction
        else:
            assert "prediction matched" in body.splitlines(), prediction
            assert "prediction diverged" not in body, prediction


def test_red_note_file_text_follows_the_rendered_red_comment_after_a_blank_line(monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-57")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-red.out").write_text(
        "TEST_PATH: tests/py/unit/test_widget.py\n"
        "TARGET_TEST: test_widget_spins_clockwise\n"
        "AGAINST_UNMODIFIED: FAILS\n"
        "FAIL_OUTPUT: assert 'ccw' == 'cw'\n"
        "PREDICTED_FAILURE: assert spin == 'cw' fires with 'ccw'\n"
        "PREDICTION: MATCHED\n")
    note = tmp_path / "note.txt"
    note.write_text("the conductor note yankee\n")

    code, out, err = run_cli(comment, ["7", "red", "--note-file", str(note)], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    assert posted[0].splitlines()[0] == "### 🔴 Red"
    assert "prediction matched\n\nthe conductor note yankee" in posted[0]


def test_verify_red_pass_posts_the_pass_heading_then_the_reason_and_appends_a_comment_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-57"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verdict-red.exit").write_text("0\n")
    (tmp_path / ".tdd" / "verify-red.reason").write_text("the case fails on the missing spin key, as the criterion says\n")

    code, out, err = run_cli(comment, ["7", "verify-red"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    number, body = posted[0]
    assert number == "7"
    assert body.splitlines()[0] == "### 🔎 verify-red — PASS"
    assert "the case fails on the missing spin key, as the criterion says" in body.splitlines()[1:]
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e["kind"], e["url"]) for e in events] == [("comment", "verify-red", url)]


def test_verify_red_reject_posts_the_reject_heading_then_the_reason_when_the_verdict_exit_is_1(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-58"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verdict-red.exit").write_text("1\n")
    (tmp_path / ".tdd" / "verify-red.reason").write_text("the case asserts a mechanism, not the criterion\n")

    code, out, err = run_cli(comment, ["7", "verify-red"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    assert posted[0][1].splitlines()[0] == "### 🔎 verify-red — REJECT"
    assert "the case asserts a mechanism, not the criterion" in posted[0][1].splitlines()[1:]


def test_the_posted_red_and_verify_red_headings_match_the_red_metrics_family_as_hand_composed_ones_do(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    metrics = importlib.import_module("metrics")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-59")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-red.out").write_text(
        "TEST_PATH: tests/py/unit/test_widget.py\n"
        "TARGET_TEST: test_widget_spins_clockwise\n"
        "AGAINST_UNMODIFIED: FAILS\n"
        "FAIL_OUTPUT: assert 'ccw' == 'cw'\n"
        "PREDICTED_FAILURE: assert spin == 'cw' fires with 'ccw'\n"
        "PREDICTION: MATCHED\n")
    (tmp_path / ".tdd" / "verdict-red.exit").write_text("0\n")
    (tmp_path / ".tdd" / "verify-red.reason").write_text("the case fails for the criterion\n")

    assert run_cli(comment, ["7", "red"], cwd=tmp_path)[0] == 0
    assert run_cli(comment, ["7", "verify-red"], cwd=tmp_path)[0] == 0

    pattern = dict(metrics.COMMENT_FAMILIES)["🔴 Red"]
    families = [[name for name, rx in metrics.COMMENT_FAMILIES if re.search(rx, body.splitlines()[0])]
                for body in posted]
    assert families == [["🔴 Red"], ["🔴 Red"]]
    assert [body.splitlines()[0] for body in posted] == ["### 🔴 Red", "### 🔎 verify-red — PASS"]
    assert pattern


def test_red_exits_2_naming_the_missing_develop_red_report_posting_and_journaling_nothing(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://example/c/1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()

    code, out, err = run_cli(comment, ["7", "red"], cwd=tmp_path)

    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
    assert ".tdd/develop-red.out" in err
    assert posted == []
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_red_exits_2_naming_test_path_when_the_report_has_no_test_path_line_posting_and_journaling_nothing(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://example/c/1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-red.out").write_text(
        "TARGET_TEST: test_widget_spins_clockwise\n"
        "AGAINST_UNMODIFIED: FAILS\n"
        "FAIL_OUTPUT: assert 'ccw' == 'cw'\n"
        "PREDICTED_FAILURE: assert spin == 'cw' fires with 'ccw'\n"
        "PREDICTION: MATCHED\n")

    code, out, err = run_cli(comment, ["7", "red"], cwd=tmp_path)

    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
    assert "TEST_PATH:" in err
    assert posted == []
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_red_exits_2_naming_prediction_note_when_diverged_without_a_note_line_posting_and_journaling_nothing(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://example/c/1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-red.out").write_text(
        "TEST_PATH: tests/py/unit/test_widget.py\n"
        "TARGET_TEST: test_widget_spins_clockwise\n"
        "AGAINST_UNMODIFIED: FAILS\n"
        "FAIL_OUTPUT: KeyError: 'spin'\n"
        "PREDICTED_FAILURE: assert spin == 'cw' fires with 'ccw'\n"
        "PREDICTION: DIVERGED\n")

    code, out, err = run_cli(comment, ["7", "red"], cwd=tmp_path)

    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
    assert "PREDICTION_NOTE:" in err
    assert posted == []
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_red_exits_2_naming_the_missing_line_when_the_report_lacks_target_test_fail_output_or_predicted_failure(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://example/c/1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    lines = {
        "TARGET_TEST": "TARGET_TEST: test_widget_spins_clockwise\n",
        "FAIL_OUTPUT": "FAIL_OUTPUT: assert 'ccw' == 'cw'\n",
        "PREDICTED_FAILURE": "PREDICTED_FAILURE: assert spin == 'cw' fires with 'ccw'\n",
    }
    for missing in lines:
        report = "TEST_PATH: tests/py/unit/test_widget.py\n" + "".join(
            text for key, text in lines.items() if key != missing) + "PREDICTION: MATCHED\n"
        (tmp_path / ".tdd" / "develop-red.out").write_text(report)

        code, out, err = run_cli(comment, ["7", "red"], cwd=tmp_path)

        assert code == 2, missing
        assert out == "", missing
        assert len(err.splitlines()) == 1, missing
        assert f"{missing}:" in err, missing
        assert posted == [], missing
        assert not (tmp_path / ".tdd" / "events.jsonl").exists(), missing


def test_the_red_metrics_family_pattern_matches_the_emoji_heading_text_each_red_and_verify_red_comment_posts(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    metrics = importlib.import_module("metrics")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-60")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-red.out").write_text(
        "TEST_PATH: tests/py/unit/test_widget.py\n"
        "TARGET_TEST: test_widget_spins_clockwise\n"
        "AGAINST_UNMODIFIED: FAILS\n"
        "FAIL_OUTPUT: assert 'ccw' == 'cw'\n"
        "PREDICTED_FAILURE: assert spin == 'cw' fires with 'ccw'\n"
        "PREDICTION: MATCHED\n")
    (tmp_path / ".tdd" / "verdict-red.exit").write_text("0\n")
    (tmp_path / ".tdd" / "verify-red.reason").write_text("the case fails for the criterion\n")

    assert run_cli(comment, ["7", "red"], cwd=tmp_path)[0] == 0
    assert run_cli(comment, ["7", "verify-red"], cwd=tmp_path)[0] == 0

    pattern = dict(metrics.COMMENT_FAMILIES)["🔴 Red"]
    headings = [body.splitlines()[0] for body in posted]
    assert headings == ["### 🔴 Red", "### 🔎 verify-red — PASS"]
    matched = [re.search(pattern, heading).group(0) for heading in headings]
    assert matched == ["🔴 Red", "🔎 verify-red"]
    assert all(heading.startswith("### " + text) for heading, text in zip(headings, matched))
    assert not re.search(pattern, "### Red")
    assert not re.search(pattern, "### verify-red — PASS")


def test_red_with_an_unknown_flag_or_a_note_file_lacking_its_path_exits_2_with_usage_posting_nothing_unlike_the_valid_call(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-58")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-red.out").write_text(
        "TEST_PATH: tests/py/unit/test_widget.py\n"
        "TARGET_TEST: test_widget_spins_clockwise\n"
        "AGAINST_UNMODIFIED: FAILS\n"
        "FAIL_OUTPUT: assert 'ccw' == 'cw'\n"
        "PREDICTED_FAILURE: assert spin == 'cw' fires with 'ccw'\n"
        "PREDICTION: MATCHED\n")
    note = tmp_path / "note.txt"
    note.write_text("the conductor note yankee\n")

    code, out, err = run_cli(comment, ["7", "red", "--note-file", str(note)], cwd=tmp_path)

    assert code == 0
    assert [b.splitlines()[0] for b in posted] == ["### 🔴 Red"]
    posted.clear()
    events = (tmp_path / ".tdd" / "events.jsonl").read_text()

    for bad in (["--bogus", str(note)], ["--note-file"]):
        code, out, err = run_cli(comment, ["7", "red", *bad], cwd=tmp_path)

        assert (code, err) == (2, USAGE), bad
    assert posted == []
    assert (tmp_path / ".tdd" / "events.jsonl").read_text() == events


def test_green_posts_the_green_heading_with_the_implementation_and_suite_output_and_appends_a_comment_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-77"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-green.out").write_text(
        "I made it spin.\n"
        "IMPL_PATH: src/widget.py, src/spin.py\n"
        "SUITE: GREEN 42 passed in 1.3s\n")

    code, out, err = run_cli(comment, ["7", "green"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    number, body = posted[0]
    assert number == "7"
    assert body.splitlines()[0] == "### 🟢 Green"
    for carried in ("src/widget.py, src/spin.py", "GREEN 42 passed in 1.3s"):
        assert carried in body, carried
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e["kind"], e["url"]) for e in events] == [("comment", "green", url)]


def test_green_exits_2_naming_the_missing_develop_green_report_posting_and_journaling_nothing(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://example/c/1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()

    code, out, err = run_cli(comment, ["7", "green"], cwd=tmp_path)

    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
    assert ".tdd/develop-green.out" in err
    assert posted == []
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_green_exits_2_naming_the_missing_line_when_the_report_lacks_impl_path_or_suite_posting_and_journaling_nothing(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://example/c/1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    lines = {
        "IMPL_PATH": "IMPL_PATH: src/widget.py\n",
        "SUITE": "SUITE: GREEN 42 passed in 1.3s\n",
    }
    for missing in lines:
        (tmp_path / ".tdd" / "develop-green.out").write_text(
            "I made it spin.\n" + "".join(text for key, text in lines.items() if key != missing))

        code, out, err = run_cli(comment, ["7", "green"], cwd=tmp_path)

        assert code == 2, missing
        assert out == "", missing
        assert len(err.splitlines()) == 1, missing
        assert f"{missing}:" in err, missing
        assert ".tdd/develop-green.out" in err, missing
        assert posted == [], missing
        assert not (tmp_path / ".tdd" / "events.jsonl").exists(), missing


def test_green_note_file_text_follows_the_rendered_green_comment_after_a_blank_line(monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://example/c/1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-green.out").write_text(
        "IMPL_PATH: src/widget.py\nSUITE: GREEN 42 passed in 1.3s\n")
    note = tmp_path / "note.txt"
    note.write_text("the conductor note xray\n")

    code, out, err = run_cli(comment, ["7", "green", "--note-file", str(note)], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    assert posted[0].startswith("### 🟢 Green")
    assert "GREEN 42 passed in 1.3s\n\nthe conductor note xray" in posted[0]


def test_verify_green_pass_posts_the_pass_heading_then_the_reason_and_appends_a_comment_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-91"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verdict-green.exit").write_text("0\n")
    (tmp_path / ".tdd" / "verify-green.reason").write_text("the implementation is minimal and the suite is green\n")

    code, out, err = run_cli(comment, ["7", "verify-green"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    number, body = posted[0]
    assert number == "7"
    assert body.splitlines()[0] == "### 🔎 verify-green — PASS"
    assert "the implementation is minimal and the suite is green" in body.splitlines()[1:]
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e["kind"], e["url"]) for e in events] == [("comment", "verify-green", url)]


def test_verify_green_reject_posts_the_reject_heading_then_the_reason(monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://github.com/o/r/issues/7#issuecomment-92")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verdict-green.exit").write_text("1\n")
    (tmp_path / ".tdd" / "verify-green.reason").write_text("the implementation hardcodes the expected value\n")

    code, out, err = run_cli(comment, ["7", "verify-green"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    body = posted[0][1]
    assert body.splitlines()[0] == "### 🔎 verify-green — REJECT"
    assert "the implementation hardcodes the expected value" in body.splitlines()[1:]


def test_refactor_posts_the_refactor_heading_with_each_transform_in_order_and_appends_a_comment_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-88"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-refactor.out").write_text(
        "Tidied up.\n"
        "RESULT: extracted spin_once from Widget.spin\n"
        "RESULT: renamed tmp to angle in spin.py\n")

    code, out, err = run_cli(comment, ["7", "refactor"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    number, body = posted[0]
    assert number == "7"
    assert body.splitlines()[0] == "### 🛠️ Refactor"
    first = "extracted spin_once from Widget.spin"
    second = "renamed tmp to angle in spin.py"
    assert first in body and second in body
    assert body.index(first) < body.index(second)
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e["kind"], e["url"]) for e in events] == [("comment", "refactor", url)]


def test_refactor_comment_carries_each_transform_value_without_the_result_label(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://github.com/o/r/issues/7#issuecomment-89")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-refactor.out").write_text(
        "Tidied up.\n"
        "RESULT: extracted spin_once from Widget.spin\n"
        "RESULT: renamed tmp to angle in spin.py\n")

    code, out, err = run_cli(comment, ["7", "refactor"], cwd=tmp_path)

    assert code == 0
    body = posted[0][1]
    assert "extracted spin_once from Widget.spin" in body
    assert "renamed tmp to angle in spin.py" in body
    assert "RESULT:" not in body


def test_refactor_comment_carries_the_transforms_and_leaves_out_the_leafs_other_lines(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://github.com/o/r/issues/7#issuecomment-90")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-refactor.out").write_text(
        "Tidied up.\n"
        "RESULT: extracted spin_once from Widget.spin\n"
        "All suites green afterwards.\n")

    code, out, err = run_cli(comment, ["7", "refactor"], cwd=tmp_path)

    assert code == 0
    body = posted[0][1]
    assert "extracted spin_once from Widget.spin" in body
    assert "Tidied up." not in body
    assert "All suites green afterwards." not in body


def test_refactor_comment_says_no_refactor_warranted_when_the_leaf_reports_nothing_left_to_tidy(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://github.com/o/r/issues/7#issuecomment-91")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-refactor.out").write_text(
        "Looked it over.\n"
        "RESULT: nothing left to tidy\n")

    code, out, err = run_cli(comment, ["7", "refactor"], cwd=tmp_path)

    assert code == 0
    body = posted[0][1]
    assert body.splitlines()[0] == "### 🛠️ Refactor"
    assert "no refactor warranted" in body.splitlines()


def test_refactor_comment_flags_each_overfit_flags_line_and_none_of_another_class_or_none(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://github.com/o/r/issues/7#issuecomment-92")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-refactor.out").write_text(
        "RESULT: renamed tmp to angle in spin.py\n"
        "CANDIDATES: none\n"
        "FLAGS: overfit: spin returns 4 for any input; add a case spinning 5\n"
        "FLAGS: overfit: clamp hardcodes 0; add a case clamping -3\n"
        "FLAGS: beyond-spec: spin also logs\n"
        "FLAGS: none\n")

    code, out, err = run_cli(comment, ["7", "refactor"], cwd=tmp_path)

    assert code == 0
    lines = posted[0][1].splitlines()
    flagged = [line for line in lines if line.startswith("triangulation flagged: ")]
    assert flagged == [
        "triangulation flagged: overfit: spin returns 4 for any input; add a case spinning 5",
        "triangulation flagged: overfit: clamp hardcodes 0; add a case clamping -3",
    ]


def test_refactor_comment_flags_an_overfit_flags_line_in_the_pipe_report_format(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://github.com/o/r/issues/7#issuecomment-93")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-refactor.out").write_text(
        "RESULT: renamed tmp to angle in spin.py\n"
        "FLAGS: overfit | spin.py:12 | test_spin_returns_four\n")

    code, out, err = run_cli(comment, ["7", "refactor"], cwd=tmp_path)

    assert code == 0
    lines = posted[0][1].splitlines()
    assert "triangulation flagged: overfit | spin.py:12 | test_spin_returns_four" in lines


def test_refactor_exits_2_naming_the_missing_develop_refactor_report_posting_and_journaling_nothing(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://example/c/1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()

    code, out, err = run_cli(comment, ["7", "refactor"], cwd=tmp_path)

    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
    assert ".tdd/develop-refactor.out" in err
    assert posted == []
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


def test_refactor_note_file_text_follows_the_rendered_refactor_comment_after_a_blank_line(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://example/c/1")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-refactor.out").write_text("RESULT: renamed tmp to angle in spin.py\n")
    note = tmp_path / "note.txt"
    note.write_text("the conductor note whiskey\n")

    code, out, err = run_cli(comment, ["7", "refactor", "--note-file", str(note)], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    assert posted[0].startswith("### 🛠️ Refactor")
    assert "renamed tmp to angle in spin.py\n\nthe conductor note whiskey" in posted[0]


def test_verify_refactor_pass_posts_the_pass_heading_then_the_reason_and_appends_a_comment_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-93"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verdict-refactor.exit").write_text("0\n")
    (tmp_path / ".tdd" / "verify-refactor.reason").write_text("the transforms keep behaviour and the suite is green\n")

    code, out, err = run_cli(comment, ["7", "verify-refactor"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    number, body = posted[0]
    assert number == "7"
    assert body.splitlines()[0] == "### 🔎 verify-refactor — PASS"
    assert "the transforms keep behaviour and the suite is green" in body.splitlines()[1:]
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e["kind"], e["url"]) for e in events] == [("comment", "verify-refactor", url)]


def test_verify_refactor_reject_posts_the_reject_heading_then_the_reason(monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or "https://github.com/o/r/issues/7#issuecomment-94")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verdict-refactor.exit").write_text("1\n")
    (tmp_path / ".tdd" / "verify-refactor.reason").write_text("the rename changed the public name of spin\n")

    code, out, err = run_cli(comment, ["7", "verify-refactor"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    body = posted[0][1]
    assert body.splitlines()[0] == "### 🔎 verify-refactor — REJECT"
    assert "the rename changed the public name of spin" in body.splitlines()[1:]


def test_verify_revised_posts_the_revised_pass_heading_then_the_reason_and_appends_a_comment_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-95"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verify-green.reason").write_text("the revised implementation now meets the spec\n")

    code, out, err = run_cli(comment, ["7", "verify-revised", "green"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    number, body = posted[0]
    assert number == "7"
    assert body.splitlines()[0] == "### 🔎 verify-green (revised) — PASS"
    assert "the revised implementation now meets the spec" in body.splitlines()[1:]
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e["kind"], e["url"]) for e in events] == [("comment", "verify-revised", url)]


def test_verify_refactor_skipped_posts_the_skipped_heading_without_reading_the_verdict_or_reason_and_appends_a_comment_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-96"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verdict-refactor.exit").write_text("1\n")
    (tmp_path / ".tdd" / "verify-refactor.reason").write_text("a stale reason from an earlier step\n")

    code, out, err = run_cli(comment, ["7", "verify-refactor", "--skipped"], cwd=tmp_path)

    assert code == 0
    assert len(posted) == 1
    number, body = posted[0]
    assert number == "7"
    assert body.splitlines()[0] == "### 🔎 verify-refactor — SKIPPED (nothing landed)"
    assert "a stale reason from an earlier step" not in body
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e["kind"], e["url"]) for e in events] == [("comment", "verify-refactor", url)]


def test_every_heading_comment_sh_posts_for_the_green_refactor_and_revised_kinds_is_classified_by_comment_class_as_the_hand_composed_heading_is(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    comment_class = importlib.import_module("veri.comment_class")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-97")
    (tmp_path / ".git").mkdir()
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "develop-green.out").write_text("IMPL_PATH: src/widget.py\nSUITE: GREEN 42 passed\n")
    (tdd / "develop-refactor.out").write_text("RESULT: extracted spin_once\n")
    (tdd / "verify-green.reason").write_text("fine\n")
    (tdd / "verify-refactor.reason").write_text("fine\n")
    calls = [(["green"], None), (["verify-green"], "0"), (["verify-green"], "1"),
             (["refactor"], None), (["verify-refactor"], "0"), (["verify-refactor"], "1"),
             (["verify-refactor", "--skipped"], None), (["verify-revised", "green"], None)]
    for argv, verdict in calls:
        for phase in ("green", "refactor"):
            (tdd / f"verdict-{phase}.exit").write_text((verdict or "0") + "\n")
        assert run_cli(comment, ["7", *argv], cwd=tmp_path)[0] == 0

    headings = [body.splitlines()[0] for body in posted]
    hand = [
        "### 🟢 Green",
        "### 🔎 verify-green — PASS",
        "### 🔎 verify-green — REJECT",
        "### 🛠️ Refactor",
        "### 🔎 verify-refactor — PASS",
        "### 🔎 verify-refactor — REJECT",
        "### 🔎 verify-refactor — SKIPPED (nothing landed)",
        "### 🔎 verify-green (revised) — PASS",
    ]
    results = []
    for name, lines in (("posted", headings), ("hand", hand)):
        directory = tmp_path / name
        directory.mkdir()
        (directory / "headings.md").write_text("\n".join(lines) + "\n")
        code, out, err = run_cli(comment_class, ["headings.md"], cwd=directory)
        assert code == 0, err
        results.append(out)

    assert results[0] == results[1]


def test_plan_posts_the_plan_heading_listing_every_ledger_step_and_the_detected_test_command_and_appends_a_comment_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    github = importlib.import_module("github")
    url = "https://github.com/o/r/issues/7#issuecomment-42"
    posted = []
    monkeypatch.setattr(github, "gh_issue_comment", lambda number, body: posted.append((str(number), body)) or url)
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: "## Problem\n\nbody of the issue\n")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text(
        "# Plan for #7\n\n- [x] first step alpha\n- [ ] second step bravo\n- [ ] third step charlie\n")
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: fast tests: `bin/detected-fast -q`\n")

    code, out, err = run_cli(comment, ["7", "plan"], cwd=tmp_path, env={"VERI_TEST_CMD": "bin/from-the-environment"})

    assert code == 0
    assert len(posted) == 1
    number, body = posted[0]
    assert number == "7"
    assert body.splitlines()[0] == "### 🗺️ Plan"
    assert body.index("first step alpha") < body.index("second step bravo") < body.index("third step charlie")
    assert "bin/detected-fast -q" in body
    assert "bin/from-the-environment" not in body
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e["kind"], e["url"]) for e in events] == [("comment", "plan", url)]


def test_plan_names_the_test_command_as_plain_text_on_its_own_test_command_line(monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    github = importlib.import_module("github")
    posted = []
    monkeypatch.setattr(github, "gh_issue_comment", lambda number, body: posted.append(body) or "https://x/7#c-1")
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: "## Problem\n\nbody of the issue\n")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [ ] only step\n")
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: fast tests: `bin/detected-fast -q`\n")

    code, out, err = run_cli(comment, ["7", "plan"], cwd=tmp_path)

    assert code == 0, err
    assert [l for l in posted[0].split("\n") if l.startswith("Test command:")] == ["Test command: bin/detected-fast -q"]


def test_verify_plan_pass_posts_the_pass_heading_then_the_reason_and_appends_a_comment_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-77"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verdict-plan.exit").write_text("0\n")
    (tmp_path / ".tdd" / "verify-plan.reason").write_text("every step fits one cycle except step four, which is tight\n")

    code, out, err = run_cli(comment, ["7", "verify-plan"], cwd=tmp_path)

    assert code == 0, err
    assert len(posted) == 1
    number, body = posted[0]
    assert number == "7"
    assert body.splitlines()[0] == "### 🗺️ verify-plan — PASS"
    assert "every step fits one cycle except step four, which is tight" in body.splitlines()[1:]
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e["kind"], e["url"]) for e in events] == [("comment", "verify-plan", url)]


def test_verify_plan_reject_posts_the_reject_heading_then_the_reason(monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-78"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "verdict-plan.exit").write_text("1\n")
    (tmp_path / ".tdd" / "verify-plan.reason").write_text("step three bundles two behaviours\n")

    code, out, err = run_cli(comment, ["7", "verify-plan"], cwd=tmp_path)

    assert code == 0, err
    assert len(posted) == 1
    body = posted[0][1]
    assert body.splitlines()[0] == "### 🗺️ verify-plan — REJECT"
    assert "step three bundles two behaviours" in body.splitlines()[1:]


def test_resuming_posts_the_resuming_heading_naming_the_next_unchecked_step_and_appends_a_comment_event(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    url = "https://github.com/o/r/issues/7#issuecomment-91"
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append((str(number), body)) or url)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text(
        "# Plan for #7\n\n- [x] first step alpha\n- [ ] second step bravo\n- [ ] third step charlie\n")

    code, out, err = run_cli(comment, ["7", "resuming"], cwd=tmp_path)

    assert code == 0, err
    assert len(posted) == 1
    number, body = posted[0]
    assert number == "7"
    assert body.splitlines()[0] == "### ▶️ Resuming"
    assert "second step bravo" in body
    assert "first step alpha" not in body
    assert "third step charlie" not in body
    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["event"], e["kind"], e["url"]) for e in events] == [("comment", "resuming", url)]


def test_resuming_note_file_text_follows_the_rendered_resuming_comment_after_a_blank_line(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-92")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] first step alpha\n- [ ] second step bravo\n")
    note = tmp_path / "note.txt"
    note.write_text("stray paths discarded: scratch/zulu.txt\n")

    code, out, err = run_cli(comment, ["7", "resuming", "--note-file", str(note)], cwd=tmp_path)

    assert code == 0, err
    assert len(posted) == 1
    assert "second step bravo" in posted[0]
    assert posted[0].rstrip("\n").endswith("\n\nstray paths discarded: scratch/zulu.txt")


def test_resuming_with_no_unchecked_step_posts_the_heading_then_the_note_file_text_and_no_step_line(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    posted = []
    monkeypatch.setattr(importlib.import_module("github"), "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-93")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-7.md").write_text("# Plan for #7\n\n- [x] first step alpha\n- [x] second step bravo\n")
    note = tmp_path / "note.txt"
    note.write_text("stray paths discarded: scratch/zulu.txt\n")

    code, out, err = run_cli(comment, ["7", "resuming", "--note-file", str(note)], cwd=tmp_path)

    assert code == 0, err
    assert posted == ["### ▶️ Resuming\n\nstray paths discarded: scratch/zulu.txt\n"]


def test_every_heading_comment_sh_posts_for_plan_verify_plan_and_resuming_is_classified_by_comment_class_as_the_hand_composed_heading_is_and_falls_in_its_metrics_family(
        monkeypatch, run_cli, tmp_path):
    comment = importlib.import_module("veri.comment")
    comment_class = importlib.import_module("veri.comment_class")
    metrics = importlib.import_module("metrics")
    github = importlib.import_module("github")
    posted = []
    monkeypatch.setattr(github, "gh_issue_comment",
                        lambda number, body: posted.append(body) or "https://github.com/o/r/issues/7#issuecomment-99")
    monkeypatch.setattr(github, "gh_issue_view", lambda number, field: "## Problem\n\nbody of the issue\n")
    (tmp_path / ".git").mkdir()
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "issue-7.md").write_text("# Plan for #7\n\n- [x] first step alpha\n- [ ] second step bravo\n")
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: fast tests: `bin/detected-fast -q`\n")
    (tdd / "verify-plan.reason").write_text("fine\n")
    calls = [(["plan"], None), (["verify-plan"], "0"), (["verify-plan"], "1"), (["resuming"], None)]
    for argv, verdict in calls:
        (tdd / "verdict-plan.exit").write_text((verdict or "0") + "\n")
        assert run_cli(comment, ["7", *argv], cwd=tmp_path)[0] == 0

    headings = [body.splitlines()[0] for body in posted]
    hand = [
        "### 🗺️ Plan",
        "### 🗺️ verify-plan — PASS",
        "### 🗺️ verify-plan — REJECT",
        "### ▶️ Resuming",
    ]
    results = []
    for name, lines in (("posted", headings), ("hand", hand)):
        directory = tmp_path / name
        directory.mkdir()
        (directory / "headings.md").write_text("\n".join(lines) + "\n")
        code, out, err = run_cli(comment_class, ["headings.md"], cwd=directory)
        assert code == 0, err
        results.append(out)
    assert results[0] == results[1]

    families = dict(metrics.COMMENT_FAMILIES)
    for heading, hand_heading, family in zip(headings, hand, ["🗺️ Plan", "🗺️ verify-plan", "🗺️ verify-plan", "▶️ Resuming"]):
        assert re.search(families[family], heading)
        assert re.search(families[family], hand_heading)
