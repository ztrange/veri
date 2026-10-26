"""Cases for where skills/tdd/SKILL.md verifies the plan and how its plan section orders and words the steps."""
import pathlib

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def skill_lines():
    return SKILL.read_text().splitlines()


def test_skill_md_names_reorder_ledger_steps_sh_as_the_one_sanctioned_reorder_of_unchecked_steps_and_the_hand_edit_guardrail_points_at_it():
    script = "reorder-ledger-steps.sh"
    lines = skill_lines()
    assert script in "\n".join(lines).lower(), f"never names {script}"
    guard = next((line for line in lines if "Never hand-edit the ledger" in line), "")
    assert script in guard and "tick-ledger.sh" in guard, guard
