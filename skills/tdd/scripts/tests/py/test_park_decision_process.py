"""The entry-point contract of park-decision.sh, through a real process; its logic is tested in-process, in
tests/py/unit/test_park_decision.py."""
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("park-decision.sh run with bad arguments, so no gh is reached")
def test_the_shim_passes_exit_2_and_the_usage_through_for_a_bad_issue_number(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "park-decision.sh"), "x1"], cwd=tmp_path, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: park-decision.sh <issue-number>\n")
