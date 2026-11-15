"""In-process cases for veri/leaf_log.py, the one scan of a leaf's stream-json log for its result records."""
import importlib
import json

import pytest


@pytest.fixture
def leaf_log():
    return importlib.import_module("veri.leaf_log")


def line(**record):
    return json.dumps(record)


def test_result_text_is_the_result_string_of_a_result_record_line_str_or_bytes(leaf_log):
    record = line(type="result", result="PASS")
    assert (leaf_log.result_text(record), leaf_log.result_text(record.encode())) == ("PASS", "PASS")


@pytest.mark.parametrize("not_a_result", [
    line(type="assistant", result="x"),
    line(type="result", result=None),
    line(type="result", result=7),
    line(type="result"),
    "[1, 2]",
    "not json",
    "",
    b"\xff\xfe{",
])
def test_result_text_is_none_for_a_line_that_is_not_a_result_record_with_a_string_result(leaf_log, not_a_result):
    assert leaf_log.result_text(not_a_result) is None


def test_result_texts_lists_every_result_string_in_log_order(leaf_log):
    lines = [line(type="system"), line(type="result", result="a"), "junk",
             line(type="result", result=3), line(type="result", result="b")]
    assert leaf_log.result_texts(lines) == ["a", "b"]


def test_last_result_text_is_the_final_result_string_and_none_when_there_is_none(leaf_log):
    assert leaf_log.last_result_text([line(type="result", result="a"), line(type="result", result="b")]) == "b"
    assert leaf_log.last_result_text([line(type="system")]) is None


def test_cost_sums_total_cost_usd_over_result_records_that_carry_a_result(leaf_log):
    lines = [line(type="result", result="a", total_cost_usd=0.25),
             line(type="result", result="b", total_cost_usd=None),
             line(type="result", result="c"),
             line(type="result", total_cost_usd=9),
             line(type="assistant", result="d", total_cost_usd=5),
             line(type="result", result="e", total_cost_usd="0.5")]
    assert leaf_log.cost(lines) == 0.75
