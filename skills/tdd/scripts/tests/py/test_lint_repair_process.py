"""Cases for veri/lint_repair.py that start a real process: the shim's entry-point contract (#4123)."""
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("lint-repair.sh run through its shim in a repo declaring a lint command")
def test_4123_lint_repair_sh_prints_the_step_with_the_worktree_path_redacted_through_its_shim(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("veri: lint: `ruff check .`\n")

    done = subprocess.run([str(SCRIPTS / "lint-repair.sh"), "step"], input=f"{tmp_path}/a.py:1: E501\n".encode(),
                          cwd=tmp_path, capture_output=True)

    assert (done.returncode, done.stderr) == (0, b"")
    assert str(tmp_path).encode() not in done.stdout
    assert done.stdout.endswith(b"/a.py:1: E501 \xe2\x9f\xa6diff-checked\xe2\x9f\xa7 \xe2\x9f\xa6lint-repair\xe2\x9f\xa7\n")
