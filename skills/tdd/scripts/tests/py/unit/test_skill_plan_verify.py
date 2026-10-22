"""Cases for where skills/tdd/SKILL.md verifies the plan and how its plan section orders and words the steps."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
SCRIPTS_MD = SKILL.with_name("SCRIPTS.md")

WANT_PHASES = ["red", "green", "refactor", "pin", "plan"]
ALTERNATION_RE = r"<([a-z|]*red[a-z|]*)>"


def skill_lines():
    return SKILL.read_text().splitlines()


def test_skill_md_script_entries_for_the_verifier_scripts_name_the_plan_phase_beside_the_four_cycle_phases():
    for script in ("build-verify-prompt.sh", "verify.sh", "run-verdict.sh"):
        entry_re = r"^- .[$]S/" + script.replace(".", "[.]") + " "
        catalogue = SCRIPTS_MD.read_text().splitlines()
        entry_line = next((n for n, text in enumerate(catalogue, 1) if re.search(entry_re, text)), 0)
        assert entry_line, f"no script-inventory entry for {script} (/{entry_re}/)"
        line = catalogue[entry_line - 1]
        match = re.search(ALTERNATION_RE, line)
        assert match, f"line {entry_line}, the entry for {script}, spells no phase alternation: {line}"
        alternation = f"|{match.group(1)}|"
        for phase in WANT_PHASES:
            assert f"|{phase}|" in alternation, (
                f"line {entry_line}, the entry for {script}, spells <{match.group(1)}>, which does not name '{phase}'")


def test_skill_md_names_reorder_ledger_steps_sh_as_the_one_sanctioned_reorder_of_unchecked_steps_and_the_hand_edit_guardrail_points_at_it():
    script = "reorder-ledger-steps.sh"
    lines = skill_lines() + SCRIPTS_MD.read_text().splitlines()
    assert script in "\n".join(lines).lower(), f"never names {script}"
    mention = " ".join(line for line in lines if script in line).lower()
    for word in ("unchecked", "plan:", "operator"):
        assert word in mention, f"no line naming {script} mentions '{word}'"
    guard = next((line for line in lines if "Never hand-edit the ledger" in line), "")
    assert script in guard and "tick-ledger.sh" in guard, guard
