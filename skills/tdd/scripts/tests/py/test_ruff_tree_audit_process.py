"""This repository's Python passes ruff under ruff.toml (PRD 039): no unused import, no undefined or redefined name,
no pycodestyle error (E4, E7, E9) or warning (W), no line over the 120-column line-length cap (E501), imports in
order, no function over the complexity cap (C901), no bugbear finding (B).
It audits the tree, not a module's logic, and runs ruff from the venv `make install-dev` built from the lock."""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[5]
RUFF = Path(sys.executable).parent / "ruff"


@pytest.mark.process("ruff check run over the repository")
@pytest.mark.tree_audit("every Python file of the repository")
def test_the_repository_passes_ruff_under_its_config():
    assert RUFF.is_file(), f"{RUFF} missing: run `make install-dev` (requirements-dev.txt locks ruff)"

    check = [str(RUFF), "check", "--no-cache", "--quiet", "--config", str(REPO / "ruff.toml")]

    ran = subprocess.run([*check, str(REPO)], stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=REPO)
    planted = subprocess.run([*check, "--stdin-filename", str(REPO / "planted.py"), "-"],
                             input="planted = 1 \n", capture_output=True, text=True, cwd=REPO)

    assert ran.returncode == 0, ran.stdout + ran.stderr
    assert "W291" in planted.stdout, planted.stdout + planted.stderr
