"""Cases for the shared helper that returns one section of a SKILL.md by its heading."""
import importlib

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
