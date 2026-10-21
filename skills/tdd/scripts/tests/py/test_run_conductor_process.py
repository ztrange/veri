"""Cases for run-conductor.sh that start a real process."""
import os
import subprocess
import sys

import pytest

from conftest import SCRIPTS


@pytest.mark.process("run-conductor.sh run as a real shim over veri/run_conductor.py, refusing an empty issue before any fetch")
def test_run_conductor_sh_with_an_empty_issue_forwards_it_to_the_module_and_returns_2_with_the_usage_line_alone(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "run-conductor.sh"), ""], cwd=tmp_path, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_BASH_MAJOR": "5",
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: run-conductor.sh <issue>\n")
