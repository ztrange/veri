"""Everything directly under skills/ is a skill."""
import re

import pytest

from conftest import SCRIPTS

SKILLS = SCRIPTS.parent.parent


def _is_run_state_only(path):
    children = list(path.iterdir())
    if not children:
        return path.name == ".tdd"
    return [c.name for c in children] == [".tdd"] and not any((path / ".tdd").iterdir())


def _without_skill_md(skills):
    return sorted(
        d.name
        for d in skills.iterdir()
        if d.is_dir() and not (d / "SKILL.md").is_file() and not _is_run_state_only(d)
    )


@pytest.mark.tree_audit("every directory directly under skills/")
def test_every_directory_directly_under_skills_contains_a_skill_md():
    without = _without_skill_md(SKILLS)

    assert without == [], "directories under skills/ with no SKILL.md: " + ", ".join(without)


def test_an_empty_run_state_directory_under_skills_is_not_a_skill_missing_its_skill_md(tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "stray").mkdir()
    (tmp_path / "stray" / ".tdd").mkdir()
    (tmp_path / "real").mkdir()
    (tmp_path / "real" / "SKILL.md").write_text("x")

    assert _without_skill_md(tmp_path) == []


def test_a_skill_directory_without_skill_md_is_still_reported(tmp_path):
    (tmp_path / "broken").mkdir()
    (tmp_path / "broken" / "notes.md").write_text("x")
    (tmp_path / "bare").mkdir()
    (tmp_path / "bare" / ".tdd").mkdir()
    (tmp_path / "bare" / ".tdd" / "log").write_text("x")

    assert _without_skill_md(tmp_path) == ["bare", "broken"]


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
