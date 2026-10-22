"""Cases for how skills/tdd/SKILL.md's Red section handles a criterion no lightweight, behaviour-level test can pin."""
import pathlib
import re

from skill_sections import heading_window

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

BAILING = "## Bailing"
BAIL = SKILL.with_name("BAIL.md")


def says(text, pattern, message):
    assert re.search(pattern, text), message


def test_bailing_causes_list_classifies_untestable_criterion_as_a_process_failure():
    text = heading_window(BAIL, BAILING, "killed-stuck")
    says(text, r"untestable-criterion[^.]{0,220}process",
         "SKILL.md's Bailing causes list never classifies untestable-criterion as a process failure")


def test_window_given_a_dotted_start_pattern_starts_at_the_dotted_line_not_at_the_wildcard_match(tmp_path):
    fixture = tmp_path / "SKILL.md"
    fixture.write_text("## H\nrunXsh wrong\nrun.sh right\n# end\n")
    assert heading_window(fixture, "## H", r"run\.sh") == "run.sh right "
