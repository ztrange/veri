"""Cases for ready-check.sh that start the real entry point."""
import os
import re
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess outside a git repository")
def test_issue_3055_ready_check_outside_a_git_repository_exits_2_with_a_usage_line_and_make_declares_its_caller(tmp_path):
    elsewhere = tmp_path / "not-a-repo"
    elsewhere.mkdir()
    env = {**os.environ, "GIT_CEILING_DIRECTORIES": str(tmp_path)}
    ran = subprocess.run([str(SCRIPTS / "ready-check.sh")], cwd=elsewhere, capture_output=True, text=True, env=env)
    makefile = (SCRIPTS.parent.parent.parent / "Makefile").read_text()

    assert ran.returncode == 2, (ran.returncode, ran.stdout, ran.stderr)
    assert "ready-check" in ran.stderr and "usage" in ran.stderr.lower()
    assert re.search(r"^ready-check:", makefile, re.M)
