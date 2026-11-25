"""This repository's Python passes ruff under ruff.toml (PRD 039): no unused import, no undefined or redefined name.
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

    ran = subprocess.run([str(RUFF), "check", "--no-cache", "--quiet", "--config", str(REPO / "ruff.toml"), str(REPO)],
                         stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=REPO)

    assert ran.returncode == 0, ran.stdout + ran.stderr
