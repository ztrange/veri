"""Cases for prose-owed.sh, through the real entry point."""
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("prose-owed.sh run as a script")
def test_a_tree_where_no_unit_has_a_requirements_list_prints_nothing_and_exits_0(tmp_path):
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("Some prose with no list.\n")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, "")
