"""A writer passes only events and keys veri/event_table.py declares (PRD 030.1, ET6)."""
import pytest
from veri import event_table, journal_schema


def _writes(index):
    """{(kind, field): 'file:line'} for every literal field a writer passes to a literal kind (field None: the kind)."""
    found = {}
    for module in index.names:
        for line, kind, names in journal_schema.writer_calls(index.text(module), module):
            for name in [None, *names] if kind else ():
                found.setdefault((kind, name), f"{module}.py:{line}")
    return found


def _undeclared(writes):
    return {key: where for key, where in writes.items()
            if key[0] not in event_table.EVENTS or (key[1] and key[1] not in event_table.keys(key[0]))}


def _report(gaps):
    return "\n".join(f"{where}: event {kind!r}" + (f" key {key!r}" if key else "") + " is not in veri/event_table.py;"
                     f" declare it with the line  {event_table.declaring(kind, key)}"
                     for (kind, key), where in sorted(gaps.items(), key=lambda item: (item[0][0], item[0][1] or "")))


@pytest.mark.tree_audit("skills/tdd/scripts/veri")
def test_every_literal_event_and_key_a_writer_passes_is_declared_in_the_table(veri_modules_index):
    """Walks `event.mark`/`event.append`, `verify.mark`, `supervise.mark` and `push_branch.record` calls
    (and the bare `mark`/`record` inside the modules that define them) with `ast`, and fails when a call
    whose kind is a string literal names a kind the table does not hold, or passes a field written as a
    literal `"name=…"` the table does not declare for it.

    It cannot see: a computed kind (`event.mark(d, c, event_name, …)`), `**fields`, a field list built in a
    variable (`harvest_usage`'s `pairs`) or a field whose name is not a literal; calls reached through a
    wrapper other than the five shapes; and events that prose writes through `event.sh`."""
    gaps = _undeclared(_writes(veri_modules_index))

    assert not gaps, "writers pass events or keys the table does not declare:\n" + _report(gaps)


def test_an_undeclared_key_or_event_is_reported_with_its_site_and_the_line_to_add():
    gaps = _undeclared({("comment", "kind"): "comment.py:1", ("comment", "colour"): "comment.py:2",
                        ("no-such-event", None): "x.py:3"})

    assert _report(gaps) == (
        "comment.py:2: event 'comment' key 'colour' is not in veri/event_table.py; declare it with the line"
        '  "comment": "%s colour?:text",\n' % event_table.EVENTS["comment"] +
        "x.py:3: event 'no-such-event' is not in veri/event_table.py; declare it with the line  \"no-such-event\": \"\",")


@pytest.mark.tree_audit("skills/tdd/scripts/veri")
def test_the_walk_sees_the_writers_of_the_tree(veri_modules_index):
    kinds = {kind for kind, _ in _writes(veri_modules_index)}

    assert {"bail", "verdict", "launch", "merged", "test-run"} <= kinds
