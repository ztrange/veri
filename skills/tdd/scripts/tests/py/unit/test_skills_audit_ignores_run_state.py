"""The skills-are-skills audit does not take a run-state .tdd/ for a skill."""
import pytest

import test_skills_are_skills as audit


def test_issue_1895_audit_skips_empty_run_state_dirs_but_reports_a_real_skill_without_skill_md(
    tmp_path, monkeypatch
):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "only-run-state" / ".tdd").mkdir(parents=True)
    (tmp_path / "good").mkdir()
    (tmp_path / "good" / "SKILL.md").write_text("x")
    (tmp_path / "no-skill-md").mkdir()
    (tmp_path / "no-skill-md" / "notes.txt").write_text("x")
    monkeypatch.setattr(audit, "SKILLS", tmp_path)

    with pytest.raises(AssertionError) as caught:
        audit.test_every_directory_directly_under_skills_contains_a_skill_md()

    assert str(caught.value).splitlines()[0] == (
        "directories under skills/ with no SKILL.md: no-skill-md"
    )


def test_issue_1895_audit_skips_a_dir_holding_only_a_non_empty_run_state_dir(
    tmp_path, monkeypatch
):
    (tmp_path / "only-run-state" / ".tdd").mkdir(parents=True)
    (tmp_path / "only-run-state" / ".tdd" / "red-prediction.md").write_text("x")
    (tmp_path / "good").mkdir()
    (tmp_path / "good" / "SKILL.md").write_text("x")
    monkeypatch.setattr(audit, "SKILLS", tmp_path)

    audit.test_every_directory_directly_under_skills_contains_a_skill_md()
