"""Cases for how skills/tdd/SKILL.md's Scope & plan section plans a step that changes pinned text."""
import importlib
import pathlib
import re

from skill_sections import plain_collapsed as _plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

SCOPE = "### 2. Scope & plan → the ledger"


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


def test_scope_and_plan_plans_a_defect_in_a_tests_own_fixture_as_a_fixture_repair_step_1021():
    text = _plain(importlib.import_module("skill_sections").section(SKILL, SCOPE))
    sentence = next((s for s in re.split(r"(?<=\.)\s", text)
                     if "repairs the fixture" in s and "⟦fixture-repair⟧" in s), "")
    assert sentence, "Scope & plan never gives the ⟦fixture-repair⟧ step's line shape"
    assert "<fixture or stub name>" in sentence, "the line shape never names the fixture or stub"
    assert "in <fixture file>, reproduced by a case in <test file>" in sentence, \
        "the line shape never places the fixture file and the reproducing case's test file"
    assert "⟦criterion k⟧" in sentence, "the line shape never carries a ⟦criterion k⟧"
    assert "fixture, stub or harness" in text, "the mark is never limited to a defect in a test's fixture, stub or harness"
    assert "script under test is correct" in text, "the mark is never limited to a correct script under test"
    assert re.search(r"<fixture file> must be a test file\s+by the rule of transform-touches-tests".replace(r"\s+", " "), text), \
        "the rule never says the fixture file must be a test file by transform-touches-tests's rule"


def test_a_fixture_repair_steps_green_pass_is_ticked_without_refactor_pending_under_a_test_subject_1021():
    text = _plain(importlib.import_module("skill_sections").section(
        SKILL, "#### A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)"))
    sentence = next((s for s in re.split(r"(?<=\.)\s", text)
                     if "⟦fixture-repair⟧" in s and "verify-green pass" in s), "")
    assert sentence, "SKILL.md never says how a ⟦fixture-repair⟧ step's verify-green PASS closes it"
    assert "without --refactor-pending" in sentence, "the PASS is never ticked without --refactor-pending"
    assert "--refactor-pending" not in sentence.replace("without --refactor-pending", ""), \
        "the sentence asks for --refactor-pending"
    assert "`test:` subject" in sentence or "test: subject" in sentence, "the PASS is never committed with a test: subject"


def test_scope_and_plan_plans_one_skill_edit_step_per_unit_with_a_requirements_list_and_never_a_red_green_or_refactor_step_for_it_1871():
    text = _plain(importlib.import_module("skill_sections").section(SKILL, SCOPE))
    sentence = next((s for s in re.split(r"(?<=\.)\s", text)
                     if "⟦skill-edit⟧" in s and "requirements list" in s), "")
    assert sentence, "Scope & plan never tells the planner to emit a ⟦skill-edit⟧ step for a unit with a requirements list"
    assert "one ⟦skill-edit⟧ step" in sentence, "the rule never plans one ⟦skill-edit⟧ step"
    assert "naming the unit" in sentence, "the step never names the unit"
    assert "## requirements" in sentence, "the rule never covers a unit an issue's ## Requirements section names"
    never = next((s for s in re.split(r"(?<=\.)\s", text)
                  if "never plan" in s and "red, green or refactor" in s and "⟦skill-edit⟧" not in s), "")
    assert never, "Scope & plan never forbids Red, Green or Refactor steps that edit such a unit"
