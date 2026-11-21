"""A VERI_* name read with a literal default anywhere in veri/ is a site this audit names, unless EXEMPT says why.

The tunables table states each default once; a literal default beside a read is a second statement of it.
This covers every `VERI_*` name, defined in `tunables.TUNABLES` or not.

What the audit sees, by `ast`: a call whose first argument is the name as a string literal and whose
function is called `read`, `read_bytes`, `get`, `getenv`, `numeric_env` or `wait_seconds` (so
`tunables.read(N, "5")`, `tunables.read(N, unless_empty="5")`, `os.environ.get(N, "5")`,
`numeric_env(N, "5")`, `wait_seconds(N, "5", 0)`) with a further string or bytes literal argument;
and `<such a call> or "5"`. What it cannot see: a name held in a variable or built by concatenation
(`tunables.read(budget_var) or "5"`), a default reached through a constant (`DEFAULT = "5"`), a default
spelled as an f-string or a computed value, a read through `tunables.environment()` or a copied
mapping, and a literal compared to the value afterwards (`if raw == "5"`).
"""
import ast

import pytest

READERS = {"read", "read_bytes", "get", "getenv", "numeric_env", "wait_seconds"}

# (module, name): why this site still writes its own literal default.
EXEMPT = {
    ("detach_command.py", "VERI_POLL"):
        "VERI_POLL has two purposes and several defaults (1, 10), declined: no single default to state",
    ("github.py", "VERI_POLL"):
        "VERI_POLL, default 10 here, 1 elsewhere: two purposes, two defaults, declined",
    ("parallel_conductors.py", "VERI_POLL"):
        "VERI_POLL, default 1 here, 10 in github.py and wait_ci.py: two purposes, declined",
    ("supervise.py", "VERI_POLL"):
        "VERI_POLL, default 1 here, 10 in github.py and wait_ci.py: two purposes, declined",
    ("wait_ci.py", "VERI_POLL"):
        "VERI_POLL, default 10 here, 1 in supervise.py and wait_leaf.py: two purposes, declined",
    ("wait_leaf.py", "VERI_POLL"):
        "VERI_POLL, default 1 here, 10 in github.py and wait_ci.py: two purposes, declined",
    ("build_develop_prompt.py", "VERI_ISSUE"):
        "a run-context field the conductor exports, not a tunable: `or \"\"` states no default, only its absence",
    ("supervise.py", "VERI_STEP"):
        "a run-context field the conductor exports, not a tunable: `or \"\"` states no default, only its absence",
}


class _AnyVeri:
    """Every name that starts `VERI_`: the `names` of a scan that does not depend on what TUNABLES defines."""

    def __contains__(self, name):
        return isinstance(name, str) and name.startswith("VERI_")


ANY_VERI = _AnyVeri()


def _name(call):
    function = call.func
    return function.attr if isinstance(function, ast.Attribute) else getattr(function, "id", None)


def _is_literal(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes))


def _read_of(node, names):
    """The VERI name a reader call reads, or None."""
    if (isinstance(node, ast.Call) and _name(node) in READERS and node.args
            and isinstance(node.args[0], ast.Constant) and node.args[0].value in names):
        return node.args[0].value
    return None


def literal_defaults(source, names):
    return literal_defaults_in(ast.parse(source), names)


def literal_defaults_in(tree, names):
    """[(line, name)] for each read of a name in `names` that carries a literal default."""
    found = []
    for node in ast.walk(tree):
        name = _read_of(node, names)
        if name and (any(_is_literal(a) for a in node.args[1:]) or any(_is_literal(k.value) for k in node.keywords)):
            found.append((node.lineno, name))
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            name = _read_of(node.values[0], names)
            if name and any(_is_literal(v) for v in node.values[1:]):
                found.append((node.lineno, name))
    return sorted(set(found))


NAMES = {"VERI_X"}


@pytest.mark.parametrize("source", [
    'tunables.read("VERI_ANYTHING", "5")',
    'tunables.read("VERI_ANYTHING") or "5"',
    'os.environ.get("VERI_ANYTHING", "5")',
])
def test_any_veri_name_with_a_literal_default_is_named_when_no_names_are_given(source):
    assert literal_defaults("import os\n" + source + "\n", ANY_VERI) == [(2, "VERI_ANYTHING")]


@pytest.mark.parametrize("source", [
    'tunables.read("VERI_ANYTHING")',
    'tunables.get("VERI_ANYTHING")',
    'tunables.read("CLAUDE_BIN", "x")',
    'os.environ.get("HOME", "x")',
])
def test_a_read_without_a_literal_default_or_of_a_non_veri_name_is_not_named(source):
    assert literal_defaults("import os\n" + source + "\n", ANY_VERI) == []


@pytest.mark.parametrize("source", [
    'tunables.read("VERI_X", "5")',
    'tunables.read("VERI_X", unless_empty="5")',
    'tunables.read("VERI_X") or "5"',
    'os.environ.get("VERI_X", "5")',
    'os.environ.get("VERI_X") or "5"',
    'numeric_env("VERI_X", "5")',
    'github.wait_seconds("VERI_X", "5", 0)',
    'tunables.read_bytes("VERI_X") or b"5"',
])
def test_a_planted_literal_default_for_a_defined_name_is_named(source):
    assert literal_defaults("import os\n" + source + "\n", NAMES) == [(2, "VERI_X")]


@pytest.mark.parametrize("source", [
    'tunables.get("VERI_X")',
    'tunables.get("VERI_X", unless_empty=True)',
    'tunables.read("VERI_X")',
    'tunables.read("VERI_OTHER", "5")',
    'os.environ.get("VERI_OTHER") or "5"',
    'tunables.read("VERI_X") or tunables.default("VERI_X")',
])
def test_a_read_that_asks_tunables_or_reads_another_name_is_not_named(source):
    assert literal_defaults("import os\n" + source + "\n", NAMES) == []


@pytest.mark.tree_audit("skills/tdd/scripts/veri")
def test_no_module_writes_a_literal_default_for_any_veri_name(veri_modules_index):
    names = ANY_VERI
    found = {}
    for module in veri_modules_index.names:
        if module == "tunables":
            continue
        for line, name in literal_defaults_in(veri_modules_index.tree(module), names):
            found[(f"{module}.py", name)] = found.get((f"{module}.py", name), []) + [line]

    assert {key: lines for key, lines in found.items() if key not in EXEMPT} == {}
    assert set(EXEMPT) == set(found), "an exemption names a site that no longer writes a literal default"
    assert all(EXEMPT.values())


@pytest.mark.tree_audit("skills/tdd/scripts/veri")
def test_every_exempt_name_is_one_tunables_does_not_define(veri_modules_index):
    from veri import tunables

    assert {name for _, name in EXEMPT} & set(tunables.TUNABLES) == set()
