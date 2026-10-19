"""Cases for scope-check.sh that start a real process."""
import subprocess

import pytest

from conftest import SCRIPTS

PY = "skills/tdd/scripts/tests/py"


@pytest.mark.process("scope-check.sh run on a ledger naming a new tests/py module whose basename exists under tests/py/unit")
def test_1782_a_step_naming_a_new_test_module_whose_basename_exists_exits_1_naming_both_paths(tmp_path):
    existing = tmp_path / PY / "unit" / "test_push_branch.py"
    existing.parent.mkdir(parents=True)
    existing.write_text("")
    ledger = tmp_path / "ledger.md"
    ledger.write_text(f"# Plan\n\n- [ ] Pin the CLI in `{PY}/test_push_branch.py` ⟦criterion 1⟧\n")

    ran = subprocess.run(["sh", str(SCRIPTS / "scope-check.sh"), str(ledger), str(tmp_path)],
                         capture_output=True, text=True,
                         env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 1
    assert f"{PY}/test_push_branch.py" in ran.stderr
    assert f"{PY}/unit/test_push_branch.py" in ran.stderr
