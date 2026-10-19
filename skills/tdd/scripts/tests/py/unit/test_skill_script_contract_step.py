"""Cases for how skills/tdd/SKILL.md's Scope & plan section sizes a step that adds a script."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

SCOPE = "### 2. Scope & plan → the ledger"


def _plain(text):
    return " ".join(text.replace("*", "").replace("`", "").lower().split())


def test_scope_and_plan_gives_the_step_adding_a_script_its_usage_exit_2_and_caller_in_that_same_step_1700():
    text = _plain(importlib.import_module("skill_sections").section(SKILL, SCOPE))
    sentence = next((s for s in re.split(r"(?<=\.)\s", text)
                     if "skills/tdd/scripts/" in s and "usage" in s), "")
    assert sentence, "Scope & plan never tells the planner what a step adding a script under skills/tdd/scripts/ owes"
    assert re.search(r"exit 2", sentence), "the script rule never names exit 2"
    assert re.search(r"caller", sentence.split("same step", 1)[0]), \
        "the script rule never gives the adding step a declared caller before saying it lands in that same step"
    assert re.search(r"same step", sentence), "the script rule never says it all lands in the same step"
    assert re.search(r"test_missing_argument_cli", sentence) and re.search(r"unreachable", sentence), \
        "the script rule never names the repo-wide audits (test_missing_argument_cli, unreachable)"
