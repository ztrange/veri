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


def test_read_events_by_default_refuses_a_line_that_is_not_a_json_object_but_skips_blank_lines(tmp_path, event_log):
    blanks = tmp_path / "blanks.jsonl"
    blanks.write_text('{"event": "a"}\n\n   \n{"event": "b"}\n')
    not_json = tmp_path / "not-json.jsonl"
    not_json.write_text('{"event": "a"}\n\nnot json at all\n{"event": "b"}\n')
    not_object = tmp_path / "not-object.jsonl"
    not_object.write_text('{"event": "a"}\n\n[1, 2]\n{"event": "b"}\n')

    assert event_log.read_events(blanks) == [{"event": "a"}, {"event": "b"}]
    with pytest.raises(ValueError):
        event_log.read_events(not_json)
    with pytest.raises(ValueError):
        event_log.read_events(not_object)


def test_read_events_reads_a_log_holding_an_invalid_utf8_byte_without_raising_and_replaces_it_with_u_fffd(tmp_path, event_log):
    log = tmp_path / "events.jsonl"
    log.write_bytes(b'{"event": "a", "note": "bad\xff byte"}\n{"event": "b"}\n')

    assert event_log.read_events(log) == [
        {"event": "a", "note": "bad� byte"}, {"event": "b"}]


def test_read_events_2035_returns_a_line_with_an_undecodable_byte_as_u_fffd_whether_or_not_skip_unreadable_is_set(tmp_path, event_log):
    log = tmp_path / "events.jsonl"
    log.write_bytes(b'{"event": "a"}\n{"event": "b", "note": "bad\xff\xfe bytes"}\n')
    expected = [{"event": "a"}, {"event": "b", "note": "bad�� bytes"}]

    assert event_log.read_events(log) == expected
    assert event_log.read_events(log, skip_unreadable=True) == expected
