"""The entry-point contract of issue-decisions.sh, through a real process; its logic is tested in-process, in
tests/py/unit/test_issue_decisions.py."""
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("issue-decisions.sh run with bad arguments, so no gh is reached")
def test_the_shim_passes_exit_2_and_the_usage_through_for_a_bad_issue_number(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "issue-decisions.sh"), "x1"], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: issue-decisions.sh <issue-number>\n")
