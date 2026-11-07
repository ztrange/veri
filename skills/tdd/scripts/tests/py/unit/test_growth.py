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
