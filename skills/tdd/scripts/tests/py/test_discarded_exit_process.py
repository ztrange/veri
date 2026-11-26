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


@pytest.mark.process("git")
def test_in_a_git_work_tree_an_uncommitted_bare_call_added_to_a_tracked_py_file_is_printed_and_exits_1(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-C", str(work)]
    module = work / "mod.py"
    module.write_text("import subprocess\n")
    subprocess.run([*git, "init", "-q"], check=True, stdin=subprocess.DEVNULL)
    subprocess.run([*git, "add", "mod.py"], check=True, stdin=subprocess.DEVNULL)
    subprocess.run([*git, "commit", "-q", "-m", "base"], check=True, stdin=subprocess.DEVNULL)
    module.write_text("import subprocess\nsubprocess.call([\"true\"])\n")

    ran = subprocess.run([str(SCRIPTS / "discarded-exit.sh")], cwd=work, capture_output=True, text=True,
                         stdin=subprocess.DEVNULL, env={**os.environ, "GIT_CEILING_DIRECTORIES": str(tmp_path)})

    assert (ran.returncode, ran.stdout) == (1, "mod.py:2\n"), ran.stderr
