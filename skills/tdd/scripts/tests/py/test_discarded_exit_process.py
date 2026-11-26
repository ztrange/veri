"""Cases for discarded-exit.sh that start the real entry point."""
import os
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("git")
def test_outside_a_git_work_tree_it_prints_the_usage_line_on_stderr_and_exits_2(tmp_path):
    work = tmp_path / "work"
    work.mkdir()

    ran = subprocess.run([str(SCRIPTS / "discarded-exit.sh")], cwd=work, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL, env={**os.environ, "GIT_CEILING_DIRECTORIES": str(tmp_path)})

    assert (ran.returncode, ran.stdout) == (2, ""), ran.stderr
    assert ran.stderr.splitlines()[-1] == "usage: discarded-exit.sh"
