"""Cases for when skills/tdd/SKILL.md has the conductor tick an issue criterion and how its step 2 plans the off-cycle step kinds."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
PIN_MD = SKILL.with_name("PIN.md")

PIN = "## Already satisfied — the pin"
DRAFT_PR = "### 4. Draft PR"


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
    doc = {PIN: PIN_MD, "## Resume": SKILL.with_name("RESUME.md")}.get(heading, SKILL)
    text = importlib.import_module("skill_sections").section(doc, heading)
    return records_of(text.split("\n", 1)[1])


def first_record(records, *filters):
    for flag, pattern in filters:
        if flag == "F":
            records = [r for r in records if pattern in r]
        else:
            records = [r for r in records if re.search(pattern, r)]
    return records[0] if records else ""


def gated_tick(label, heading, extra, problems):
    rec = first_record(section_records(heading), ("F", "tick-issue-criterion.sh"))
    if not rec:
        problems.append(f"{label}: no instruction under '{heading}' runs tick-issue-criterion.sh — the gate could not be checked")
        return
    if "criterion-finished.sh" not in rec:
        problems.append(f"{label}: the instruction that ticks the issue criterion never runs criterion-finished.sh")
    if not re.search(r"exit \*?\*?0", rec):
        problems.append(f"{label}: the tick is not tied to criterion-finished.sh's exit 0")
    if not (re.search(r"exit \*?\*?3", rec) and re.search(r"(nothing|no criterion|not tick|without ticking|skip)", rec)):
        problems.append(f"{label}: the instruction never says exit 3 ticks nothing")
    if extra and not re.search(extra, rec):
        problems.append(f"{label}: the instruction no longer posts the comment matching /{extra}/")


def test_step_done_and_pin_paths_tick_an_issue_criterion_only_on_criterion_finished_exit_0_ticking_nothing_on_exit_3():
    problems = []
    gated_tick("pin path", PIN, "", problems)
    assert not problems, "\n".join(problems)


def test_481_draft_pr_step_ticks_every_full_suite_line_and_its_issue_criterion_only_once_the_last_full_suite_run_is_green():
    problems = []
    pr_rec = first_record(section_records(DRAFT_PR), ("F", "⟦full-suite⟧"), ("E", "tick"))
    if not pr_rec:
        problems.append("draft PR: no instruction in step 4 ticks a ⟦full-suite⟧ ledger line — the rule could not be checked")
    else:
        if "tick-issue-criterion.sh" not in pr_rec:
            problems.append("draft PR: the ⟦full-suite⟧ tick never ticks the issue criterion it finishes with tick-issue-criterion.sh")
        if not re.search(r"(no|without|never) [^.]*refactor.pending", pr_rec):
            problems.append("draft PR: the ⟦full-suite⟧ tick never says it carries no refactor-pending mark")
        if not re.search(r"last full-suite run[^.]*green", pr_rec):
            problems.append("draft PR: the ⟦full-suite⟧ tick is not tied to the last full-suite run being green")
        if "rebased tip" not in pr_rec:
            problems.append("draft PR: the ⟦full-suite⟧ tick never says the rebased tip's run is the one that counts after a rebase")
        if not re.search(r"(never|not|no) [^.]*red", pr_rec):
            problems.append("draft PR: the ⟦full-suite⟧ tick never says a red run ticks nothing")
    assert not problems, "\n".join(problems)


CONTEXT = pathlib.Path(__file__).resolve().parents[6] / "CONTEXT.md"


def pin_replaces_case_rec():
    return first_record(section_records(PIN), ("F", "⟦replaces-case⟧"))


def guardrails_rec():
    return first_record(section_records("## Guardrails"), ("F", "passes against unmodified code"))


def test_1397_pin_section_sends_a_replaces_case_step_whose_red_reports_passes_through_verify_pin_then_a_green_leaf_deleting_exactly_the_named_cases_accepted_once_mutation_parity_exits_0_then_one_tick():
    problems = []
    rec = pin_replaces_case_rec()
    if not rec:
        problems.append("pin path: no instruction under '## Already satisfied — the pin' states the path for a ⟦replaces-case⟧ step whose Red reports PASSES — the path could not be checked")
    else:
        if "passes" not in rec:
            problems.append("pin path: the ⟦replaces-case⟧ instruction never names a Red that reports PASSES")
        if not re.search(r"verify-pin|verify\.sh pin", rec):
            problems.append("pin path: the ⟦replaces-case⟧ instruction never runs verify-pin first")
        if not (re.search(r"green leaf", rec) and re.search(r"delet", rec) and "exactly the named" in rec):
            problems.append("pin path: the ⟦replaces-case⟧ instruction never launches a green leaf that deletes exactly the named cases")
        if "verify-green" not in rec:
            problems.append("pin path: the ⟦replaces-case⟧ instruction never judges the deletion by the replaces-case verify-green")
        if not ("mutation-parity.sh" in rec and re.search(r"exits? \*{0,2}0", rec)):
            problems.append("pin path: the ⟦replaces-case⟧ instruction never accepts the deletion only once mutation-parity.sh exits 0")
        if not re.search(r"one tick|tick[^.]*once|single tick", rec):
            problems.append("pin path: the ⟦replaces-case⟧ instruction never ends the step in one tick")
    assert not problems, "\n".join(problems)


def test_1397_pin_pass_bullet_names_the_replaces_case_exception_before_its_tick_and_commit_and_the_pin_path_and_step_2_say_whether_refactor_and_refactor_pending_follow_the_deletion_green():
    problems = []
    pin_recs = section_records(PIN)
    pass_rec = first_record(pin_recs, ("F", "pass (exit 0)"))
    if not pass_rec:
        problems.append("pin PASS: no PASS (exit 0) bullet under '## Already satisfied — the pin' — the exception could not be checked")
    elif "⟦replaces-case⟧" not in pass_rec.split("tick-ledger.sh")[0]:
        problems.append("pin PASS: the bullet never names the ⟦replaces-case⟧ exception before its tick-ledger.sh commit")
    refactor_rec = first_record(pin_recs, ("F", "⟦replaces-case⟧"), ("F", "refactor pending"))
    if not (refactor_rec and re.search(r"delet", refactor_rec) and re.search(r"refactor[^ ]* (phase|leaf|follows|runs|does|is)", refactor_rec)):
        problems.append("pin path: no ⟦replaces-case⟧ instruction says whether Refactor and ⟂ refactor pending follow the deletion green")
    assert not problems, "\n".join(problems)


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
    pin_rc_rec = pin_replaces_case_rec()
    pin_before_green = pin_rc_rec.split("green leaf")[0].replace("commit nothing", "")
    if not ("green leaf" in pin_rc_rec and not re.search(r"commit|tick", pin_before_green)):
        problems.append(f"pin path: a commit or tick comes before the deletion green: {pin_before_green}")
    if not ("accepted only once" in pin_rc_rec and not re.search(r"whether or not|regardless|even if", pin_rc_rec)):
        problems.append("pin path: the deletion is not accepted only once mutation-parity.sh exits 0")
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


def test_481_draft_pr_step_lists_every_human_owed_ledger_line_in_the_pr_body_under_owed_by_a_human_each_naming_its_criterion_number_and_adds_no_such_section_when_the_ledger_holds_none():
    problems = []
    rec = first_record(section_records(DRAFT_PR), ("F", "⟦human-owed⟧"), ("F", "## owed by a human"))
    if not rec:
        problems.append("draft PR: no instruction in step 4 lists ⟦human-owed⟧ ledger lines under '## Owed by a human' — the rule could not be checked")
    else:
        if "pr body" not in rec:
            problems.append("draft PR: the ⟦human-owed⟧ instruction never says the lines go into the PR body")
        if not re.search(r"criterion (number|k)", rec):
            problems.append("draft PR: the ⟦human-owed⟧ instruction never says each listed line names its criterion number")
        if not re.search(r"(no|none|omit|without) [^.]*(section|heading)", rec):
            problems.append("draft PR: the ⟦human-owed⟧ instruction never says no such section is added when the ledger holds none")
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
    does_not_hold("draft PR entry", first_record(section_records(DRAFT_PR), ("F", "reached when")), problems)
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


def reconcile_lines():
    return (SKILL.parent / "RECONCILE.md").read_text().splitlines()


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


def test_495_reconcile_check_compares_ledger_steps_state_and_pending_fields_grepping_the_markdown_for_neither_a_tick_nor_the_pending_mark():
    problems = []
    anchor = "diff <("
    lines = [l for l in reconcile_lines() if anchor in l and ".tdd/reconcile-ledger.before" in l]
    reads_ledger_steps(anchor, "[x]", lines, problems)
    for line in lines:
        if "⟂ refactor pending" in line:
            problems.append(f"'{anchor}' still greps for the pending mark itself: {line}")
    assert not problems, "\n".join(problems)
