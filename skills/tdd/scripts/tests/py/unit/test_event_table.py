"""veri/event_table.py is the one table of every event veri emits and its keys (PRD 030.1)."""
import ast

import pytest

from conftest import SCRIPTS

TABLE = SCRIPTS / "veri" / "event_table.py"


def test_the_table_module_imports_no_other_veri_module():
    tree = ast.parse(TABLE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    siblings = sorted(name for name in imported if name == "veri" or (SCRIPTS / "veri" / f"{name}.py").exists())

    assert not siblings, f"veri/event_table.py imports veri modules {siblings}; it must be readable alone"


def test_the_table_declares_the_five_events_journal_md_lacked_with_the_keys_their_writers_pass():
    from veri import event_table

    written = {"grading": {"unit", "verdict", "failing", "cost_usd", "id"}, "unpinnable-missing": {"step"},
               "prose-owed-waived": {"unit", "step"}, "suite-flake": {"at", "files"}, "skill-edit-no-author": {"unit"}}

    assert {event: set(event_table.keys(event)) for event in written} == written
    assert event_table.required("suite-flake") == {"files"}


def test_journal_md_lists_exactly_the_events_and_keys_the_table_declares():
    from veri import event_table, journal_schema

    page = (SCRIPTS.parent / "JOURNAL.md").read_text(encoding="utf-8")
    drift = []
    for event in sorted(set(event_table.EVENTS) | journal_schema.kinds(page)):
        if event not in event_table.EVENTS:
            drift.append(f"{event}: a JOURNAL.md row, not in veri/event_table.py's EVENTS")
            continue
        documented = journal_schema.fields(page, event)
        if documented is None:
            drift.append(f"{event}: in veri/event_table.py's EVENTS, no JOURNAL.md row")
            continue
        drift += [f"{event} key {key}: in veri/event_table.py's EVENTS, not in its JOURNAL.md row"
                  for key in event_table.keys(event) if key not in documented]
        drift += [f"{event} key {key}: in its JOURNAL.md row, not in veri/event_table.py's EVENTS"
                  for key in documented if key not in event_table.keys(event)]

    assert not drift, "skills/tdd/JOURNAL.md and veri/event_table.py differ:\n" + "\n".join(drift)


@pytest.mark.tree_audit("reads every .sh and .md file under skills/ for event.sh call sites")
def test_every_literal_event_and_key_of_an_event_sh_call_under_skills_is_declared_in_the_table():
    from event_roster import event_sh_call_sites
    from veri import event_table

    sites = event_sh_call_sites()
    assert any(keys for _, _, keys in sites), "no event.sh call site with a key found under skills/"
    gaps = [f"{where}: event {event!r} is not in veri/event_table.py; add  {event_table.declaring(event, None)}"
            for where, event, _ in sites if event not in event_table.EVENTS]
    gaps += [f"{where}: event {event!r} key {key!r} is not in veri/event_table.py; make its line"
             f"  {event_table.declaring(event, key)}"
             for where, event, keys in sites if event in event_table.EVENTS
             for key in keys if key not in event_table.keys(event)]

    assert not gaps, "event.sh call sites under skills/ the table does not declare:\n" + "\n".join(gaps)
