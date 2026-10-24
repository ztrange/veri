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
