import ast
import pathlib

import pytest

VERI = pathlib.Path(__file__).resolve().parents[3] / "veri"


def is_call(node, name):
    return isinstance(node, ast.Call) and (
        getattr(node.func, "attr", getattr(node.func, "id", None)) == name)


def unresolved_file_locations(source):
    tree = ast.parse(source)
    resolved = {id(arg) for node in ast.walk(tree) if is_call(node, "realpath") for arg in node.args}
    return [node.lineno for node in ast.walk(tree)
            if is_call(node, "abspath") and id(node) not in resolved
            and any(isinstance(n, ast.Name) and n.id == "__file__" for a in node.args for n in ast.walk(a))]


@pytest.mark.tree_audit("reads the sources of skills/tdd/scripts/veri/*.py")
def test_no_veri_module_locates_itself_through_abspath_of_file_3501():
    found = {path.name: lines for path in sorted(VERI.glob("*.py"))
             if (lines := unresolved_file_locations(path.read_text()))}
    assert found == {}
