"""The captured journal under fixtures/journal/ uses only events and keys veri/event_table.py declares (PRD 030.1, ET7)."""
import json
import pathlib

import pytest

from veri import event_table

ROOT = pathlib.Path(__file__).resolve().parents[6]
FIXTURES = ROOT / "fixtures" / "journal"


def undeclared(lines, name):
    """One problem line per event or key of the JSON lines that the table does not declare."""
    problems = []
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        record = json.loads(line)
        event = record.get("event")
        if event not in event_table.EVENTS:
            problems.append("%s:%d event %r is not declared; add  %s" % (name, n, event, event_table.declaring(event, None)))
            continue
        for key in record:
            if key not in event_table.COMMON and key not in event_table.keys(event):
                problems.append("%s:%d key %r of event %r is not declared; make its line  %s"
                                % (name, n, key, event, event_table.declaring(event, key)))
    return problems


def test_an_undeclared_event_or_key_of_a_journal_line_is_a_problem():
    lines = ['{"ts": 1, "awake": 2, "issue": "7", "event": "comment", "kind": "red", "url": "u"}',
             '{"ts": 1, "event": "comment", "colour": "red"}', '{"ts": 1, "event": "no-such-event"}']

    assert undeclared(lines, "x.jsonl") == [
        "x.jsonl:2 key 'colour' of event 'comment' is not declared; make its line  \"comment\": \"kind url colour?\",",
        "x.jsonl:3 event 'no-such-event' is not declared; add  \"no-such-event\": \"\","]


@pytest.mark.tree_audit("lists fixtures/journal/ for its captured journals")
def test_every_event_and_key_in_the_fixture_journal_is_declared_in_the_table():
    files = sorted(FIXTURES.glob("*.jsonl"))
    assert files, "no fixture journal under fixtures/journal/"
    problems = []
    for path in files:
        problems += undeclared(path.read_text(encoding="utf-8").splitlines(), path.name)
    assert not problems, "veri/event_table.py does not declare:\n" + "\n".join(problems)
