"""Process cases for stack-branch.sh, the shim over veri/stack_branch.py."""
import os
import subprocess

import pytest

SHIM = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "stack-branch.sh"))


@pytest.mark.process("stack-branch.sh run in place against a git repository with a local origin whose CLAUDE.md names a stack branch, and one naming none")
def test_shim_prints_the_named_stack_branch_with_exit_0_and_nothing_with_exit_3(tmp_path):
    named = tmp_path / "named"
    named.mkdir()
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(named), check=True)
    (named / "CLAUDE.md").write_text("veri: stack branch: stack\n")
    for argv in (["add", "CLAUDE.md"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "seed"],
                 ["remote", "add", "origin", str(tmp_path / "origin.git")], ["push", "-q", "origin", "main"]):
        subprocess.run(["git", *argv], cwd=str(named), check=True)
    silent = tmp_path / "silent"
    silent.mkdir()

    found = subprocess.run([SHIM], capture_output=True, text=True, cwd=str(named))
    none = subprocess.run([SHIM, str(silent)], capture_output=True, text=True, cwd=str(named))

    assert [(r.returncode, r.stdout, r.stderr) for r in (found, none)] == [(0, "stack\n", ""), (3, "", "")]
