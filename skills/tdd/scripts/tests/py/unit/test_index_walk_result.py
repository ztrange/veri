import pytest

SCRATCH = '''LIMIT = "alpha"


def test_a(tmp):
    assert tmp.read("beta"), "gamma"
    return f"delta {other}"
'''


@pytest.mark.tree_audit("one scratch test file")
def test_an_index_entry_walk_result_lists_each_module_level_definition_with_what_audits_query_2170(
        tests_py_index, tmp_path):
    path = tmp_path / "test_scratch.py"
    path.write_text(SCRATCH)
    entry = type(tests_py_index[0])(path)

    by_name = {definition.name: definition for definition in entry.walk.definitions}

    assert sorted(by_name) == ["LIMIT", "test_a"]
    assert by_name["LIMIT"].segment == 'LIMIT = "alpha"'
    assert set(by_name["LIMIT"].literals) == {"alpha"}
    function = by_name["test_a"]
    assert function.segment == SCRATCH.split("\n\n\n")[1].rstrip("\n")
    assert {"beta", "gamma"} <= set(function.literals)
    assert {"tmp", "other"} <= set(function.names)
    assert set(function.constants) == {"beta"}
