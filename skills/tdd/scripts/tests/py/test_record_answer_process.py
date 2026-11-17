"""The entry-point contract of record-answer.sh, through a real process and a gh stub that records every call; its
logic is tested in-process, in tests/py/unit/test_record_answer.py."""
import subprocess

import pytest

from conftest import INTERPRETER_VENV, SCRIPTS
from stub_script import write_stub

# Answers a comments read with no comments and a post with a record; logs every call's arguments, one per line.
GH = """for a in "$@"; do printf '%s\\n' "$a"; done >> "$GH_LOG"
echo ---- >> "$GH_LOG"
case "$*" in
  *POST*) echo '{}' ;;
  *) echo '[]' ;;
esac
"""


def run(tmp_path, *argv):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(str(bin_dir / "gh"), GH)
    (tmp_path / "gh.log").write_text("")
    (tmp_path / "work").mkdir()
    ran = subprocess.run([str(SCRIPTS / "record-answer.sh"), *argv], cwd=tmp_path / "work", capture_output=True, text=True,
                         stdin=subprocess.DEVNULL,
                         env={"PATH": "%s:/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin" % bin_dir,
                              "HOME": str(tmp_path / "home"), "VERI_VENV": INTERPRETER_VENV, "GH_LOG": str(tmp_path / "gh.log"),
                              "PYTHONDONTWRITEBYTECODE": "1"})
    return ran.returncode, ran.stdout, ran.stderr, (tmp_path / "gh.log").read_text()


@pytest.mark.process("record-answer.sh run against a gh stub that records every call")
def test_issue_4252_the_shim_posts_the_redacted_answer_through_gh_and_exits_0(tmp_path):
    question = tmp_path / "main-7.md"
    question.write_text("#### Question\n\nKeep %s/notes?\n\n#### Options\n\n## Answer\n\nYes.\n" % (tmp_path / "home"))

    code, out, err, log = run(tmp_path, "7", str(question))

    assert (code, out, err) == (0, "", "")
    assert "\nbody=Question: Keep <tmp>/" in log and log.endswith("/notes?\n\nOwner's answer: Yes.\n----\n")
    assert str(tmp_path) not in log


@pytest.mark.process("record-answer.sh run with bad arguments, so no gh is reached")
def test_issue_4252_the_shim_passes_exit_2_and_the_usage_through_for_a_bad_issue_number(tmp_path):
    code, out, err, log = run(tmp_path, "x7", "q.md")

    assert (code, out, err, log) == (2, "", "usage: record-answer.sh <issue-number> <question-file>\n", "")
