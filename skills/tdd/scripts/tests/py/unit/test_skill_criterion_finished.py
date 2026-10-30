"""Cases for when skills/tdd/SKILL.md has the conductor tick an issue criterion and how its step 2 plans the off-cycle step kinds."""
import ast
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
PIN_MD = SKILL.with_name("PIN.md")


def records_of(text):
    records, rec = [], ""
    for line in text.splitlines():
        if re.match(r"[0-9]+\. ", line) or re.match(r"\s*- ", line):
            if rec:
                records.append(rec)
            rec = line
        elif not line.strip():
            if rec:
                records.append(rec)
            rec = ""
        elif not rec:
            rec = line
        else:
            rec += " " + line
    if rec:
        records.append(rec)
    return [re.sub(r"\s+", " ", r).lower() for r in records]


def reads_ledger_steps(anchor, box, lines, problems):
    if not lines:
        problems.append(f"no instruction of skills/tdd/SKILL.md runs '{anchor}' — the rule could not be checked")
        return
    for line in lines:
        if "ledger-steps.sh" not in line:
            problems.append(f"'{anchor}' reads without ledger-steps.sh: {line}")
        if box in line:
            problems.append(f"'{anchor}' still spells its own checkbox pattern: {line}")


def skill_lines():
    return SKILL.read_text().splitlines() + PIN_MD.read_text().splitlines()


def test_495_every_instruction_that_ticks_criterion_k_in_the_issue_body_reads_its_text_from_ledger_steps_records_spelling_no_checkbox_pattern():
    problems = []
    anchor = 'tick-issue-criterion.sh <n> "$('
    reads_ledger_steps(anchor, r"\[[ x]\]", [r for r in records_of(SKILL.read_text()) if anchor in r], problems)
    assert not problems, "\n".join(problems)


def test_495_every_instruction_that_names_the_last_ticked_step_reads_it_from_ledger_steps_records_spelling_no_checkbox_pattern():
    problems = []
    for anchor in ("event.sh step-done", "event.sh pin", 'event.sh step-added anchor="$(', 'add-ledger-step.sh .tdd/issue-<n>.md after "$('):
        lines = [l for l in skill_lines() if anchor in l and "next-unchecked.sh" not in l and "next-pending-refactor.sh" not in l]
        reads_ledger_steps(anchor, r"\[x\]", lines, problems)
    assert not problems, "\n".join(problems)


def test_495_every_instruction_that_counts_the_steps_left_for_run_affordable_reads_them_from_ledger_steps_records_spelling_no_checkbox_pattern():
    problems = []
    anchor = 'run-affordable.sh "$('
    reads_ledger_steps(anchor, r"\[ \]", [l for l in skill_lines() if anchor in l], problems)
    assert not problems, "\n".join(problems)



def test_2468_every_non_test_function_defined_in_this_file_is_called_at_least_once_in_it():
    tree = ast.parse(pathlib.Path(__file__).read_text())
    defined = [n.name for n in tree.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("test_")]
    called = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    orphans = [name for name in defined if name not in called]
    assert not orphans, "never called in this file: " + ", ".join(orphans)
