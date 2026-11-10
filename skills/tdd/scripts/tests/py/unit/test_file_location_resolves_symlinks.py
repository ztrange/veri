import ast
import pathlib

import pytest

VERI = pathlib.Path(__file__).resolve().parents[3] / "veri"


def is_call(node, name):
    return isinstance(node, ast.Call) and (
        getattr(node.func, "attr", getattr(node.func, "id", None)) == name)


def names_file_unresolved(node):
    """True if __file__ occurs under node without a realpath call between them."""
    if isinstance(node, ast.Name):
        return node.id == "__file__"
    if is_call(node, "realpath"):
        return False
    return any(names_file_unresolved(child) for child in ast.iter_child_nodes(node))


def unresolved_file_locations(source):
    # abspath collapses ".." textually, so wrapping it in realpath is too late:
    # any abspath over a path still holding __file__ unresolved is the bug.
    return [node.lineno for node in ast.walk(ast.parse(source))
            if is_call(node, "abspath") and any(names_file_unresolved(a) for a in node.args)]


@pytest.mark.tree_audit("reads the sources of skills/tdd/scripts/veri/*.py")
def test_no_veri_module_locates_itself_through_abspath_of_file_3501():
    found = {path.name: lines for path in sorted(VERI.glob("*.py"))
             if (lines := unresolved_file_locations(path.read_text()))}
    assert found == {}
