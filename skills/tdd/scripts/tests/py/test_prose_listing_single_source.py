"""GRADED and REQUIREMENTS.md files are listed by one function under skills/tdd/scripts/veri/."""
import ast

import pytest


def listing_sites(tree, module):
    sites = set()

    def visit(node, scope):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scope = node.name
        if (isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.startswith("**/")):
            sites.add(f"{module}:{scope}")
        for child in ast.iter_child_nodes(node):
            visit(child, scope)

    visit(tree, "<module>")
    return sites


@pytest.mark.tree_audit("parses every module under skills/tdd/scripts/veri/ for a glob or pathspec naming GRADED or REQUIREMENTS.md")
def test_2674_one_function_lists_graded_and_requirements_files_at_any_depth(veri_modules_index):
    sites = set()
    for name in veri_modules_index.names:
        sites |= listing_sites(veri_modules_index.tree(name), veri_modules_index.path(name).name)
    assert len(sites) == 1, f"GRADED/REQUIREMENTS.md listed by {sorted(sites)}, expected exactly one function"


@pytest.mark.tree_audit("parses requirements.py for the glob or pathspec naming GRADED or REQUIREMENTS.md")
def test_2702_requirements_tracked_is_found_as_the_listing_site(veri_modules_index):
    assert listing_sites(veri_modules_index.tree("requirements"), "requirements.py") == {"requirements.py:tracked"}
