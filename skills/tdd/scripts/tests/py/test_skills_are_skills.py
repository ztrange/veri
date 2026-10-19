"""Everything directly under skills/ is a skill."""
import pytest

from conftest import SCRIPTS

SKILLS = SCRIPTS.parent.parent


@pytest.mark.tree_audit("every directory directly under skills/")
def test_every_directory_directly_under_skills_contains_a_skill_md():
    without = sorted(
        d.name for d in SKILLS.iterdir() if d.is_dir() and not (d / "SKILL.md").is_file()
    )

    assert without == [], "directories under skills/ with no SKILL.md: " + ", ".join(without)
