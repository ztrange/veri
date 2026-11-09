"""In-process cases for veri/growth.py, the one function that measures a session's context growth."""
import importlib

import pytest


@pytest.fixture
def growth():
    return importlib.import_module("veri.growth").growth


def test_growth_returns_none_not_zero_when_the_records_carry_no_usage_record_at_all(growth):
    records = [
        {"type": "system", "subtype": "init"},
        {"type": "assistant", "message": {"id": "m1", "content": []}},
        {"type": "user", "message": {"content": "hi"}},
    ]
    assert growth(records) is None
    assert growth([]) is None


def test_growth_is_the_last_usage_records_context_minus_the_baseline(growth):
    def turn(msg_id, inp, read, created):
        usage = {
            "input_tokens": inp,
            "cache_read_input_tokens": read,
            "cache_creation_input_tokens": created,
            "output_tokens": 999,
        }
        return {"type": "assistant", "message": {"id": msg_id, "usage": usage}}

    records = [turn("m1", 10, 20000, 5000), turn("m2", 7, 30000, 4000)]
    assert growth(records, 25000) == 7 + 30000 + 4000 - 25000


def test_growth_skips_records_with_no_usage_so_a_later_one_leaves_the_context_at_the_last_usage_record(growth):
    usage = {
        "input_tokens": 3,
        "cache_read_input_tokens": 40000,
        "cache_creation_input_tokens": 2000,
    }
    records = [
        {"type": "assistant", "message": {"id": "m1", "usage": usage}},
        {"type": "user", "message": {"content": "tool result"}},
        {"type": "assistant", "message": {"id": "m2", "content": []}},
        {"type": "system", "subtype": "note"},
    ]
    assert growth(records, 10000) == 3 + 40000 + 2000 - 10000


def test_growth_reads_a_session_transcript_row_without_type_assistant_as_a_usage_record(growth):
    usage = {
        "input_tokens": 4,
        "cache_read_input_tokens": 50000,
        "cache_creation_input_tokens": 1000,
    }
    records = [{"message": {"id": "m1", "role": "assistant", "usage": usage}}]
    assert growth(records, 20000) == 4 + 50000 + 1000 - 20000


def test_growth_reads_a_record_repeated_under_the_same_message_id_once_so_the_repeat_does_not_replace_its_first_context(growth):
    def turn(msg_id, read):
        usage = {
            "input_tokens": 1,
            "cache_read_input_tokens": read,
            "cache_creation_input_tokens": 0,
        }
        return {"type": "assistant", "message": {"id": msg_id, "usage": usage}}

    records = [turn("m1", 20000), turn("m2", 30000), turn("m1", 90000)]
    assert growth(records, 10000) == 1 + 30000 - 10000


def test_growth_with_no_baseline_given_takes_the_first_usage_records_context_of_a_single_session_as_the_baseline(growth):
    def turn(msg_id, read):
        usage = {
            "input_tokens": 2,
            "cache_read_input_tokens": read,
            "cache_creation_input_tokens": 100,
        }
        return {"type": "assistant", "message": {"id": msg_id, "usage": usage}}

    records = [
        {"type": "system", "subtype": "init"},
        turn("m1", 20000),
        turn("m2", 26000),
        turn("m3", 31000),
    ]
    assert growth(records) == (2 + 31000 + 100) - (2 + 20000 + 100)


def test_growth_with_no_baseline_given_takes_the_first_turn_of_the_last_session_as_the_baseline(growth):
    def turn(msg_id, read):
        usage = {
            "input_tokens": 2,
            "cache_read_input_tokens": read,
            "cache_creation_input_tokens": 100,
        }
        return {"type": "assistant", "message": {"id": msg_id, "usage": usage}}

    records = [
        {"type": "system", "subtype": "init"},
        turn("a1", 20000),
        turn("a2", 50000),
        {"type": "system", "subtype": "init"},
        turn("b1", 60000),
        turn("b2", 64000),
    ]
    assert growth(records) == 64000 - 60000


def test_growth_3389_returns_none_when_an_init_record_follows_the_last_usage_record_and_the_new_session_has_none_yet(growth):
    usage = {
        "input_tokens": 2,
        "cache_read_input_tokens": 20000,
        "cache_creation_input_tokens": 100,
    }
    records = [
        {"type": "assistant", "message": {"id": "m1", "usage": usage}},
        {"type": "system", "subtype": "init"},
    ]
    assert growth(records) is None
