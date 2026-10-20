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


@pytest.mark.process("prose-owed.sh run as a script")
def test_a_unit_with_a_requirements_list_and_no_graded_line_is_printed_and_the_exit_is_1(tmp_path):
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout.split()) == (1, ["skills/demo/SKILL.md"]), ran.stderr
