"""Cases for park-issue.sh that start a real process."""
import os
import subprocess

import pytest

from conftest import SCRIPTS

GH_STUB = """#!/bin/sh
{
  echo "ARGS: $*"
  for a in "$@"; do [ -f "$a" ] && cat "$a"; done
  [ -t 0 ] || cat
} >> "$GH_LOG" 2>/dev/null
echo '{}'
"""


@pytest.mark.process("park-issue.sh run against a gh stub that records every call")
def test_park_issue_labels_the_issue_parked_and_posts_one_comment_with_the_cause_and_the_unblock(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    log.write_text("")

    ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), "7", "second bail on the verifier", "a human reads the diff"],
                         cwd=tmp_path, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1"})

    recorded = log.read_text()
    assert ran.returncode == 0, ran.stderr
    assert "parked" in recorded
    assert "7" in recorded
    assert recorded.count("### ⏸ Parked") == 1
    assert "### ⏸ Parked\nCause: second bail on the verifier\n" in recorded
    assert "Unblock: a human reads the diff" in recorded


@pytest.mark.process("park-issue.sh run against a gh stub that records every call")
def test_park_issue_with_the_wrong_number_of_arguments_prints_usage_exits_2_and_calls_no_gh(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    log.write_text("")
    env = {"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
           "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1"}

    for args in ([], ["7", "cause"], ["7", "cause", "unblock", "12", "extra"]):
        ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), *args], cwd=tmp_path, capture_output=True,
                             text=True, stdin=subprocess.DEVNULL, env=env)

        assert ran.returncode == 2, (args, ran.stderr)
        assert "usage: park-issue.sh <issue-number> <cause> <unblock> [<pr>]" in ran.stderr
        assert log.read_text() == ""


@pytest.mark.process("park-issue.sh run against a gh stub that records every call")
def test_park_issue_comment_carries_a_pr_line_only_when_given_a_pr(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    env = {"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
           "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1"}

    def park(*args):
        log.write_text("")
        ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), *args], cwd=tmp_path, capture_output=True,
                             text=True, stdin=subprocess.DEVNULL, env=env)
        assert ran.returncode == 0, ran.stderr
        return log.read_text()

    assert "\nPR: 12\n" in park("7", "held for review", "a human merges", "12")
    assert "PR:" not in park("7", "held for review", "a human merges")



LABEL_STATE_GH_STUB = """#!/bin/sh
echo "ARGS: $*" >> "$GH_LOG"
for a in "$@"; do
  case "$a" in
    */issues/*/labels)
      [ -f "$GH_LABEL_CREATED" ] || { echo "label parked not found" >&2; exit 1; }
      touch "$GH_ISSUE_LABELLED"; echo '{}'; exit 0 ;;
    */labels/parked)
      [ -f "$GH_LABEL_CREATED" ] || { echo "HTTP 404: Not Found" >&2; exit 1; }
      echo '{}'; exit 0 ;;
  esac
done
for a in "$@"; do
  case "$a" in
    label|*/labels) touch "$GH_LABEL_CREATED"; echo '{}'; exit 0 ;;
  esac
done
echo '{}'
"""


@pytest.mark.process("park-issue.sh run against a gh stub whose repository starts without the parked label")
def test_park_issue_creates_the_parked_label_when_the_repository_lacks_it_then_labels_the_issue_and_exits_0(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(LABEL_STATE_GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    log.write_text("")
    created = tmp_path / "repo-has-parked-label"
    labelled = tmp_path / "issue-7-labelled-parked"

    ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), "7", "held for review", "a human merges"],
                         cwd=tmp_path, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "GH_LOG": str(log), "GH_LABEL_CREATED": str(created),
                              "GH_ISSUE_LABELLED": str(labelled), "PYTHONDONTWRITEBYTECODE": "1"})

    assert created.exists(), "no call created the parked label:\n" + log.read_text()
    assert labelled.exists(), "the issue was never labelled parked:\n" + log.read_text()
    assert ran.returncode == 0, ran.stderr


