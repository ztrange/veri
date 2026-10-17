"""Cases for the shared helper that returns one section of a SKILL.md by its heading."""
import importlib

import pytest

SKILL = (
    "# Title\n"
    "intro\n"
    "## Alpha\n"
    "alpha body\n"
    "### Alpha one\n"
    "one body\n"
    "#### Alpha one deep\n"
    "deep body\n"
    "### Alpha two\n"
    "two body\n"
    "## Beta\n"
    "beta body\n"
)


def test_section_returns_only_the_named_section_up_to_the_next_heading_of_the_same_or_higher_level(tmp_path):
    skill_sections = importlib.import_module("skill_sections")
    skill = tmp_path / "SKILL.md"
    skill.write_text(SKILL)

    sub = skill_sections.section(skill, "### Alpha one")
    top = skill_sections.section(skill, "## Alpha")

    assert "one body" in sub and "deep body" in sub
    assert "alpha body" not in sub and "two body" not in sub and "beta body" not in sub
    assert "alpha body" in top and "one body" in top and "two body" in top
    assert "beta body" not in top and "intro" not in top


def test_section_fails_the_calling_test_naming_the_heading_when_it_is_absent_and_never_returns_the_whole_file(tmp_path):
    skill_sections = importlib.import_module("skill_sections")
    skill = tmp_path / "SKILL.md"
    skill.write_text(SKILL)

    with pytest.raises(pytest.fail.Exception) as failure:
        skill_sections.section(skill, "## Missing heading")

    assert "## Missing heading" in str(failure.value)


def test_section_fails_the_calling_test_naming_the_heading_when_it_matches_only_a_non_heading_line(tmp_path):
    skill_sections = importlib.import_module("skill_sections")
    skill = tmp_path / "SKILL.md"
    skill.write_text(SKILL)

    with pytest.raises(pytest.fail.Exception) as failure:
        skill_sections.section(skill, "intro")

    assert "intro" in str(failure.value)


def test_section_of_returns_a_section_whole_when_a_backtick_or_tilde_fence_holds_a_heading_shaped_line_1569():
    skill_sections = importlib.import_module("skill_sections")

    for fence in ("```", "~~~"):
        text = f"## Beta\nbefore\n{fence}\n## x\nin fence\n{fence}\nafter\n## Gamma\ngamma body\n"

        beta = skill_sections.section_of(text, "## Beta")

        assert beta == f"## Beta\nbefore\n{fence}\n## x\nin fence\n{fence}\nafter\n", fence
