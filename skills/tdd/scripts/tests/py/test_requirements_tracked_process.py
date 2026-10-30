"""Cases for requirements.tracked, through prose-owed.sh in a real git repository."""
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("prose-owed.sh run as a script in a real git repository")
def test_2702_an_untracked_requirements_md_in_a_subdirectory_is_owed_nothing(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, stdin=subprocess.DEVNULL)
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "scratch").mkdir()
    (tmp_path / "scratch" / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, ""), ran.stderr


@pytest.mark.process("prose-owed.sh run as a script in a real git repository")
def test_2702_an_untracked_graded_in_a_subdirectory_orphans_nothing(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, stdin=subprocess.DEVNULL)
    (tmp_path / "scratch").mkdir()
    (tmp_path / "scratch" / "GRADED").write_text("skills/gone/SKILL.md %s 2026-01-01 g1\n" % ("0" * 64))

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, ""), ran.stderr
