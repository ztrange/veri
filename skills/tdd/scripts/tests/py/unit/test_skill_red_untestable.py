"""Cases for how skills/tdd/SKILL.md's Red section handles a criterion no lightweight, behaviour-level test can pin."""
from skill_sections import heading_window


def test_window_given_a_dotted_start_pattern_starts_at_the_dotted_line_not_at_the_wildcard_match(tmp_path):
    fixture = tmp_path / "SKILL.md"
    fixture.write_text("## H\nrunXsh wrong\nrun.sh right\n# end\n")
    assert heading_window(fixture, "## H", r"run\.sh") == "run.sh right "
