"""Every name read through tunables.read, read_bytes or pop is a knob (TUNABLES) or says why it is not (NOT_KNOBS)."""
import ast
import importlib

import pytest

VERBS = {"read", "read_bytes", "pop"}

# A name its one reader holds alone, so no table in tunables.py may name it: only event.py may write VERI_HOME's
# journal (test_event_journal.py's test_only_event_py_outside_the_tests_names_veri_home_so_nothing_else_writes_there).
# An operator's knob (default ~/.veri, computed by event.py). Kept here, not in tunables.py, by that guard.
OWN_READER = {"VERI_HOME": "event.py"}


def unlisted(tree, listed):
    """[(line, name)] for each literal name passed to tunables.read, read_bytes or pop that `listed` lacks."""
    return sorted({(node.lineno, node.args[0].value) for node in ast.walk(tree)
                   if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                   and node.func.attr in VERBS and isinstance(node.func.value, ast.Name)
                   and node.func.value.id == "tunables" and node.args
                   and isinstance(node.args[0], ast.Constant) and node.args[0].value not in listed})


def listed_names():
    tunables = importlib.import_module("veri.tunables")
    return set(tunables.TUNABLES) | set(tunables.NOT_KNOBS)


def test_4047_a_planted_read_of_a_name_in_neither_table_is_named_and_listed_ones_are_not():
    source = ('import tunables\ntunables.read("VERI_LABEL")\ntunables.read_bytes("VERI_AWAKE_CLOCK")\n'
              'tunables.pop("VERI_PLANTED_UNLISTED")\n')

    assert unlisted(ast.parse(source), listed_names()) == [(4, "VERI_PLANTED_UNLISTED")]


def test_4047_not_knobs_says_run_state_or_test_stand_in_for_each_name_and_none_is_also_a_knob():
    tunables = importlib.import_module("veri.tunables")

    assert set(tunables.NOT_KNOBS.values()) <= {"run state", "test stand-in"}
    assert set(tunables.NOT_KNOBS) & set(tunables.TUNABLES) == set()


@pytest.mark.tree_audit("skills/tdd/scripts/veri")
def test_4047_every_name_veri_reads_through_read_read_bytes_or_pop_is_a_knob_or_says_why_not(veri_modules_index):
    listed = listed_names()
    found = {f"{module}.py:{line}": name for module in veri_modules_index.names
             for line, name in unlisted(veri_modules_index.tree(module), listed)
             if OWN_READER.get(name) != f"{module}.py"}

    assert found == {}


def test_4047_a_name_with_its_own_reader_is_in_neither_table():
    assert set(OWN_READER) & listed_names() == set()
