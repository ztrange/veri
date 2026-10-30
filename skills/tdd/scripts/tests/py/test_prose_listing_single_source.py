"""GRADED and REQUIREMENTS.md files are listed by one function under skills/tdd/scripts/veri/."""
import ast
import pathlib

import pytest

VERI = pathlib.Path(__file__).resolve().parents[2] / "veri"
LISTED = ("GRADED", "REQUIREMENTS.md")


def listing_sites(tree, module):
    sites = set()

    def visit(node, scope):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scope = node.name
        if (isinstance(node, ast.Constant) and isinstance(node.value, str) and "*" in node.value
                and not node.value.startswith(":(exclude") and any(name in node.value for name in LISTED)):
            sites.add(f"{module}:{scope}")
        for child in ast.iter_child_nodes(node):
            visit(child, scope)

    visit(tree, "<module>")
    return sites


@pytest.mark.tree_audit("parses every module under skills/tdd/scripts/veri/ for a glob or pathspec naming GRADED or REQUIREMENTS.md")
def test_2674_one_function_lists_graded_and_requirements_files_at_any_depth():
    sites = set()
    for path in sorted(VERI.glob("*.py")):
        sites |= listing_sites(ast.parse(path.read_text(encoding="utf-8")), path.name)
    assert len(sites) == 1, f"GRADED/REQUIREMENTS.md listed by {sorted(sites)}, expected exactly one function"
