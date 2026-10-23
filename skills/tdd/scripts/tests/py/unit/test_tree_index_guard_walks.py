import ast
import pathlib
import types

import pytest

import test_tree_index_guard

PLANTED = '''import ast
import pytest

@pytest.mark.tree_audit("x")
def test_planted_walker_2170(tests_py_index):
    return [n for entry in tests_py_index for n in ast.walk(entry.tree)]
'''


def test_2170_the_guard_names_a_tree_audit_case_that_walks_its_entrys_tree_itself():
    entry = types.SimpleNamespace(path=pathlib.Path("test_planted.py"), tree=ast.parse(PLANTED))
    with pytest.raises(AssertionError) as raised:
        test_tree_index_guard.test_every_tree_audit_case_sweeping_all_test_files_uses_the_shared_index_2168([entry])
    assert "test_planted.py::test_planted_walker_2170" in str(raised.value)
