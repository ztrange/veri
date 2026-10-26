"""Cases for how skills/tdd/SKILL.md drives the refactor-pending mark, and for CLAUDE.md's and CONTEXT.md's account of it, read as text."""
import importlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[6]
SKILL = ROOT / "skills" / "tdd" / "SKILL.md"
CLAUDE = ROOT / "CLAUDE.md"
CONTEXT = ROOT / "CONTEXT.md"

MARK = "⟂ refactor pending"


def records_of(raw):
    records, rec = [], b""
    for line in raw.splitlines():
        if re.match(rb"[0-9]+\. ", line) or re.match(rb"\s*- ", line):
            records.append(rec)
            rec = line
        elif not line.strip():
            records.append(rec)
            rec = b""
        elif rec == b"":
            rec = line
        else:
            rec += b" " + line
    records.append(rec)
    return [re.sub(rb"\s+", b" ", r).lower() for r in records if r != b""]


def file_records(path):
    return records_of(pathlib.Path(path).read_bytes())


def body_of(text):
    return text.split("\n", 1)[1] if "\n" in text else ""


def section_records(heading):
    return records_of(body_of(importlib.import_module("skill_sections").section(SKILL, heading)).encode())


def first(records, *patterns):
    return next((r for r in records if all(re.search(p.encode(), r) for p in patterns)), None)


def read(records, what, *patterns):
    found = first(records, *patterns)
    assert found is not None, f"SKILL.md has no instruction that {what}"
    return found


def says(text, pattern, message):
    assert re.search(pattern.encode(), text), message


def test_claude_md_s_ledger_invariant_and_context_md_s_ledger_entry_say_a_ticked_step_carries_the_refactor_pending_mark_until_its_verify_refactor_passes():
    claude = file_records(CLAUDE)
    assert claude, "CLAUDE.md has no records to read"
    invariant = read(claude, "CLAUDE.md's ledger invariant", "committed ledger", "source of truth")
    says(invariant, MARK, "CLAUDE.md's ledger invariant never spells the mark")
    says(invariant, "verify-refactor", "CLAUDE.md's ledger invariant never names verify-refactor")
    context = file_records(CONTEXT)
    assert context, "CONTEXT.md has no records to read"
    entry = read(context, "CONTEXT.md's Ledger glossary entry", r"^\*\*ledger\*\*:")
    says(entry, MARK, "CONTEXT.md's Ledger entry never spells the mark")
    says(entry, "verify-refactor", "CONTEXT.md's Ledger entry never names verify-refactor")


SCRIPTS_HEADING = "## The scripts (this skill's `scripts/` directory)"
SKILL_MD = "skills/tdd/SKILL.md"
REMOVAL_VERB = r"strip|remove|drop|clear|delete"


def scripts_records():
    records = file_records(SKILL.with_name("SCRIPTS.md"))
    assert records, "SCRIPTS.md has no entries to read"
    return records


def planted_records(text):
    records = records_of(body_of(importlib.import_module("skill_sections").section_of(text, SCRIPTS_HEADING)).encode())
    assert records, "the planted ## The scripts section could not be read"
    return records


def entry_of(records, script, problems):
    found = first(records, r"^- .\$s/" + re.escape(script))
    if found is None:
        problems.append(f"{SKILL_MD} has no instruction that documents {script} in the script reference list")
    return found


def entry_says(problems, entry, script, pattern, message):
    if not re.search(pattern.encode(), entry):
        problems.append(f"{SKILL_MD}'s entry for {script} {message}")


def says_removal_verb(problems, entry, script):
    entry_says(problems, entry.replace(script.encode(), b""), script, REMOVAL_VERB,
               "never says it takes the mark off the step, so what the script does to the ledger is left to be guessed from its name")


def says_exit_codes(problems, entry, script):
    entry_says(problems, entry, script, r"exits? 0",
               "never names exit 0, so nothing says what a call that did its work answers with, and the conductor is left inferring it from whether stdout came back empty")
    entry_says(problems, entry, script, r"exits? 3",
               "never names exit 3, so the one code that is not an error — nothing matched, nothing pending — has no documented meaning and reads as the plumbing having broken")


def removal_verb_probe(records):
    problems = []
    entry = entry_of(records, "clear-refactor-pending.sh", problems)
    if entry is not None:
        says_removal_verb(problems, entry, "clear-refactor-pending.sh")
    return problems


