import ast

import pytest


def _is_tree_audit(decorator):
    return (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == "tree_audit")


def _sweeps_every_test_file(tree):
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.args):
            continue
        arg = node.args[0]
        if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
            continue
        if node.func.attr == "rglob" and arg.value == "test_*.py":
            return True
        if node.func.attr == "glob" and arg.value == "**/test_*.py":
            return True
    return False


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_tree_audit_case_sweeping_all_test_files_uses_the_shared_index_2168(tests_py_index):
    stray = []
    for entry in tests_py_index:
        if entry.path.name == "conftest.py" or not _sweeps_every_test_file(entry.tree):
            continue
        for node in ast.walk(entry.tree):
            if not isinstance(node, ast.FunctionDef) or not any(_is_tree_audit(d) for d in node.decorator_list):
                continue
            if "tests_py_index" not in [a.arg for a in node.args.args]:
                stray.append(f"{entry.path.name}::{node.name}")
    assert stray == [], "tree_audit cases sweep every test file without the tests_py_index fixture:\n" + "\n".join(stray)
