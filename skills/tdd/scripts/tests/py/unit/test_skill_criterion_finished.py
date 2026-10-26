"""Cases for when skills/tdd/SKILL.md has the conductor tick an issue criterion and how its step 2 plans the off-cycle step kinds."""
import importlib
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


def section_records(heading):
    doc = {"## Resume": SKILL.with_name("RESUME.md")}.get(heading, SKILL)
    text = importlib.import_module("skill_sections").section(doc, heading)
    return records_of(text.split("\n", 1)[1])


def first_record(records, *filters):
    for flag, pattern in filters:
        if flag == "F":
            records = [r for r in records if pattern in r]
        else:
            records = [r for r in records if re.search(pattern, r)]
    return records[0] if records else ""


CONTEXT = pathlib.Path(__file__).resolve().parents[6] / "CONTEXT.md"


def guardrails_rec():
    return first_record(section_records("## Guardrails"), ("F", "passes against unmodified code"))


def test_1397_guardrails_line_on_a_test_that_passes_against_unmodified_code_carves_out_the_replaces_case_deletion_green():
    problems = []
    rec = guardrails_rec()
    if not rec:
        problems.append("guardrails: no line under '## Guardrails' names a test that passes against unmodified code — the carve-out could not be checked")
    else:
        if "⟦replaces-case⟧" not in rec:
            problems.append("guardrails: the line never carves out a ⟦replaces-case⟧ step")
        if not (re.search(r"green", rec) and re.search(r"delet", rec)):
            problems.append("guardrails: the line never names the green that deletes the named cases")
    assert not problems, "\n".join(problems)


def test_1397_replaces_case_pin_then_delete_path_keeps_its_meaning_exception_not_negated_nothing_committed_or_ticked_before_the_deletion_green_accepted_only_once_mutation_parity_exits_0():
    problems = []
    guard_rec = guardrails_rec()
    guard_after = guard_rec.split("⟦replaces-case⟧", 1)[1] if "⟦replaces-case⟧" in guard_rec else ""
    if not re.search(r"(save|except|unless|but) (on )?(a )?`?⟦replaces-case⟧", guard_rec):
        problems.append("guardrails: the ⟦replaces-case⟧ clause is not introduced as an exception (save/except/unless/but)")
    if re.search(r"(^|[^a-z])(never|not|no)([^a-z]|$)", guard_after):
        problems.append(f"guardrails: the ⟦replaces-case⟧ clause negates the deletion green: {guard_after}")
    assert not problems, "\n".join(problems)


def test_671_context_md_defines_contract_case_implementation_case_and_the_replaces_case_mark():
    problems = []
    entries, rec = [], ""
    for line in CONTEXT.read_text().splitlines():
        if re.match(r"\*\*[^*]+\*\*:", line):
            if rec:
                entries.append(rec)
            rec = line
        elif line.startswith("#") or not line.strip():
            if rec:
                entries.append(rec)
            rec = ""
        elif rec:
            rec += " " + line
    if rec:
        entries.append(rec)
    for term in ("Contract case", "Implementation case"):
        if not any(f"**{term}**:" in e for e in entries):
            problems.append(f"CONTEXT.md: no **{term}**: entry")
    if not any("⟦replaces-case⟧" in e for e in entries):
        problems.append("CONTEXT.md: no glossary entry defines the ⟦replaces-case⟧ mark")
    assert not problems, "\n".join(problems)


def does_not_hold(label, rec, problems):
    if not rec:
        problems.append(f"{label}: the condition could not be found — the rule could not be checked")
        return
    for marker in ("⟦full-suite⟧", "⟦human-owed⟧"):
        if marker not in rec:
            problems.append(f"{label}: the condition never names {marker} lines")
    if not re.search(r"unchecked[^.]*(not|never) hold[^.]*back", rec):
        problems.append(f"{label}: the condition never says an unchecked off-cycle line does not hold the run back")


def test_481_draft_pr_entry_condition_and_resumes_go_to_draft_pr_condition_say_unchecked_full_suite_and_human_owed_lines_do_not_hold_a_run_back():
    problems = []
    does_not_hold("resume", first_record(section_records("## Resume"), ("E", r"go to the \*?\*?draft pr")), problems)
    assert not problems, "\n".join(problems)


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

