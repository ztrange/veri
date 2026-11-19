"""Cases for revise.sh (PRD 038.9) that start a real process: the shim's usage."""
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("revise.sh's /bin/sh shim exec'd on the interpreter with no argument")
def test_the_shim_with_no_argument_prints_its_usage_and_exits_2_4433(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "revise.sh")], cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True,
                         text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (
        2, "", "usage: revise.sh <n> <phase>  (phase: red, green, refactor or diff)\n")
