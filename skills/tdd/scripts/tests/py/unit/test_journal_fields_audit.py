"""A writer passes only the fields JOURNAL.md documents for the kind it writes."""
import pytest

from veri import journal_schema

# Ratchet: (kind, field) -> where a writer passes a field JOURNAL.md's row for that kind does not list.
# Each is a documentation gap to close in JOURNAL.md (or a field to stop passing). Entries may be removed,
# never added; a stale entry (the writer no longer passes it) fails the audit so the table shrinks.
UNDOCUMENTED = {}

# Ratchet: kind -> where a writer passes a literal kind JOURNAL.md has no row for (so its fields are
# unaudited above). Entries may be removed, never added.
UNDOCUMENTED_KINDS = {
    "grading": "grade_prose.py:322",  # unit, verdict, failing, cost_usd, id
    "unpinnable-missing": "pin_reject_route.py:56",  # step
    "prose-owed-waived": "prose_owed.py:69",  # unit, step
    "suite-flake": "rerun_alone.py:24",  # files; at (suite_red_resume.py:121)
    "skill-edit-no-author": "skill_edit_step.py:385",  # unit
}

# Fields every journal line carries from the run context, documented in JOURNAL.md's prose above the table.
CONTEXT_KEYS = {"ts", "awake", "issue", "actor", "phase", "step", "event", "attempt", "skill_commit"}


def _writes(index):
    """{(kind, field): 'file:line'} for every literal field a writer passes to a literal kind."""
    found = {}
    for module in index.names:
        for line, kind, names in journal_schema.writer_calls(index.text(module), module):
            for name in names if kind else ():
                found.setdefault((kind, name), f"{module}.py:{line}")
    return found


@pytest.mark.tree_audit("skills/tdd/scripts/veri and skills/tdd/JOURNAL.md")
def test_every_literal_field_a_writer_passes_is_documented_for_its_literal_kind(veri_modules_index):
    """Walks `event.mark`/`event.append`, `verify.mark`, `supervise.mark` and `push_branch.record` calls
    (and the bare `mark`/`record` inside the modules that define them) with `ast`, and fails when a call
    whose kind is a string literal passes a field written as a literal `"name=…"` that the kind's row in
    JOURNAL.md does not list. Kinds without a row are skipped (test_journal_event_roster audits names).

    It cannot see: a computed kind (`event.mark(d, c, event_name, …)`), `**fields`, a field list built in a
    variable (`harvest_usage`'s `pairs`) or a field whose name is not a literal; calls reached through a
    wrapper other than the five shapes; and events that prose writes through `event.sh`."""
    from conftest import SCRIPTS

    journal = (SCRIPTS.parent / "JOURNAL.md").read_text(encoding="utf-8")
    documented = journal_schema.kinds(journal)
    gaps = {key: where for key, where in _writes(veri_modules_index).items()
            if key[0] in documented and key[1] not in journal_schema.fields(journal, key[0])
            and key[1] not in CONTEXT_KEYS}

    new = {key: where for key, where in gaps.items() if key not in UNDOCUMENTED}
    stale = sorted(key for key in UNDOCUMENTED if key not in gaps)

    assert not new, f"writers pass fields JOURNAL.md does not document: {new}"
    assert not stale, f"UNDOCUMENTED lists gaps that no longer exist, remove them: {stale}"


@pytest.mark.tree_audit("skills/tdd/scripts/veri")
def test_the_walk_sees_the_writers_of_the_tree(veri_modules_index):
    kinds = {kind for kind, _ in _writes(veri_modules_index)}

    assert {"bail", "verdict", "launch", "merged", "test-run"} <= kinds


@pytest.mark.tree_audit("skills/tdd/scripts/veri and skills/tdd/JOURNAL.md")
def test_every_literal_kind_a_writer_passes_has_a_row_in_journal_md(veri_modules_index):
    """Same walk as above; a kind that is not a string literal or a module-level constant is invisible."""
    from conftest import SCRIPTS

    documented = journal_schema.kinds((SCRIPTS.parent / "JOURNAL.md").read_text(encoding="utf-8"))
    gaps = {}
    for module in veri_modules_index.names:
        for line, kind, _ in journal_schema.writer_calls(veri_modules_index.text(module), module):
            if kind and kind not in documented:
                gaps.setdefault(kind, f"{module}.py:{line}")

    new = {kind: where for kind, where in gaps.items() if kind not in UNDOCUMENTED_KINDS}
    stale = sorted(kind for kind in UNDOCUMENTED_KINDS if kind not in gaps)

    assert not new, f"writers pass kinds JOURNAL.md has no row for: {new}"
    assert not stale, f"UNDOCUMENTED_KINDS lists kinds that are now documented or unwritten, remove them: {stale}"
