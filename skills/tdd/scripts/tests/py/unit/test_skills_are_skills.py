"""Everything directly under skills/ is a skill."""
import re
import sys

import pytest

from conftest import SCRIPTS

SKILLS = SCRIPTS.parent.parent


@pytest.mark.tree_audit("every directory directly under skills/")
def test_every_directory_directly_under_skills_contains_a_skill_md():
    def run_state_only(d):
        return all(c.name == ".tdd" and c.is_dir() for c in d.iterdir())

    without = sorted(
        d.name
        for d in SKILLS.iterdir()
        if d.is_dir()
        and d.name != ".tdd"
        and not (d / "SKILL.md").is_file()
        and not (any(d.iterdir()) and run_state_only(d))
    )

    assert without == [], "directories under skills/ with no SKILL.md: " + ", ".join(without)


@pytest.mark.parametrize("skill", ["vcoord", "vdev", "vstatus", "vreport"])
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


def test_issue_1895_audit_still_reports_an_empty_directory_under_skills(tmp_path, monkeypatch):
    (tmp_path / "empty").mkdir()
    monkeypatch.setattr(sys.modules[__name__], "SKILLS", tmp_path)

    with pytest.raises(AssertionError) as caught:
        test_every_directory_directly_under_skills_contains_a_skill_md()

    assert str(caught.value).splitlines()[0] == "directories under skills/ with no SKILL.md: empty"


def test_issue_1895_audit_skips_a_non_empty_run_state_directory_under_skills(tmp_path, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "red-prediction.md").write_text("prediction\n")
    monkeypatch.setattr(sys.modules[__name__], "SKILLS", tmp_path)

    test_every_directory_directly_under_skills_contains_a_skill_md()
