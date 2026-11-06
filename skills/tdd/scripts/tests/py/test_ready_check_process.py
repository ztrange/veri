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


@pytest.mark.process("ready-check.sh, a /bin/sh shim over veri/ready_check.py, run as a subprocess inside a git repository")
def test_issue_3055_ready_check_with_two_positionals_or_an_unknown_option_exits_2_with_its_usage_line_and_no_stdout(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, capture_output=True)
    for argv in (["one", "two"], ["--no-such-option"]):
        ran = subprocess.run([str(SCRIPTS / "ready-check.sh"), *argv], cwd=repo, capture_output=True, text=True)

        assert ran.returncode == 2, (argv, ran.returncode, ran.stdout, ran.stderr)
        assert "usage: ready-check.sh [repo-root]" in ran.stderr, (argv, ran.stderr)
        assert ran.stdout == "", (argv, ran.stdout)
