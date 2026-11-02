"""What skills/tdd/SKILL.md and CLAUDE.md say about which leaves run the full suite, read as text."""
import pathlib
import re

import skill_sections
from skill_sections import plain_lower as plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

REFACTOR_LOOP = "#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"


def doc_text(skill, heading, start=None):
    lines = skill_sections.section(skill, heading).splitlines()[1:]
    if start is not None:
        at = next((i for i, line in enumerate(lines) if re.search(start, line)), len(lines))
        lines = lines[at:]
    return "".join(plain(line) + " " for line in lines)


def test_1300_skill_md_runs_suite_reported_sh_only_after_a_leaf_whose_prompt_asks_for_a_suite_line_never_after_the_refactor_leaf_or_a_revise_of_red_green_or_refactor():
    assert "suite-reported.sh" not in doc_text(SKILL, REFACTOR_LOOP), (
        "Refactor loop: runs suite-reported.sh after a leaf whose prompt asks for no SUITE: line")


def whole_skill():
    return plain(SKILL.with_name("REFACTOR-KIND.md").read_text()).replace("\n", " ")


def test_1568_skill_md_runs_suite_reported_sh_develop_transform_after_the_refactor_kind_transform_leaf_and_before_its_blind_transform_verifier():
    assert "suite-reported.sh develop-transform" in whole_skill(), "REFACTOR-KIND.md never runs suite-reported.sh develop-transform"


def test_991_doc_text_given_the_from_regex_5_starts_at_the_line_5_y_not_at_5x_y(tmp_path):
    fixture = tmp_path / "doc.md"
    fixture.write_text("## Section\n5x y\n5. y\n")
    assert doc_text(fixture, "## Section", r"^5\. ") == "5. y "


