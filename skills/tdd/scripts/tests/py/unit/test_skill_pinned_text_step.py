"""Cases for how skills/tdd/SKILL.md's Scope & plan section plans a step that changes pinned text."""
import importlib
import pathlib
import re

from skill_sections import plain_collapsed as _plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

SCOPE = "### 2. Scope & plan → the ledger"


def test_scope_and_plan_names_the_repo_wide_audits_a_step_adding_a_script_goes_green_against_1700():
    text = _plain(importlib.import_module("skill_sections").section(SKILL, SCOPE))
    sentence = next((s for s in re.split(r"(?<=\.)\s", text)
                     if "skills/tdd/scripts/" in s and "usage" in s), "")
    assert sentence, "Scope & plan never tells the planner what a step adding a script under skills/tdd/scripts/ owes"
    assert re.search(r"test_missing_argument_cli", sentence) and re.search(r"unreachable", sentence), \
        "the script rule never names the repo-wide audits (test_missing_argument_cli, unreachable)"


def test_scope_and_plan_says_a_fixture_repair_steps_fixture_file_must_be_a_test_file_by_transform_touches_tests_1021():
    text = _plain(importlib.import_module("skill_sections").section(SKILL, SCOPE))
    assert re.search(r"<fixture file> must be a test file\s+by the rule of transform-touches-tests".replace(r"\s+", " "), text), \
        "the rule never says the fixture file must be a test file by transform-touches-tests's rule"
