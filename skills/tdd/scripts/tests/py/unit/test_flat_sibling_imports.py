"""A module of veri/ imports its siblings flat (`import git`, `from ledger import x`), with no fallback."""
import ast

import pytest


def _package_imports(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.level >= 1 or (node.module or "").split(".")[0] == "veri"):
            yield f"line {node.lineno}: from {'.' * node.level}{node.module or ''} import {', '.join(a.name for a in node.names)}"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] == "veri":
                    yield f"line {node.lineno}: import {alias.name}"


@pytest.mark.tree_audit("skills/tdd/scripts/veri")
def test_no_module_imports_a_sibling_relatively_or_through_the_package_name(veri_modules_index):
    offenders = {
        name: sorted(_package_imports(veri_modules_index.tree(name)))
        for name in veri_modules_index.names
    }
    offenders = {name: lines for name, lines in offenders.items() if lines}

    assert not offenders, f"modules of veri/ import a sibling other than flat: {sorted(offenders)}"
