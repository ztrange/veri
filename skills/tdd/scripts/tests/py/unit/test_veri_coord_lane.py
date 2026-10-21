"""Prose cases for the lane word of skills/veri-coord/SKILL.md."""
from conftest import ROOT

SKILL = ROOT / "skills" / "veri-coord" / "SKILL.md"
REQUIREMENTS = ROOT / "skills" / "veri-coord" / "REQUIREMENTS.md"


def test_1778_veri_coord_takes_an_optional_lane_word_in_its_invocation_line_and_c1_row():
    text = SKILL.read_text()
    invoked = next(line for line in text.splitlines() if line.startswith("1. Invoked as"))
    c1 = next(line for line in REQUIREMENTS.read_text().splitlines() if line.startswith("| C1 |"))
    form = "/veri-coord [<lane>] [--resume <file>]"

    assert form in text.split("---")[1]
    assert "/veri-coord [<lane>]" in invoked
    assert form in c1
    assert "VERI_LABEL=ready-for-agent:mu" in text


def test_1778_veri_coord_states_its_lane_in_its_first_line_and_names_it_in_every_dev_message():
    text = " ".join(SKILL.read_text().split())

    assert "State the lane in your first line of output" in text
    assert "name it in every message to the dev session" in text
