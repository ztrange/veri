"""Cases for how skills/tdd/SKILL.md's Scope & plan section plans a step that changes pinned text."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

SCOPE = "### 2. Scope & plan → the ledger"


def _plain(text):
    return " ".join(text.replace("*", "").replace("`", "").lower().split())


def test_scope_and_plan_plans_a_step_changing_pinned_prompt_or_skill_text_as_diff_checked_with_its_pins_in_one_commit_1713():
    text = _plain(importlib.import_module("skill_sections").section(SKILL, SCOPE))
    sentence = next((s for s in re.split(r"(?<=\.)\s", text)
                     if "rendered prompt text" in s and "checksum" in s), "")
    assert sentence, "Scope & plan never tells the planner how to plan a step that changes pinned prompt or SKILL.md text"
    assert "skill.md sentence" in sentence, "the rule never names a SKILL.md sentence a suite pins"
    assert "verbatim" in sentence, "the rule never names a verbatim pin"
    assert "⟦diff-checked⟧" in sentence, "the rule never plans the step as ⟦diff-checked⟧"
    assert "never as red/green" in sentence, "the rule never rules out a Red/Green step"
    assert re.search(r"one commit", text.split("rendered prompt text", 1)[1]), \
        "the rule never says the text and every pin it moves land in one commit"
