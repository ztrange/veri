"""The interface index of veri/ (veri/README.md) names every shared module, and veri/ keeps its seams public."""
import ast
from collections import defaultdict

import pytest


def _modules(index):
    """{module name: its parsed tree}, from the session's one index of veri/."""
    return {name: index.tree(name) for name in index.names}


def _sibling_imports(tree, modules):
    """Yield (sibling module, names imported from it or None, alias bound to it or None) for each import."""
    for node in ast.walk(tree):
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


def _users(index):
    """{stem: tree} of the modules outside veri/ that count as its importers: the pytest leg, tests/leg/ (#4051)."""
    return index.user_trees() if hasattr(index, "user_trees") else {}


def _importers(index):
    modules = _modules(index)
    importers = defaultdict(set)
    for name, tree in {**modules, **_users(index)}.items():
        for target, _, _ in _sibling_imports(tree, modules):
            if target != name:
                importers[target].add(name)
    return importers


def _shared_modules(index):
    return {name for name, users in _importers(index).items() if len(users) >= 2}


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
def test_every_shared_module_has_a_section_in_the_index(veri_modules_index):
    missing = sorted(_shared_modules(veri_modules_index) - _index_sections())

    assert not missing, f"veri/README.md has no `## <module>` section for: {missing}"


@pytest.mark.tree_audit("every module of veri/")
def test_every_section_of_the_index_names_a_shared_module(veri_modules_index):
    stray = sorted(_index_sections() - _shared_modules(veri_modules_index))

    assert not stray, f"veri/README.md has sections for modules that do not exist or are not shared: {stray}"


@pytest.mark.tree_audit("every module of veri/")
def test_no_module_reaches_into_the_private_names_of_a_sibling(veri_modules_index):
    modules = _modules(veri_modules_index)
    reaches = []
    for name, tree in modules.items():
        aliases = {}
        for target, imported, alias in _sibling_imports(tree, modules):
            if target == name:
                continue
            reaches += [f"{name}: from {target} import {x}" for x in imported or [] if _private(x)]
            if alias:
                aliases[alias] = target
        for node in ast.walk(tree):
            if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                    and node.value.id in aliases and _private(node.attr)):
                reaches.append(f"{name}: {node.value.id}.{node.attr}")

    reaches = set(reaches) - KNOWN_REACHES

    assert not reaches, f"modules of veri/ read a sibling's underscore name: {sorted(reaches)}"


@pytest.mark.tree_audit("every module of veri/")
def test_every_module_has_a_docstring(veri_modules_index):
    bare = [name for name, tree in _modules(veri_modules_index).items()
            if not ast.get_docstring(tree)]

    assert not bare, f"modules of veri/ without a module docstring: {bare}"


# ---- groups: the README maps every module to one concept, and the tree obeys the directions it states ----

# The only imports that break a stated direction. A ratchet: the set may shrink, never grow; an entry that no longer
# occurs fails the case that checks it, so it is removed when the import is.
EXEMPT_DIRECTION_BREAKS = {
    # event.sh imports github to mirror an event onto the issue; Run state and journal builds on Foundations only.
    "event -> github",
    # event.sh imports metrics, only after an exit, step-done, bail, done or stage-end, to rewrite the issue's
    # published metrics file (PRD 035.2): the fold is the one definition of every figure, and it lives with the
    # operator's report.
    "event -> metrics",
}

# Import cycles the tree has: none. A ratchet like the list above; an entry is a frozenset of the modules in a cycle.
KNOWN_CYCLES = set()


def _readme_lines():
    from conftest import SCRIPTS

    return (SCRIPTS / "veri" / "README.md").read_text().splitlines()


def _module_named(token):
    """The module a backticked list token names: `ledger` is ledger, `add-ledger-step.sh` is add_ledger_step."""
    return token[: -len(".sh")].replace("-", "_") if token.endswith(".sh") else token


def _readme_groups():
    """{group: (names its list lines carry, names of its `## ` sections)}, in README order."""
    groups, current, in_sections = {}, None, False
    for number, line in enumerate(_readme_lines()):
        if line.startswith("# ") and number > 0 and line[2:].strip() != "Groups":
            current, in_sections = line[2:].strip(), False
            groups[current] = (set(), set())
        elif current and line.startswith("## "):
            in_sections = True
            groups[current][1].add(line[3:].strip().strip("`"))
        elif current and not in_sections and line.startswith("- `") and "`:" in line:
            groups[current][0].add(_module_named(line[3:line.index("`:")]))
    return groups


