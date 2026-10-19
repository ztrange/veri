"""Cases for the `repair <case>` route in skills/tdd/SKILL.md's green WRONG_TEST handling."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def test_1765_repair_route_runs_verify_red_before_green_and_carries_no_stray_pin_standing_order():
    text = SKILL.read_text()
    bullet = next(line for line in text.splitlines() if "printing `repair <case>`" in line)
    assert re.search(r"verify-red again.*only then retry green", bullet), \
        "the repair route does not send the repaired Red through verify-red before Green"
    stray = re.search(r"every checksum or verbatim pin the change moves lands in the same commit", text, re.I)
    assert not stray, "SKILL.md carries a stray standing order about pins outside Scope & plan"
