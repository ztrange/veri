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


def test_scope_and_plan_plans_a_pinned_text_criterions_case_as_its_own_step_after_the_diff_checked_one_1730():
    text = _plain(importlib.import_module("skill_sections").section(SKILL, SCOPE))
    sentence = next((s for s in re.split(r"(?<=\.)\s", text)
                     if "also asks for a case pinning that text" in s), "")
    assert sentence, "Scope & plan never says what to plan when a text-changing criterion also asks for a case pinning it"
    assert "⟦diff-checked⟧ step for the text" in sentence, "the rule never plans a ⟦diff-checked⟧ step for the text"
    assert "separate step for the case" in sentence, "the rule never plans the case as a separate step"
    assert "same ⟦criterion k⟧" in sentence, "the rule never tags both steps with the same ⟦criterion k⟧"
    assert "after the text's" in sentence, "the rule never places the case's step after the text's"


def test_scope_and_plan_plans_a_step_updating_the_older_cases_pinning_changed_text_ahead_of_the_step_changing_it_1862():
    text = _plain(importlib.import_module("skill_sections").section(SKILL, SCOPE))
    sentence = next((s for s in re.split(r"(?<=\.)\s", text)
                     if "changes text or output" in s and "older cases" in s), "")
    assert sentence, "Scope & plan never tells the planner what to do when a criterion changes text older cases pin"
    assert "outside the step's own red" in sentence, "the rule never limits itself to cases outside the step's own Red"
    assert "holds a step that updates those older cases" in sentence, "the rule never plans a step updating the older cases"
    assert "ahead of the step that changes the text" in sentence, "the rule never places that step ahead of the one changing the text"
