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


TRAILING_COMMENT_GH_STUB = """#!/bin/sh
for a in "$@"; do
  case "$a" in
    *page=[2-9]*) echo '[]'; exit 0 ;;
    */issues/7/comments*)
      echo '[{"body":"### ⏸ Parked\\nCause: second bail on the verifier\\nUnblock: a human reads the diff"},{"body":"Still waiting on the human."}]'
      exit 0 ;;
    */issues*)
      echo '[{"number":7,"title":"Teach the verifier to refuse","labels":[{"name":"parked"}]}]'
      exit 0 ;;
  esac
done
echo '[]'
"""


@pytest.mark.process("parked-issues.sh run against a gh stub whose parked issue ends with a non-parked comment")
def test_parked_issues_when_the_final_comment_is_not_a_parked_comment_still_prints_the_cause_and_unblock_of_the_parked_comment(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(TRAILING_COMMENT_GH_STUB)
    gh.chmod(0o755)

    ran = subprocess.run([str(SCRIPTS / "parked-issues.sh")], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 0, ran.stderr
    assert ran.stdout == "7\tTeach the verifier to refuse\tsecond bail on the verifier\ta human reads the diff\n"


SEVERAL_PARKED_GH_STUB = """#!/bin/sh
for a in "$@"; do
  case "$a" in
    *page=[2-9]*) echo '[]'; exit 0 ;;
    */issues/7/comments*)
      echo '[{"body":"### ⏸ Parked\\nCause: first bail\\nUnblock: old"},{"body":"chatter"},{"body":"### ⏸ Parked\\nCause: held PR\\nUnblock: the human merges"},{"body":"### ⏸ Parked\\nCause: third bail\\nUnblock: fix the fixture"},{"body":"Still waiting."}]'
      exit 0 ;;
    */issues*)
      echo '[{"number":7,"title":"Teach the verifier to refuse","labels":[{"name":"parked"}]}]'
      exit 0 ;;
  esac
done
echo '[]'
"""


@pytest.mark.process("parked-issues.sh run against a gh stub whose parked issue carries three parked comments")
def test_parked_issues_when_an_issue_carries_several_parked_comments_prints_the_cause_and_unblock_of_the_latest(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(SEVERAL_PARKED_GH_STUB)
    gh.chmod(0o755)

    ran = subprocess.run([str(SCRIPTS / "parked-issues.sh")], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 0, ran.stderr
    assert ran.stdout == "7\tTeach the verifier to refuse\tthird bail\tfix the fixture\n"


@pytest.mark.process("parked-issues.sh run against a gh stub serving no issue at all")
def test_parked_issues_with_no_open_issue_labelled_parked_prints_nothing_and_exits_3(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text("#!/bin/sh\necho '[]'\n")
    gh.chmod(0o755)

    ran = subprocess.run([str(SCRIPTS / "parked-issues.sh")], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 3, ran.stderr
    assert ran.stdout == ""


UNANSWERED_LISTING_GH_STUB = """#!/bin/sh
exit 1
"""


@pytest.mark.process("parked-issues.sh run against a gh stub that gives no answer to listing the issues")
def test_parked_issues_exits_2_naming_the_listing_call_when_gh_gives_no_answer_to_it(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(UNANSWERED_LISTING_GH_STUB)
    gh.chmod(0o755)

    ran = subprocess.run([str(SCRIPTS / "parked-issues.sh")], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 2, ran.stderr
    assert "listing the issues" in ran.stderr, ran.stderr


UNANSWERED_COMMENTS_GH_STUB = """#!/bin/sh
for a in "$@"; do
  case "$a" in
    *page=[2-9]*) echo '[]'; exit 0 ;;
    */issues/7/comments*) exit 1 ;;
    */issues*)
      echo '[{"number":7,"title":"Teach the verifier to refuse","labels":[{"name":"parked"}]}]'
      exit 0 ;;
  esac
done
echo '[]'
"""


@pytest.mark.process("parked-issues.sh run against a gh stub that lists an issue but gives no answer to reading its comments")
def test_parked_issues_exits_2_naming_the_comments_call_when_gh_answers_the_listing_but_not_an_issues_comments(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(UNANSWERED_COMMENTS_GH_STUB)
    gh.chmod(0o755)

    ran = subprocess.run([str(SCRIPTS / "parked-issues.sh")], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 2, ran.stderr
    assert "reading the comments" in ran.stderr, ran.stderr


TWO_PAGES_OF_COMMENTS_GH_STUB = """#!/bin/sh
for a in "$@"; do
  case "$a" in
    */issues/7/comments*page=1) echo '[{"body":"chatter on page one"}]'; exit 0 ;;
    */issues/7/comments*page=2)
      echo '[{"body":"### ⏸ Parked\\nCause: bail found on page two\\nUnblock: a human reads page two"}]'
      exit 0 ;;
    *page=[3-9]*) echo '[]'; exit 0 ;;
    */issues*page=1)
      echo '[{"number":7,"title":"Teach the verifier to refuse","labels":[{"name":"parked"}]}]'
      exit 0 ;;
  esac
done
echo '[]'
"""


@pytest.mark.process("parked-issues.sh run against a gh stub serving a parked issue's comments over two pages")
def test_parked_issues_reads_the_parked_comment_served_on_the_second_page_of_an_issues_comments(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(TWO_PAGES_OF_COMMENTS_GH_STUB)
    gh.chmod(0o755)

    ran = subprocess.run([str(SCRIPTS / "parked-issues.sh")], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 0, ran.stderr
    assert ran.stdout == "7\tTeach the verifier to refuse\tbail found on page two\ta human reads page two\n"


TWO_PAGES_OF_LISTING_GH_STUB = """#!/bin/sh
for a in "$@"; do
  case "$a" in
    */issues/7/comments*page=1)
      echo '[{"body":"### ⏸ Parked\\nCause: bail on the first page\\nUnblock: a human reads page one"}]'
      exit 0 ;;
    */issues/8/comments*page=1)
      echo '[{"body":"### ⏸ Parked\\nCause: held PR on the second page\\nUnblock: the human merges"}]'
      exit 0 ;;
    */comments*) echo '[]'; exit 0 ;;
    */issues*page=1)
      echo '[{"number":7,"title":"Teach the verifier to refuse","labels":[{"name":"parked"}]}]'
      exit 0 ;;
    */issues*page=2)
      echo '[{"number":8,"title":"Hold the PR","labels":[{"name":"parked"}]}]'
      exit 0 ;;
  esac
done
echo '[]'
"""


@pytest.mark.process("parked-issues.sh run against a gh stub serving the parked listing over two pages")
def test_parked_issues_prints_the_parked_issue_served_on_the_second_page_of_the_listing(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(TWO_PAGES_OF_LISTING_GH_STUB)
    gh.chmod(0o755)

    ran = subprocess.run([str(SCRIPTS / "parked-issues.sh")], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 0, ran.stderr
    assert ran.stdout == ("7\tTeach the verifier to refuse\tbail on the first page\ta human reads page one\n"
                          "8\tHold the PR\theld PR on the second page\tthe human merges\n")


NO_PARKED_COMMENT_GH_STUB = """#!/bin/sh
for a in "$@"; do
  case "$a" in
    */issues/7/comments*page=1)
      echo '[{"body":"### ⏸ Parked\\nCause: bail on the verifier\\nUnblock: a human reads the diff"}]'
      exit 0 ;;
    */issues/8/comments*page=1) echo '[{"body":"just chatter"}]'; exit 0 ;;
    */comments*) echo '[]'; exit 0 ;;
    */issues*page=1)
      echo '[{"number":7,"title":"Teach the verifier to refuse","labels":[{"name":"parked"}]},{"number":8,"title":"Hold the PR","labels":[{"name":"parked"}]}]'
      exit 0 ;;
  esac
done
echo '[]'
"""


@pytest.mark.process("parked-issues.sh run against a gh stub whose second parked issue has no parked comment")
def test_parked_issues_when_a_parked_issue_has_no_parked_comment_exits_2_naming_it_after_printing_the_issues_before_it(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(NO_PARKED_COMMENT_GH_STUB)
    gh.chmod(0o755)

    ran = subprocess.run([str(SCRIPTS / "parked-issues.sh")], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert "#8" in ran.stderr, ran.stderr
    assert ran.stdout == "7\tTeach the verifier to refuse\tbail on the verifier\ta human reads the diff\n"
    assert ran.returncode == 2, ran.stderr
