import importlib

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


@pytest.mark.tree_audit("one scratch test file")
def test_an_audit_cannot_mutate_the_walk_result_the_index_hands_it_2170(tests_py_index, tmp_path):
    path = tmp_path / "test_scratch.py"
    path.write_text(SCRATCH)
    walk = type(tests_py_index[0])(path).walk
    definition = walk.definitions[0]

    with pytest.raises(AttributeError):
        walk.definitions = ()
    with pytest.raises(AttributeError):
        definition.name = "other"
    with pytest.raises(TypeError):
        walk.definitions[0] = definition
    with pytest.raises((AttributeError, TypeError)):
        definition.literals.append("x")


# One planted case per shape the shared walk once dropped from "the text a case reads" (#2170): each reads SKILL.md's
# subsection only through that shape, so an audit blind to the shape stops naming it.
@pytest.mark.parametrize("audit, source", [
    ("test_skill_red_readers",
     'SKILL = "skills/tdd/SKILL.md"\n\n\ndef test_a(text):\n    assert SKILL in text, "#### Red"\n'),
    ("test_skill_green_readers",
     'SKILL = "skills/tdd/SKILL.md"\n\n\ndef test_a(text):\n    return SKILL, text.index(f"{\'#### Green\'} \u2014")\n'),
    ("test_skill_refactor_readers",
     'SKILL = "skills/tdd/SKILL.md"\n\n\ndef test_a(text):\n    assert SKILL and b"#### Refactor loop" in text\n'),
], ids=["assert-message", "f-string-nested-constant", "bytes-literal"])
@pytest.mark.tree_audit("one scratch test file")
def test_a_readers_audit_still_counts_a_skill_md_read_made_only_through_each_shape_it_once_dropped_2170(
        tests_py_index, tmp_path, audit, source):
    path = tmp_path / "test_scratch.py"
    path.write_text(source)
    entry = type(tests_py_index[0])(path)
    readers = importlib.import_module(audit)._readers
    extra = ({},) if readers.__code__.co_argcount == 4 else ()

    assert readers(entry, "", "", *extra) == ["test_a"]