def reference_list_probes(records):
    problems = []
    script = "tick-ledger.sh"
    entry = entry_of(records, script, problems)
    if entry is not None:
        entry_says(problems, entry, script, r"--refactor-pending",
                   "never mentions --refactor-pending, so the flag the green commit must tick with is invisible to a session that reads the list to find out how to tick")
        entry_says(problems, entry, script, re.escape(MARK),
                   f"never spells the mark the flag appends, so nothing connects that write to the `{MARK}` string next-pending-refactor.sh matches, and either side can be reworded without the other noticing")
        entry_says(problems, entry, script, r"exits? 3",
                   "never names exit 3, so a green commit whose substring matched no unchecked step looks like it ticked, and the step is committed as green with no mark and no tick")
    script = "next-pending-refactor.sh"
    entry = entry_of(records, script, problems)
    if entry is not None:
        entry_says(problems, entry, script, r"prints?[^.]*step",
                   "never says it prints the pending step, so a resumed conductor is not told that stdout is the step to re-enter the refactor loop on")
        says_exit_codes(problems, entry, script)
    script = "clear-refactor-pending.sh"
    entry = entry_of(records, script, problems)
    if entry is not None:
        entry_says(problems, entry, script, re.escape(MARK),
                   "never spells the mark it removes, so the list documents an eraser without saying what it erases and nothing ties it to the flag that wrote the mark")
        says_removal_verb(problems, entry, script)
        says_exit_codes(problems, entry, script)
    return problems


def test_skill_md_s_script_reference_list_documents_tick_ledger_sh_refactor_pending_next_pending_refactor_sh_and_clear_refactor_pending_sh_each_with_what_it_prints_and_its_exit_codes():
    problems = reference_list_probes(scripts_records())
    assert not problems, problems


PLANTED_CLEAR_ONLY_BY_FILENAME = """## The scripts (this skill's `scripts/` directory)

- `$S/clear-refactor-pending.sh .tdd/issue-<n>.md '<substring>'` — the counterpart of
  `tick-ledger.sh --refactor-pending`: the first ticked step matching the substring no longer
  carries the ` ⟂ refactor pending` mark afterwards, once that step's refactor has been
  verified. Nothing on stdout. **Exit 0** when it did its work; **exit 3** when no ticked step
  both matched and carried the mark.
"""

PLANTED_BARE_ENTRIES = """## The scripts (this skill's `scripts/` directory)

- `$S/tick-ledger.sh .tdd/issue-<n>.md '<substring>'` — the ledger is rewritten so the first
  unchecked step matching the substring is ticked.
- `$S/next-pending-refactor.sh .tdd/issue-<n>.md` — reads the ledger and answers about the
  first ticked step whose tidying is still owed.
- `$S/clear-refactor-pending.sh .tdd/issue-<n>.md '<substring>'` — the counterpart of the
  tick above, run once that step's refactor has been verified. Nothing on stdout.
"""


def test_case_4_s_removal_verb_probe_reports_a_problem_naming_the_clear_refactor_pending_sh_entry_when_only_the_filename_that_opens_it_supplies_a_removal_verb():
    problems = removal_verb_probe(planted_records(PLANTED_CLEAR_ONLY_BY_FILENAME))
    assert problems, "the removal-verb probe reported nothing against an entry whose only removal verb is the clear-refactor-pending.sh filename that opens it"
    assert "clear-refactor-pending.sh" in " ".join(problems), "the removal-verb probe reported a problem that never names the clear-refactor-pending.sh entry"


def test_skill_md_s_clear_refactor_pending_sh_entry_names_a_removal_verb_in_its_own_prose_so_case_4_s_removal_verb_probe_reports_nothing_against_the_document_as_committed():
    problems = removal_verb_probe(scripts_records())
    assert not problems, problems


def test_case_4_s_other_nine_probes_each_report_a_problem_under_the_entry_they_were_asked_of_against_reference_list_entries_that_carry_none_of_what_they_ask_for():
    problems = reference_list_probes(planted_records(PLANTED_BARE_ENTRIES))
    wanted = [
        ("tick-ledger.sh", "never mentions --refactor-pending"),
        ("tick-ledger.sh", "never spells the mark the flag appends"),
        ("tick-ledger.sh", "never names exit 3, so a green commit"),
        ("next-pending-refactor.sh", "never says it prints the pending step"),
        ("next-pending-refactor.sh", "never names exit 0"),
        ("next-pending-refactor.sh", "never names exit 3, so the one code"),
        ("clear-refactor-pending.sh", "never spells the mark it removes"),
        ("clear-refactor-pending.sh", "never names exit 0"),
        ("clear-refactor-pending.sh", "never names exit 3, so the one code"),
    ]
    silent = [w for w in wanted if not any(f"entry for {w[0]}" in p and w[1] in p for p in problems)]
    assert not silent, f"no probe reported these, though the planted entries carry none of it: {silent}"
