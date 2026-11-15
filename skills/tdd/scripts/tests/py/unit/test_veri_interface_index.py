"""The interface index of veri/ (veri/README.md) names every shared module, and veri/ keeps its seams public."""
import ast
from collections import defaultdict

import pytest


def _modules():
    from conftest import SCRIPTS

    return {source.stem: source for source in sorted((SCRIPTS / "veri").glob("*.py"))}


def _sibling_imports(source, modules):
    """Yield (sibling module, names imported from it or None, alias bound to it or None) for each import."""
    for node in ast.walk(ast.parse(source.read_text())):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if parts[0] in modules:
                    yield parts[0], None, alias.asname or parts[0]
                elif parts[0] == "veri" and len(parts) > 1 and parts[1] in modules:
                    yield parts[1], None, alias.asname
        elif isinstance(node, ast.ImportFrom):
            parts = node.module.split(".") if node.module else []
            if (node.level >= 1 and not parts) or parts == ["veri"]:
                for alias in node.names:
                    if alias.name in modules:
                        yield alias.name, None, alias.asname or alias.name
            elif parts and (node.level >= 1 or parts[0] != "veri") and parts[0] in modules:
                yield parts[0], [alias.name for alias in node.names], None
            elif parts and parts[0] == "veri" and node.level == 0 and len(parts) > 1 and parts[1] in modules:
                yield parts[1], [alias.name for alias in node.names], None


def _importers():
    modules = _modules()
    importers = defaultdict(set)
    for name, source in modules.items():
        for target, _, _ in _sibling_imports(source, modules):
            if target != name:
                importers[target].add(name)
    return importers


def _shared_modules():
    return {name for name, users in _importers().items() if len(users) >= 2}


def _index_sections():
    from conftest import SCRIPTS

    readme = SCRIPTS / "veri" / "README.md"
    if not readme.exists():
        return set()
    return {
        line[3:].strip().strip("`")
        for line in readme.read_text().splitlines()
        if line.startswith("## ")
    }


# wrong_test_route.py is owned by an open PR; case_reader keeps `_js_title_pattern` as an alias for it. Drop this
# when that module imports the public `js_title_pattern`.
KNOWN_REACHES = {"wrong_test_route: from case_reader import _js_title_pattern"}


def _private(name):
    return name.startswith("_") and not (name.startswith("__") and name.endswith("__"))


@pytest.mark.tree_audit("every module of veri/")
def test_every_shared_module_has_a_section_in_the_index():
    missing = sorted(_shared_modules() - _index_sections())

    assert not missing, f"veri/README.md has no `## <module>` section for: {missing}"


@pytest.mark.tree_audit("every module of veri/")
def test_every_section_of_the_index_names_a_shared_module():
    stray = sorted(_index_sections() - _shared_modules())

    assert not stray, f"veri/README.md has sections for modules that do not exist or are not shared: {stray}"


@pytest.mark.tree_audit("every module of veri/")
def test_no_module_reaches_into_the_private_names_of_a_sibling():
    modules = _modules()
    reaches = []
    for name, source in modules.items():
        aliases = {}
        for target, imported, alias in _sibling_imports(source, modules):
            if target == name:
                continue
            reaches += [f"{name}: from {target} import {x}" for x in imported or [] if _private(x)]
            if alias:
                aliases[alias] = target
        for node in ast.walk(ast.parse(source.read_text())):
            if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                    and node.value.id in aliases and _private(node.attr)):
                reaches.append(f"{name}: {node.value.id}.{node.attr}")

    reaches = set(reaches) - KNOWN_REACHES

    assert not reaches, f"modules of veri/ read a sibling's underscore name: {sorted(reaches)}"


@pytest.mark.tree_audit("every module of veri/")
def test_every_module_has_a_docstring():
    bare = [name for name, source in _modules().items()
            if not ast.get_docstring(ast.parse(source.read_text()))]

    assert not bare, f"modules of veri/ without a module docstring: {bare}"
