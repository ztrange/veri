"""Everything directly under skills/ is a skill."""
import re

import pytest

from conftest import SCRIPTS

SKILLS = SCRIPTS.parent.parent


@pytest.mark.tree_audit("every directory directly under skills/")
def test_every_directory_directly_under_skills_contains_a_skill_md():
    without = sorted(
        d.name for d in SKILLS.iterdir() if d.is_dir() and not (d / "SKILL.md").is_file()
    )

    assert without == [], "directories under skills/ with no SKILL.md: " + ", ".join(without)


@pytest.mark.parametrize("skill", ["veri-coord", "veri-dev", "veri-status", "veri-report"])
def test_operator_skill_names_principles_by_a_path_found_in_the_repo(skill):
    root = SKILLS.parent
    line = next(
        ln for ln in (SKILLS / skill / "SKILL.md").read_text().splitlines() if ln.startswith("Obeys ")
    )
    named = re.findall(r"`([^`]*PRINCIPLES\.md)`", line)

    assert named, f"{skill}: no PRINCIPLES.md path on its Obeys line: {line}"
    assert "../veri-ops/" not in named[-1], f"{skill} still names {named[-1]}"
    repo_path = named[-1].rsplit("}", 1)[-1].lstrip("/")
    assert (root / repo_path).is_file(), f"{skill}: {repo_path} is not a file in the repo"