def _group_of():
    """{module: [groups naming it, by list line or section]}."""
    named = defaultdict(list)
    for group, (listed, sections) in _readme_groups().items():
        for name in listed | sections:
            named[name].append(group)
    return named


def _stated_directions():
    """({group: groups it may import}, groups nothing may import), from the README."""
    only, closed = {}, set()
    for line in _readme_lines():
        if " imports only: " in line and line.startswith("- "):
            group, _, allowed = line[2:].partition(" imports only: ")
            only[group] = set() if allowed.strip() == "nothing" else {g.strip() for g in allowed.split(";")}
        elif line.startswith("- Nothing imports "):
            closed.add(line[len("- Nothing imports "):].strip())
    return only, closed


def _group_import_breaks(index):
    group_of = _group_of()
    modules = _modules(index)
    only, closed = _stated_directions()
    breaks = set()
    for name, tree in modules.items():
        for target, _, _ in _sibling_imports(tree, modules):
            mine, theirs = group_of.get(name, [None])[0], group_of.get(target, [None])[0]
            if mine == theirs or name == target:
                continue
            if theirs in closed or (mine in only and theirs not in only[mine]):
                breaks.add(f"{name} -> {target}")
    return breaks


@pytest.mark.tree_audit("every module of veri/")
def test_every_module_is_in_exactly_one_group_of_the_index(veri_modules_index):
    named = _group_of()
    modules = set(_modules(veri_modules_index))

    assert sorted(modules - set(named)) == [], "modules in no group of veri/README.md"
    assert {name: groups for name, groups in named.items() if len(set(groups)) > 1} == {}, "modules in two groups"


@pytest.mark.tree_audit("every module of veri/")
def test_every_name_a_group_lists_is_a_module(veri_modules_index):
    named = set(_group_of())

    assert sorted(named - set(_modules(veri_modules_index))) == [], "veri/README.md names modules that do not exist"


@pytest.mark.tree_audit("every module of veri/")
def test_every_section_sits_in_the_group_that_lists_its_module():
    stray = []
    for group, (_, sections) in _readme_groups().items():
        for module in sections:
            elsewhere = [g for g, (listed, _) in _readme_groups().items() if module in listed and g != group]
            if elsewhere:
                stray.append(f"{module}: section in {group}, listed in {elsewhere}")

    assert not stray, f"sections outside their module's group: {stray}"


@pytest.mark.tree_audit("every module of veri/")
def test_the_directions_the_index_states_name_real_groups():
    only, closed = _stated_directions()
    groups = set(_readme_groups())

    assert only and closed
    assert (set(only) | closed | {g for allowed in only.values() for g in allowed}) <= groups


@pytest.mark.tree_audit("every module of veri/")
def test_no_group_imports_against_the_directions_the_index_states(veri_modules_index):
    breaks = _group_import_breaks(veri_modules_index)

    assert not breaks - EXEMPT_DIRECTION_BREAKS, f"imports against veri/README.md's directions: {sorted(breaks - EXEMPT_DIRECTION_BREAKS)}"
    assert not EXEMPT_DIRECTION_BREAKS - breaks, f"exemptions no longer needed, remove them: {sorted(EXEMPT_DIRECTION_BREAKS - breaks)}"


def _adding_a_script_section():
    """The lines of README's `### Adding a script`, up to the next heading."""
    lines = _readme_lines()
    start = lines.index("### Adding a script")
    end = next((n for n in range(start + 1, len(lines)) if lines[n].startswith("#")), len(lines))
    return lines[start:end]


def test_every_test_file_the_adding_a_script_checklist_names_exists():
    import re

    from conftest import SCRIPTS

    named = {token for line in _adding_a_script_section() for token in re.findall(r"`(tests/py/[\w/]*test_\w+\.py)`", line)}
    missing = sorted(token for token in named if not (SCRIPTS / token).is_file())

    assert len(named) >= 8, f"the checklist names {sorted(named)}: fewer test files than it had"
    assert not missing, f"veri/README.md's `Adding a script` names test files that do not exist: {missing}"


@pytest.mark.tree_audit("every module of veri/")
def test_the_only_import_cycles_are_the_known_ones(veri_modules_index):
    modules = _modules(veri_modules_index)
    reaches = {name: {t for t, _, _ in _sibling_imports(tree, modules) if t != name} for name, tree in modules.items()}

    def closure(start):
        seen, todo = set(), [start]
        while todo:
            for nxt in reaches[todo.pop()] - seen:
                seen.add(nxt)
                todo.append(nxt)
        return seen

    cycles = {frozenset({name} | {m for m in closure(name) if name in closure(m)})
              for name in modules if name in closure(name)}

    assert cycles == KNOWN_CYCLES
