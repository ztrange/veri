"""Cases for the conductor's own preservation of a troubled step's attempt, as skills/tdd/SKILL.md prescribes it."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

BAILING = "## Bailing"
BAIL = SKILL.with_name("BAIL.md")
PRESERVE_RE = r"\$s/preserve-attempt\.sh"


def bail_lines():
    section = importlib.import_module("skill_sections").section(BAIL, BAILING)
    return section.lower().splitlines()[1:]


def first_line(lines, pattern):
    return next((i for i, line in enumerate(lines) if re.search(pattern, line)), None)


def test_skill_md_preserves_the_attempt_on_a_bail_before_the_bails_reset():
    lines = bail_lines()
    preserve = first_line(lines, PRESERVE_RE)
    reset = first_line(lines, r"git reset --hard head")
    assert preserve is not None, "Bailing section prescribes no `$S/preserve-attempt.sh` call"
    assert reset is not None, "Bailing section no longer prescribes `git reset --hard HEAD`"
    assert preserve < reset, f"bails by preserving at line {preserve}, after the reset at line {reset}"

