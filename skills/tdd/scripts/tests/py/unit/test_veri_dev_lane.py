"""Prose cases for the lane word of skills/veri-dev/SKILL.md."""
from conftest import ROOT

SKILL = ROOT / "skills" / "veri-dev" / "SKILL.md"


def test_1778_veri_dev_takes_an_optional_lane_word_in_its_invocation_line_and_d1_row():
    text = SKILL.read_text()
    invoked = next(line for line in text.splitlines() if line.startswith("Invoked as"))
    d1 = next(line for line in text.splitlines() if line.startswith("| D1 |"))
    form = "/veri-dev [<lane>] [N] [--resume <file>]"

    assert form in invoked
    assert form in d1
    assert "[<lane>] [N] [--resume <file>]" in text.split("---")[1]
    assert "VERI_LABEL=ready-for-agent:mu" in text


def test_1778_veri_dev_states_its_lane_in_its_first_line_of_output():
    text = " ".join(SKILL.read_text().split())

    assert "State the lane in your first line of output" in text
