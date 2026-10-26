"""Case for the print-mode aside in skills/tdd/SKILL.md resolving for a reader of that file alone."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def test_2433_skill_never_promises_modes_below_and_print_mode_aside_cites_readme():
    text = SKILL.read_text()
    flat = re.sub(r"\s+", " ", text)
    aside = re.search(r"print-mode session.{0,400}", flat)
    assert "modes below" not in flat, "SKILL.md still refers to unattended modes 'below'"
    assert aside, "SKILL.md has no print-mode aside"
    assert "README.md" in aside.group(0), f"print-mode aside does not cite README.md: {aside.group(0)!r}"
