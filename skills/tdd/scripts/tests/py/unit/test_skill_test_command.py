"""The section and line-finding helpers, exercised over fixtures."""
import re

import skill_sections


def at(text, pattern):
    return next((n for n, line in enumerate(text.splitlines(), 1) if re.search(pattern, line)), None)


def test_1037_section_given_a_dotted_heading_starts_at_the_dotted_heading_not_at_the_wildcard_match(tmp_path):
    fixture = tmp_path / "SKILL.md"
    fixture.write_text("### runXsh\nwrong\n### run.sh\nright\n### end\n")
    assert skill_sections.section(fixture, "### run.sh") == "### run.sh\nright\n"


def test_1037_at_given_run_dot_sh_returns_the_line_where_run_sh_stands_not_the_one_where_runXsh_does():
    assert at("runXsh\nrun.sh\n", r"run\.sh") == 2
