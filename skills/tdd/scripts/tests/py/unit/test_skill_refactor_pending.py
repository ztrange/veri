"""Cases for how skills/tdd/SKILL.md drives the refactor-pending mark, and for CLAUDE.md's and CONTEXT.md's account of it, read as text."""
import importlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[6]
SKILL = ROOT / "skills" / "tdd" / "SKILL.md"
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
    context = file_records(CONTEXT)
    assert context, "CONTEXT.md has no records to read"
    entry = read(context, "CONTEXT.md's Ledger glossary entry", r"^\*\*ledger\*\*:")
    says(entry, MARK, "CONTEXT.md's Ledger entry never spells the mark")
    says(entry, "verify-refactor", "CONTEXT.md's Ledger entry never names verify-refactor")
