"""Cases for entry.whole_number, the one check that a string is a whole number of at least `minimum`."""
import importlib

import pytest


@pytest.mark.parametrize("text, minimum, expected", [
    ("1", 1, 1), ("7", 1, 7), ("007", 1, 7), ("0", 0, 0), ("000", 0, 0), ("5", 5, 5),
    ("0", 1, None), ("00", 1, None), ("4", 5, None),
    ("", 0, None), ("-1", 0, None), ("+1", 1, None), (" 7", 1, None), ("7 ", 1, None), ("7\n", 1, None),
    ("1.5", 1, None), ("1e3", 1, None), ("abc", 1, None),
    ("²", 1, None), ("٣", 1, None), ("１", 1, None),
])
def test_whole_number_is_the_int_of_ascii_digits_at_or_above_the_minimum_else_none(text, minimum, expected):
    entry = importlib.import_module("veri.entry")

    assert entry.whole_number(text, minimum) == expected


def test_the_minimum_defaults_to_one():
    entry = importlib.import_module("veri.entry")

    assert (entry.whole_number("0"), entry.whole_number("1")) == (None, 1)
