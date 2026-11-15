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


def test_read_events_2035_by_default_refuses_a_line_that_is_not_a_json_object_with_a_value_error_naming_the_log_path(tmp_path, event_log):
    log = tmp_path / "events.jsonl"
    log.write_text('{"event": "a"}\n[1, 2]\n')

    with pytest.raises(ValueError) as refused:
        event_log.read_events(log)

    assert str(log) in str(refused.value)


def test_read_events_2035_with_errors_strict_keeps_raising_unicode_decode_error_whether_or_not_skip_unreadable_is_set(tmp_path, event_log):
    log = tmp_path / "events.jsonl"
    log.write_bytes(b'{"event": "a"}\n{"event": "b", "note": "bad\xff byte"}\n')

    with pytest.raises(UnicodeDecodeError):
        event_log.read_events(log, errors="strict")
    with pytest.raises(UnicodeDecodeError):
        event_log.read_events(log, skip_unreadable=True, errors="strict")


def _journal(tmp_path, text):
    (tmp_path / ".tdd").mkdir(exist_ok=True)
    (tmp_path / ".tdd" / "events.jsonl").write_text(text)
    return str(tmp_path)


def test_journal_path_is_events_jsonl_under_the_runs_tdd_directory(event_log):
    assert event_log.path("/some/run") == "/some/run/.tdd/events.jsonl"


def test_events_without_kinds_returns_every_event_in_order_and_skips_blank_lines(tmp_path, event_log):
    run = _journal(tmp_path, '{"event": "a"}\n\n   \n{"event": "b"}\n')

    assert event_log.events(run) == [{"event": "a"}, {"event": "b"}]


def test_events_of_a_run_with_no_journal_is_an_empty_list(tmp_path, event_log):
    assert event_log.events(str(tmp_path)) == []
    assert event_log.events(str(tmp_path), "done") == []


def test_events_with_kinds_keeps_only_those_kinds_in_journal_order(tmp_path, event_log):
    run = _journal(tmp_path, '{"event": "a", "n": 1}\n{"event": "b"}\n{"event": "c"}\n{"event": "a", "n": 2}\n')

    assert event_log.events(run, "a") == [{"event": "a", "n": 1}, {"event": "a", "n": 2}]
    assert event_log.events(run, "c", "b") == [{"event": "b"}, {"event": "c"}]
    assert event_log.events(run, "zzz") == []


def test_events_by_default_refuses_an_unreadable_line_naming_the_journal(tmp_path, event_log):
    run = _journal(tmp_path, '{"event": "a"}\nnot json\n')

    with pytest.raises(ValueError, match="events.jsonl"):
        event_log.events(run)


def test_events_with_skip_unreadable_drops_unreadable_lines(tmp_path, event_log):
    run = _journal(tmp_path, '{"event": "a"}\nnot json\n[1]\n{"event": "b"}\n')

    assert event_log.events(run, skip_unreadable=True) == [{"event": "a"}, {"event": "b"}]
    assert event_log.events(run, "b", skip_unreadable=True) == [{"event": "b"}]


def test_events_errors_strict_refuses_an_undecodable_byte_and_default_replaces_it(tmp_path, event_log):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_bytes(b'{"event": "a", "note": "x\xff"}\n')

    assert event_log.events(str(tmp_path))[0]["note"] == "x�"
    with pytest.raises(ValueError):
        event_log.events(str(tmp_path), errors="strict")


def test_last_returns_the_last_event_of_a_kind(tmp_path, event_log):
    run = _journal(tmp_path, '{"event": "bail", "n": 1}\n{"event": "x"}\n{"event": "bail", "n": 2}\n{"event": "x"}\n')

    assert event_log.last(run, "bail") == {"event": "bail", "n": 2}


def test_last_is_none_when_the_kind_is_absent_or_the_journal_missing(tmp_path, event_log):
    assert event_log.last(str(tmp_path), "done") is None
    run = _journal(tmp_path, '{"event": "x"}\n')
    assert event_log.last(run, "done") is None


def test_last_passes_the_tolerance_flags_through(tmp_path, event_log):
    run = _journal(tmp_path, '{"event": "done", "pr": 1}\nnot json\n')

    with pytest.raises(ValueError):
        event_log.last(run, "done")
    assert event_log.last(run, "done", skip_unreadable=True) == {"event": "done", "pr": 1}
