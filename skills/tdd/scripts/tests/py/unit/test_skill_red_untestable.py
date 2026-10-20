"""Cases for how skills/tdd/SKILL.md's Red section handles a criterion no lightweight, behaviour-level test can pin."""
import pathlib
import re

from skill_sections import heading_window

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

RED = "#### Red — one failing test (developer leaf), then verify-red (blind)"
BAILING = "## Bailing"
BAIL = SKILL.with_name("BAIL.md")


def says(text, pattern, message):
    assert re.search(pattern, text), message


def test_red_section_states_what_a_valid_test_is_behaviour_over_mechanism_with_the_in_process_spy_carve_out():
    text = heading_window(SKILL, RED, r"Develop\.")
    says(text, r"process[^.]{0,20}(count|fork)|fork[^.]{0,20}count",
         "SKILL.md never forbids pinning a process or fork count")
    says(text, r"make profile",
         "SKILL.md never points process/fork counts or timings at make profile instead of an assertion")
    says(text, r"in-process spy",
         "SKILL.md never carves out an in-process spy for a call count the criterion itself names")


def test_red_section_skips_the_blind_verifier_and_bails_immediately_on_against_unmodified_untestable():
    text = heading_window(SKILL, RED, "Branch on the leaf")
    says(text, r"untestable", "SKILL.md's verify sub-step never branches on UNTESTABLE")
    says(text, r"skip[^.]{0,60}verify-(red|pin)|verify-(red|pin)[^.]{0,60}skip",
         "SKILL.md never says to skip verify-red/verify-pin on UNTESTABLE")
    says(text, r"bail", "SKILL.md never says to bail on UNTESTABLE")
    says(text, r"untestable-criterion",
         "SKILL.md never names the untestable-criterion cause token for this bail")


def test_bailing_causes_list_classifies_untestable_criterion_as_a_process_failure():
    text = heading_window(BAIL, BAILING, "killed-stuck")
    says(text, r"untestable-criterion[^.]{0,220}process",
         "SKILL.md's Bailing causes list never classifies untestable-criterion as a process failure")


def test_red_section_routes_a_ci_repair_step_reporting_passes_to_green_with_the_ci_log_as_its_red_evidence_never_to_verify_pin_or_the_test_pin_commit():
    text = heading_window(SKILL, RED, "Branch on the leaf")
    assert "⟦ci-repair⟧" in text, "SKILL.md's Red verify sub-step never names a ⟦ci-repair⟧ step"
    text = text.split("⟦ci-repair⟧", 1)[1][:700]
    says(text, r"passes", "SKILL.md's ⟦ci-repair⟧ rule never says what it does on AGAINST_UNMODIFIED: PASSES")
    says(text, r"green", "SKILL.md's ⟦ci-repair⟧ rule never sends the step on to Green")
    says(text, r"ci[^.]{0,40}log", "SKILL.md's ⟦ci-repair⟧ rule never names the CI log as the step's red evidence")
    says(text, r"(never|not)[^.]{0,120}verify-pin", "SKILL.md's ⟦ci-repair⟧ rule never keeps the step from verify-pin")
    says(text, r"(never|not)[^.]{0,160}test: pin",
         "SKILL.md's ⟦ci-repair⟧ rule never keeps the step from the test: pin tick-and-commit")


def test_window_given_a_dotted_start_pattern_starts_at_the_dotted_line_not_at_the_wildcard_match(tmp_path):
    fixture = tmp_path / "SKILL.md"
    fixture.write_text("## H\nrunXsh wrong\nrun.sh right\n# end\n")
    assert heading_window(fixture, "## H", r"run\.sh") == "run.sh right "
