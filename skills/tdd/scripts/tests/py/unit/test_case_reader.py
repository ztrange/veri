"""In-process cases for veri/case_reader.py."""
import importlib


def test_strip_param_suffix_strips_a_trailing_bracket_and_leaves_a_plain_name_unchanged():
    case_reader = importlib.import_module("veri.case_reader")

    assert case_reader.strip_param_suffix("test_x[a-b]") == "test_x"
    assert case_reader.strip_param_suffix("test_x") == "test_x"