@pytest.mark.process("park-issue.sh run against a gh stub that records every call")
def test_park_issue_with_a_bad_argument_exits_2_naming_which_argument_and_calls_no_gh(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    log.write_text("")
    env = {"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
           "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1"}

    for args, named in ((["seven", "cause", "unblock"], "issue number"),
                        (["7", "", "unblock"], "cause"),
                        (["7", "cause", ""], "unblock"),
                        (["7", "cause", "unblock", "12", "extra"], "too many")):
        ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), *args], cwd=tmp_path, capture_output=True,
                             text=True, stdin=subprocess.DEVNULL, env=env)

        assert ran.returncode == 2, (args, ran.stderr)
        assert named in ran.stderr, (args, ran.stderr)
        assert log.read_text() == "", args


UNANSWERED_GH_STUB = """#!/bin/sh
for a in "$@"; do
  case "$a" in
    */comments) exit 1 ;;
  esac
done
echo '{}'
"""


@pytest.mark.process("park-issue.sh run against a gh stub that gives no answer to the comment call")
def test_park_issue_exits_2_naming_the_comment_call_when_gh_gives_no_answer_to_it(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(UNANSWERED_GH_STUB)
    gh.chmod(0o755)

    ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), "7", "held for review", "a human merges"],
                         cwd=tmp_path, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 2, ran.stderr
    assert "comment" in ran.stderr, ran.stderr


UNANSWERED_LABEL_GH_STUB = """#!/bin/sh
for a in "$@"; do
  case "$a" in
    */labels) exit 1 ;;
  esac
done
echo '{}'
"""


@pytest.mark.process("park-issue.sh run against a gh stub that gives no answer to the label call")
def test_park_issue_exits_2_naming_the_label_call_when_gh_gives_no_answer_to_it(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(UNANSWERED_LABEL_GH_STUB)
    gh.chmod(0o755)

    ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), "7", "held for review", "a human merges"],
                         cwd=tmp_path, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 2, ran.stderr
    assert "label call" in ran.stderr, ran.stderr


ALREADY_PARKED_GH_STUB = """#!/bin/sh
echo "ARGS: $*" >> "$GH_LOG"
for a in "$@"; do
  case "$a" in
    */issues/*/comments) cat >> "$GH_LOG" 2>/dev/null; echo '{}'; exit 0 ;;
    */issues/*/labels) echo '[{"name":"parked"}]'; exit 0 ;;
    */labels) echo '{"message":"Validation Failed","errors":[{"code":"already_exists"}]}' >&2; exit 1 ;;
  esac
done
echo '{}'
"""


@pytest.mark.process("park-issue.sh run against a gh stub whose issue already carries the parked label")
def test_park_issue_on_an_issue_already_labelled_parked_posts_the_new_comment_and_exits_0(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(ALREADY_PARKED_GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    log.write_text("")

    ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), "7", "second park, new cause", "a human reads the diff"],
                         cwd=tmp_path, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1"})

    recorded = log.read_text()
    assert ran.returncode == 0, ran.stderr
    assert recorded.count("### ⏸ Parked\nCause: second park, new cause\n") == 1, recorded


@pytest.mark.process("park-issue.sh run against a gh stub that records every call")
def test_park_issue_refuses_the_issue_number_0_exiting_2_naming_the_number_and_calls_no_gh(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    log.write_text("")

    ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), "0", "held for review", "a human merges"],
                         cwd=tmp_path, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 2, ran.stderr
    assert "0" in ran.stderr, ran.stderr
    assert log.read_text() == ""


@pytest.mark.process("park-issue.sh run against a gh stub that records every call")
def test_park_issue_refuses_an_issue_number_with_a_non_ascii_digit_exiting_2_naming_the_number_and_calls_no_gh(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(GH_STUB)
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    env = {"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
           "GH_LOG": str(log), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}

    for number in ("١٢", "１２"):
        log.write_text("")
        ran = subprocess.run([str(SCRIPTS / "park-issue.sh"), number, "held for review", "a human merges"],
                             cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
                             stdin=subprocess.DEVNULL, env=env)

        assert ran.returncode == 2, (number, ran.stderr)
        assert number in ran.stderr, (number, ran.stderr)
        assert log.read_text() == "", number
