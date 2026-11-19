"""Cases for diff-step.sh (PRD 038.3, #4435) that start a real process: the shim's usage."""
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("diff-step.sh's /bin/sh shim exec'd on the interpreter with no argument")
def test_4435_the_shim_with_no_argument_prints_its_usage_and_exits_2(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "diff-step.sh")], cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True,
                         text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: diff-step.sh <n>\n")
