"""Process cases for worktree-setup.sh, the shim over veri/worktree_setup.py."""
import os
import subprocess

import pytest

SHIM = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "worktree-setup.sh"))


@pytest.mark.process("worktree-setup.sh runs the CLAUDE.md setup line in the worktree root")
def test_2231_setup_line_in_claude_md_runs_once_in_the_worktree_root_and_exits_0(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: setup: `echo ran >> setup-marker`\n")
    (tmp_path / "sub").mkdir()

    result = subprocess.run([SHIM, "2231"], capture_output=True, text=True, cwd=str(tmp_path))

    assert (result.returncode, (tmp_path / "setup-marker").read_text()) == (0, "ran\n")


@pytest.mark.process("worktree-setup.sh refuses a call with no arguments")
def test_2231_no_arguments_prints_a_usage_line_on_stderr_and_exits_2(tmp_path):
    result = subprocess.run([SHIM], capture_output=True, text=True, cwd=str(tmp_path))

    assert (result.returncode, result.stderr.strip()) == (2, "usage: worktree-setup.sh <n>")
