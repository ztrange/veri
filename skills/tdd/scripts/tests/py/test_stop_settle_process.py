"""Cases for stop-settle.sh (PRD 038.5, #4388) that start a real process: the shim's usage."""
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("stop-settle.sh's /bin/sh shim exec'd on the interpreter with no argument")
def test_4388_the_shim_with_no_argument_prints_its_usage_and_exits_2(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "stop-settle.sh")], cwd=tmp_path, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: stop-settle.sh <n> <mode> [--drop]\n")
