"""A module of veri/ imports its siblings flat (`import git`, `from ledger import x`), with no fallback."""
import ast

import pytest

# The pytest-leg plugins are loaded by name from pytest_leg.py (PYTEST_PLUGINS) in a process that may not have veri/
# first on sys.path, so a flat import of a sibling could fail there; they name their sibling through the package.
PYTEST_LEG_PLUGINS = {"network_guard", "small_case_guard"}


def _package_imports(source):
    for node in ast.walk(ast.parse(source.read_text())):
        if isinstance(node, ast.ImportFrom) and (node.level >= 1 or (node.module or "").split(".")[0] == "veri"):
            yield f"line {node.lineno}: from {'.' * node.level}{node.module or ''} import {', '.join(a.name for a in node.names)}"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] == "veri":
                    yield f"line {node.lineno}: import {alias.name}"


@pytest.mark.tree_audit("skills/tdd/scripts/veri")
def test_no_module_imports_a_sibling_relatively_or_through_the_package_name():
    from conftest import SCRIPTS

    offenders = {
        source.stem: sorted(_package_imports(source))
        for source in sorted((SCRIPTS / "veri").glob("*.py"))
        if source.stem not in PYTEST_LEG_PLUGINS
    }
    offenders = {name: lines for name, lines in offenders.items() if lines}

    assert not offenders, f"modules of veri/ import a sibling other than flat: {sorted(offenders)}"
