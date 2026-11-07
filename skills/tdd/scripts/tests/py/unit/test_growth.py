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
