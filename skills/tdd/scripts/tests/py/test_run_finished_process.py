"""Cases for run-finished.sh's done, not-done and no-answer verdicts, run as the real entry point."""
import json
import os
import subprocess
import time

import pytest

from conftest import SCRIPTS

FINISHED = str(SCRIPTS / "run-finished.sh")
LAUNCH = '{"ts":%s,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}'
DONE = '{"ts":1001,"event":"done","pr":"https://github.com/o/r/pull/7"}'
STEP = "- [x] first step ⟦criterion 1⟧\n"


def git_init(path):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    for key, value in (("user.name", "Test"), ("user.email", "test@example.com")):
        subprocess.run(["git", "-C", str(path), "config", key, value], check=True)


def make_run(tmp_path, events, steps=STEP):
    repo = tmp_path / "repo"
    git_init(repo)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "--allow-empty", "-m", "init"], check=True)
    run = repo / ".tdd" / "wt" / "4242"
    git_init(run)
    (run / ".tdd").mkdir(exist_ok=True)
    (run / ".tdd" / "events.jsonl").write_text("".join(e + "\n" for e in events))
    (run / ".tdd" / "issue-4242.md").write_text("# Plan for #4242 — a title\n\n" + steps)
    return repo


def finish(repo, tmp_path, body=None):
    env = dict(os.environ)
    if body is not None:
        bin = tmp_path / "bin"
        bin.mkdir()
        (bin / "body").write_text(json.dumps({"body": body}))
        (bin / "gh").write_text('#!/bin/sh\ncat "$(dirname "$0")/body"\n')
        (bin / "gh").chmod(0o755)
        env["PATH"] = "%s:%s" % (bin, env["PATH"])
    ran = subprocess.run([FINISHED, "4242"], cwd=repo, capture_output=True, text=True, env=env)
    return ran.returncode, ran.stdout, ran.stderr


@pytest.mark.process("run-finished.sh on a repository with no run under .tdd/wt/")
def test_an_issue_with_no_run_exits_2_and_says_on_stderr_there_is_no_run_for_it(tmp_path):
    repo = tmp_path / "repo"
    git_init(repo)
    (repo / ".tdd" / "wt").mkdir(parents=True)

    code, _, err = finish(repo, tmp_path)

    assert code == 2
    assert "no run for issue 4242" in err


def assert_done_and_silent(tmp_path, body, steps=STEP):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE], steps)

    assert finish(repo, tmp_path, body) == (0, "", "")


def assert_not_done(tmp_path, events, state):
    repo = make_run(tmp_path, events)

    code, out, _ = finish(repo, tmp_path)

    assert code == 1
    assert out.startswith("not-done %s" % state)


@pytest.mark.process("run-finished.sh on a done run, with a fake gh answering the PR body")
def test_a_done_run_with_every_step_ticked_and_its_human_owed_line_ticked_exits_0_and_prints_nothing(tmp_path):
    assert_done_and_silent(
        tmp_path, "Closes #4242\n\n- [x] a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧",
        STEP + "- [x] second step ⟦criterion 2⟧\n")


@pytest.mark.process("run-finished.sh on a done run, with a fake gh answering the PR body")
def test_a_done_run_whose_pr_body_holds_an_unticked_checkbox_that_is_not_human_owed_exits_0_and_prints_nothing(
        tmp_path):
    assert_done_and_silent(tmp_path, "Closes #4242\n\n- [ ] a follow-up someone may file later")


@pytest.mark.process("run-finished.sh on a done run, with a fake gh answering the PR body")
def test_a_done_run_whose_pr_body_holds_star_bulleted_and_indented_checkboxes_exits_0_and_prints_nothing(tmp_path):
    assert_done_and_silent(
        tmp_path,
        "Closes #4242\n\n* [ ] a star-bulleted follow-up someone may file later\n"
        "  - [ ] an indented follow-up someone may file later\n"
        "  - [x] a reviewer checked the indented page ⟦human-owed⟧ ⟦criterion 3⟧")


@pytest.mark.process("run-finished.sh on a stopped run")
def test_a_stopped_run_with_a_clean_ledger_exits_1_and_prints_a_not_done_line_naming_stopped(tmp_path):
    assert_not_done(tmp_path, [LAUNCH % 1000, '{"ts":1001,"event":"stop","mode":"graceful"}'], "stopped")


@pytest.mark.process("run-finished.sh on a bailed run")
def test_a_run_whose_state_is_not_done_exits_1_and_prints_a_not_done_line_naming_the_state(tmp_path):
    assert_not_done(
        tmp_path, [LAUNCH % 1000, '{"ts":1001,"event":"bail","phase":"red","classification":"process"}'],
        "bailed")


@pytest.mark.process("run-finished.sh on a stale run")
def test_a_stale_run_exits_1_and_prints_a_not_done_line_naming_the_stale_state(tmp_path):
    assert_not_done(tmp_path, [LAUNCH % 1000], "stale")


@pytest.mark.process("run-finished.sh on a running run")
def test_a_running_run_exits_1_and_prints_a_not_done_line_naming_the_running_state(tmp_path):
    assert_not_done(tmp_path, [LAUNCH % int(time.time())], "running")


@pytest.mark.process("run-finished.sh on a done run whose ledger has unchecked steps, with a fake gh")
def test_a_done_run_whose_ledger_has_unchecked_steps_exits_1_and_prints_one_unchecked_line_per_step(tmp_path):
    steps = STEP + "- [ ] second step ⟦criterion 2⟧\n- [ ] third step ⟦criterion 3⟧\n"
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE], steps)

    code, out, _ = finish(repo, tmp_path, "Closes #4242")

    lines = out.splitlines()
    assert code == 1
    assert len(lines) == 2
    assert lines[0].startswith("unchecked ") and "second step" in lines[0]
    assert lines[1].startswith("unchecked ") and "third step" in lines[1]
    assert "first step" not in out
