"""No case under tests/py carries the `serial` mark, so `make test` on veri ends after one pytest session (#3921).

The leg's two-pass mechanism stays for a future case that needs it. A mark is a source line that starts with the
decorator, or a `pytestmark` assignment naming it; a planted case inside a one-line string literal starts its line with
the quote, so it is not one.
"""
import pathlib
import re

import pytest

TESTS_PY = pathlib.Path(__file__).resolve().parent.parent
SERIAL_MARK = re.compile(r"^[ \t]*(?:@pytest\.mark\.serial\b|pytestmark\s*=.*\bpytest\.mark\.serial\b)", re.M)


def serial_marks(entries):
    """`<path under tests/py>:<line>` of each `serial` mark, from each entry's text."""
    return sorted(f"{entry.path.relative_to(TESTS_PY)}:{entry.text.count(chr(10), 0, match.start()) + 1}"
                  for entry in entries if "mark.serial" in entry.text for match in SERIAL_MARK.finditer(entry.text))


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py, searched for serial marks")
def test_no_case_under_tests_py_carries_the_serial_mark(tests_py_index):
    found = serial_marks(tests_py_index)
    assert found == [], "cases marked serial, which buys make test a second pytest pass:\n" + "\n".join(found)
