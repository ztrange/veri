"""No case under tests/py carries the `serial` mark, so `make test` on veri ends after one pytest session (#3921).

The leg's two-pass mechanism stays for a future case that needs it; a planted case inside a string literal is not a case.
"""
import ast
import pathlib

import pytest

TESTS_PY = pathlib.Path(__file__).resolve().parent


def _is_serial(node):
    node = node.func if isinstance(node, ast.Call) else node
    return (isinstance(node, ast.Attribute) and node.attr == "serial"
            and isinstance(node.value, ast.Attribute) and node.value.attr == "mark")


def serial_marks(entries):
    """`<path under tests/py>:<line>` of each `serial` mark on a function, a class or a module's `pytestmark`."""
    found = []
    for entry in entries:
        for node in ast.walk(entry.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                marks = node.decorator_list
            elif isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "pytestmark" for t in node.targets):
                marks = node.value.elts if isinstance(node.value, (ast.List, ast.Tuple)) else [node.value]
            else:
                continue
            found += [f"{entry.path.relative_to(TESTS_PY)}:{mark.lineno}" for mark in marks if _is_serial(mark)]
    return sorted(found)


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py, parsed for serial marks")
def test_no_case_under_tests_py_carries_the_serial_mark(tests_py_index):
    found = serial_marks(tests_py_index)
    assert found == [], "cases marked serial, which buys make test a second pytest pass:\n" + "\n".join(found)
