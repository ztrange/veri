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


@pytest.mark.process("worktree-setup.sh finds no setup line and does nothing")
def test_2231_no_setup_line_runs_nothing_writes_nothing_and_exits_3(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: all tests: `echo ran >> all-marker`\n")

    result = subprocess.run([SHIM, "2231"], capture_output=True, text=True, cwd=str(tmp_path))

    assert (result.returncode, sorted(p.name for p in tmp_path.iterdir())) == (3, ["CLAUDE.md"])


@pytest.mark.process("worktree-setup.sh finds no CLAUDE.md and does nothing")
def test_2231_no_claude_md_runs_nothing_writes_nothing_and_exits_3(tmp_path):
    result = subprocess.run([SHIM, "2231"], capture_output=True, text=True, cwd=str(tmp_path))

    assert (result.returncode, sorted(p.name for p in tmp_path.iterdir())) == (3, [])


@pytest.mark.process("worktree-setup.sh refuses a call with no arguments")
def test_2231_no_arguments_prints_a_usage_line_on_stderr_and_exits_2(tmp_path):
    result = subprocess.run([SHIM], capture_output=True, text=True, cwd=str(tmp_path))

    assert (result.returncode, result.stderr.strip()) == (2, "usage: worktree-setup.sh <n>")


@pytest.mark.process("worktree-setup.sh called again in a worktree whose setup already succeeded")
def test_2231_second_call_after_a_successful_setup_runs_nothing_and_exits_3(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: setup: `echo ran >> setup-marker`\n")
    subprocess.run([SHIM, "2231"], capture_output=True, text=True, cwd=str(tmp_path))

    result = subprocess.run([SHIM, "2231"], capture_output=True, text=True, cwd=str(tmp_path))

    assert (result.returncode, (tmp_path / "setup-marker").read_text()) == (3, "ran\n")


@pytest.mark.process("worktree-setup.sh called again in a worktree whose setup failed")
def test_2231_second_call_after_a_failed_setup_runs_the_command_again_and_exits_with_its_code(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# notes\n\nveri: setup: `echo ran >> setup-marker; exit 7`\n")
    first = subprocess.run([SHIM, "2231"], capture_output=True, text=True, cwd=str(tmp_path))

    second = subprocess.run([SHIM, "2231"], capture_output=True, text=True, cwd=str(tmp_path))

    assert (
        first.returncode,
        "exit 7" in first.stderr and "echo ran >> setup-marker; exit 7" in first.stderr,
        second.returncode,
        (tmp_path / "setup-marker").read_text(),
    ) == (1, True, 1, "ran\nran\n")
