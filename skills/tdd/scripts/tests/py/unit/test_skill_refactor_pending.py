"""Cases for how skills/tdd/SKILL.md drives the refactor-pending mark, read as text."""
import importlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[6]
SKILL = ROOT / "skills" / "tdd" / "SKILL.md"

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
