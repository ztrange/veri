"""Cases for parked-issues.sh that start a real process."""
import subprocess

import pytest

from conftest import SCRIPTS

PARKED_SET_GH_STUB = """#!/bin/sh
for a in "$@"; do
  case "$a" in
    *page=[2-9]*) echo '[]'; exit 0 ;;
    */issues/7/comments*)
      echo '[{"body":"### ⏸ Parked\\nCause: first bail\\nUnblock: old"},{"body":"### ⏸ Parked\\nCause: second bail on the verifier\\nUnblock: a human reads the diff"}]'
      exit 0 ;;
    */issues*)
      echo '[{"number":7,"title":"Teach the verifier to refuse","labels":[{"name":"parked"}]}]'
      exit 0 ;;
  esac
done
echo '[]'
"""


@pytest.mark.process("parked-issues.sh run against a gh stub serving one parked issue and its comments")
def test_parked_issues_prints_one_tab_separated_line_per_parked_issue_with_the_cause_and_unblock_of_its_parked_comment_and_exits_0(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(PARKED_SET_GH_STUB)
    gh.chmod(0o755)

    ran = subprocess.run([str(SCRIPTS / "parked-issues.sh")], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 0, ran.stderr
    assert ran.stdout == "7\tTeach the verifier to refuse\tsecond bail on the verifier\ta human reads the diff\n"


@pytest.mark.process("parked-issues.sh run with an argument against a gh stub that records every call")
def test_parked_issues_given_any_argument_prints_its_usage_line_on_stderr_and_exits_2_without_calling_gh(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    called = tmp_path / "gh-called"
    gh = bin_dir / "gh"
    gh.write_text("#!/bin/sh\necho called >> '%s'\necho '[]'\n" % called)
    gh.chmod(0o755)

    ran = subprocess.run([str(SCRIPTS / "parked-issues.sh"), "--all"], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 2, ran.stderr
    assert "usage: parked-issues.sh" in ran.stderr
    assert ran.stdout == ""
    assert not called.exists()
