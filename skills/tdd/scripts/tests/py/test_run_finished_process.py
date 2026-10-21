"""Cases for run-finished.sh's done, not-done and no-answer verdicts, run as the real entry point."""
import json
import os
import re
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


def fake_gh(tmp_path, script):
    bin = tmp_path / "bin"
    bin.mkdir(exist_ok=True)
    (bin / "gh").write_text("#!/bin/sh\n" + script)
    (bin / "gh").chmod(0o755)
    return {**os.environ, "PATH": "%s:%s" % (bin, os.environ["PATH"])}


def finish_with_gh(repo, tmp_path, script):
    env = fake_gh(tmp_path, script)
    ran = subprocess.run([FINISHED, "4242"], cwd=repo, capture_output=True, text=True, env=env)
    return ran.returncode, ran.stdout, ran.stderr


def finish(repo, tmp_path, body=None):
    if body is None:
        ran = subprocess.run([FINISHED, "4242"], cwd=repo, capture_output=True, text=True)
        return ran.returncode, ran.stdout, ran.stderr
    (tmp_path / "body").write_text(json.dumps({"body": body}))
    return finish_with_gh(repo, tmp_path, 'cat "%s"\n' % (tmp_path / "body"))


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


@pytest.mark.process("run-finished.sh on a done run whose ledger has refactor-pending steps, with a fake gh")
def test_a_done_run_whose_ledger_has_a_step_still_refactor_pending_exits_1_and_prints_one_refactor_pending_line_per_such_step(
        tmp_path):
    steps = (STEP + "- [x] second step ⟦criterion 2⟧ ⟂ refactor pending\n"
             "- [x] third step ⟦criterion 3⟧ ⟂ refactor pending\n")
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE], steps)

    code, out, _ = finish(repo, tmp_path, "Closes #4242")

    lines = out.splitlines()
    assert code == 1
    assert len(lines) == 2
    assert lines[0].startswith("refactor-pending ") and "second step" in lines[0]
    assert lines[1].startswith("refactor-pending ") and "third step" in lines[1]
    assert "first step" not in out


@pytest.mark.process("run-finished.sh on a done run whose PR body holds unticked human-owed lines, with a fake gh")
def test_a_done_run_whose_pr_body_holds_unticked_human_owed_lines_exits_1_and_prints_one_human_owed_line_per_unticked_line(
        tmp_path):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])
    body = ("Closes #4242\n\n- [ ] a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧\n"
            "- [x] a reviewer checks the ticked one ⟦human-owed⟧ ⟦criterion 4⟧\n"
            "- [ ] a reviewer reads the docs ⟦human-owed⟧ ⟦criterion 5⟧")

    code, out, _ = finish(repo, tmp_path, body)

    lines = out.splitlines()
    assert code == 1
    assert len(lines) == 2
    assert lines[0].startswith("human-owed ") and "checks the page" in lines[0]
    assert lines[1].startswith("human-owed ") and "reads the docs" in lines[1]
    assert "ticked one" not in out


@pytest.mark.process("run-finished.sh on a done run whose gh fails, with a fake gh")
def test_a_done_run_whose_pr_body_cannot_be_read_exits_2_and_says_on_stderr_the_pr_body_could_not_be_read(tmp_path):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])

    code, _, err = finish_with_gh(repo, tmp_path, 'echo "gh: HTTP 502" >&2\nexit 1\n')

    assert code == 2
    assert "PR body" in err


def tree_digest(repo):
    files = {}
    for path in sorted(repo.rglob("*")):
        if ".git" in path.relative_to(repo).parts or not path.is_file():
            continue
        files[str(path)] = path.read_bytes()
    git = []
    for where in (repo, repo / ".tdd" / "wt" / "4242"):
        for args in (["for-each-ref"], ["config", "--list", "--local"], ["status", "--porcelain"]):
            git.append(subprocess.run(["git", "-C", str(where)] + args, capture_output=True, text=True).stdout)
    return files, git


@pytest.mark.process("run-finished.sh on a done run, with a fake gh recording its calls")
def test_a_run_of_it_changes_no_file_in_the_repository_and_every_gh_call_it_makes_is_a_read(tmp_path):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE], STEP + "- [ ] second step ⟦criterion 2⟧\n")
    calls = tmp_path / "calls"
    script = 'echo "$*" >> "%s"\nprintf \'{"body": "Closes #4242"}\\n\'\n' % calls
    env = fake_gh(tmp_path, script)
    before = tree_digest(repo)

    subprocess.run([FINISHED, "4242"], cwd=repo, capture_output=True, text=True, env=env)

    assert tree_digest(repo) == before
    made = calls.read_text().splitlines()
    assert made
    for call in made:
        assert call.startswith("pr view ") or re.fullmatch(r"api repos/\S+/pulls/\d+", call)
        for write in ("POST", "PATCH", "PUT", "DELETE", "-X", "--method", "--input", "-f ", "-F "):
            assert write.lower() not in call.lower()


@pytest.mark.process("run-finished.sh on a done run with an empty recorded PR URL, with a fake gh recording its calls")
def test_a_done_run_with_an_empty_recorded_pr_url_exits_2_with_one_stderr_line_saying_no_pr_is_recorded_and_never_calls_gh_pr_view(
        tmp_path):
    repo = make_run(tmp_path, [LAUNCH % 1000, '{"ts":1001,"event":"done","pr":""}'])
    calls = tmp_path / "calls"

    code, _, err = finish_with_gh(repo, tmp_path, 'echo "$*" >> "%s"\necho \'{"body": "Closes #4242"}\'\n' % calls)

    assert code == 2
    assert "no PR" in err
    assert len(err.splitlines()) == 1
    assert not calls.exists()


@pytest.mark.process("run-finished.sh on a done run whose PR body holds an indented unticked human-owed checkbox, with a fake gh")
def test_a_done_run_whose_pr_body_holds_an_indented_unticked_human_owed_checkbox_exits_1_and_prints_its_human_owed_line(
        tmp_path):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])

    code, out, _ = finish(
        repo, tmp_path, "Closes #4242\n\n  - [ ] a reviewer checks the nested page ⟦human-owed⟧ ⟦criterion 3⟧")

    assert code == 1
    assert out.startswith("human-owed ") and "checks the nested page" in out


@pytest.mark.process("run-finished.sh on a done run whose PR body holds a star-bulleted unticked human-owed checkbox, with a fake gh")
def test_a_done_run_whose_pr_body_holds_a_star_bulleted_unticked_human_owed_checkbox_exits_1_and_prints_its_human_owed_line(
        tmp_path):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])

    code, out, _ = finish(
        repo, tmp_path, "Closes #4242\n\n* [ ] a reviewer checks the starred page ⟦human-owed⟧ ⟦criterion 3⟧")

    assert code == 1
    assert out.startswith("human-owed ") and "checks the starred page" in out


@pytest.mark.process("run-finished.sh on a done run whose ledger file is missing, with a fake gh")
def test_a_done_run_whose_ledger_is_missing_exits_2_with_one_stderr_line_naming_the_file_and_no_traceback(tmp_path):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])
    (repo / ".tdd" / "wt" / "4242" / ".tdd" / "issue-4242.md").unlink()

    code, _, err = finish(repo, tmp_path, "Closes #4242")

    assert code == 2
    assert "issue-4242.md" in err
    assert len(err.splitlines()) == 1
    assert "Traceback" not in err
