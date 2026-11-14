"""Cases for branch-suite.sh that start the real entry point."""
import os
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("branch-suite.sh, a /bin/sh shim over veri/branch_suite.py, run as a subprocess with the mode given")
def test_branch_suite_prints_the_mode_it_is_given_and_exits_0_and_exits_2_on_any_other(tmp_path):
    for mode in ("ci", "local"):
        ran = subprocess.run([str(SCRIPTS / "branch-suite.sh")], cwd=tmp_path, capture_output=True, text=True,
                             env={**os.environ, "VERI_BRANCH_SUITE": mode})

        assert (ran.returncode, ran.stdout) == (0, mode + "\n"), (mode, ran.stderr)

    ran = subprocess.run([str(SCRIPTS / "branch-suite.sh")], cwd=tmp_path, capture_output=True, text=True,
                         env={**os.environ, "VERI_BRANCH_SUITE": "remote"})

    assert (ran.returncode, ran.stdout) == (2, "")
    assert "VERI_BRANCH_SUITE" in ran.stderr and "remote" in ran.stderr
