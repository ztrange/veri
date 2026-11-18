"""Cases for pr-checks.sh (PRD 038.8, #4392) that start a real process: the shim's usage and its refusal of a missing
input, exec'd on the interpreter."""
import subprocess

import pytest

from conftest import SCRIPTS


def shim(*args, cwd):
    return subprocess.run([str(SCRIPTS / "pr-checks.sh"), *args], cwd=cwd, stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=60)


@pytest.mark.process("pr-checks.sh's /bin/sh shim exec'd on the interpreter with no argument")
def test_4392_the_shim_with_no_argument_prints_its_usage_and_exits_2(tmp_path):
    ran = shim(cwd=tmp_path)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: pr-checks.sh <n>\n")


@pytest.mark.process("pr-checks.sh's /bin/sh shim exec'd on the interpreter with no preflight file")
def test_4392_the_shim_with_no_preflight_exits_2_naming_it(tmp_path):
    ran = shim("12", cwd=tmp_path)

    assert (ran.returncode, ran.stdout) == (2, "")
    assert ".tdd/issue-12-preflight" in ran.stderr
