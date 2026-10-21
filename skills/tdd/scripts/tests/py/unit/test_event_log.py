"""In-process cases for veri/event_log.py, the one per-line parse of a run's events.jsonl."""
import importlib

import pytest


@pytest.fixture
def event_log():
    return importlib.import_module("veri.event_log")


def test_read_events_with_skip_unreadable_returns_the_events_of_the_other_lines_in_order(tmp_path, event_log):
    log = tmp_path / "events.jsonl"
    log.write_text(
        '{"event": "a"}\n'
        '\n'
        'not json at all\n'
        '[1, 2]\n'
        '{"event": "b"}\n'
        '"a string"\n'
        '{"event": "c"}\n')

    assert event_log.read_events(log, skip_unreadable=True) == [
        {"event": "a"}, {"event": "b"}, {"event": "c"}]
