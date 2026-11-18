"""Entry-point contract case for stack-land.sh (PRD 034.4a, #4317)."""
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("stack-land.sh's /bin/sh shim exec'd on the interpreter with a commit name for an argument")
def test_4317_any_argument_other_than_now_exits_2_with_the_usage_line(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "stack-land.sh"), "abc1234"], cwd=tmp_path, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: stack-land.sh [--now]\n")
