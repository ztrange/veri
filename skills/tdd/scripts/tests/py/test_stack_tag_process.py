"""Entry-point contract case for stack-tag.sh (PRD 034.4c, #4319)."""
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("stack-tag.sh's /bin/sh shim exec'd on the interpreter with no argument")
def test_4319_no_argument_exits_2_with_the_usage_line(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "stack-tag.sh")], cwd=tmp_path, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (
        2, "", "usage: stack-tag.sh <slice-pr-url> [--message <n>=<text>]...\n")
