"""The names veri/README.md lists in a `## <module>` section are the names the other modules of veri/ really use."""
import ast
import re
from collections import defaultdict

import pytest
from test_veri_interface_index import (
    _modules,
    _private,
    _readme_lines,
    _shared_modules,
    _sibling_imports,
    _users,
)

# Names a section lists that no other module of veri/ uses, each with why it stays. A ratchet: the set may shrink,
# never grow; an entry that is used by a sibling after all, or no longer listed, fails the case that checks it.
USED_ONLY_BY_TESTS = {
    "case_reader.js_title_pattern": "the public name wrong_test_route will import once its open PR lands (it reads the `_js_title_pattern` alias, KNOWN_REACHES in test_veri_interface_index.py)",
    "grade_prose.signature": "the stamp formula: the graded-signature pins and signer() call it, in the tree's own grade_prose.py",
    "issue_body.section": "the text of a body's section, the suite's way to read what spans returns; callers use spans",
    "tests_frozen.check": "typed form of the `check` subcommand; the shim's main and the suite drive it",
    "tests_frozen.record": "typed form of the `record` subcommand; the shim's main and the suite drive it",
    "tunables.TABLE": "the table the tunable audits read; code reads it through get and resolve",
    "tunables.TUNABLES": "the table the tunable audits read; code reads it through get and resolve",
    "tunables.Tunable": "the table's entry type, built by the table and read by the tunable audits",
}
MOST_ALLOWANCES = 9

_NAME = re.compile(r"[A-Za-z_]\w*(?:\(.*\))?$")
_IDENT = re.compile(r"[A-Za-z_]\w*")


def section_lines(lines, module):
    """The lines of `## <module>` up to the next heading; empty when the module has no section."""
    inside, found = False, []
    for line in lines:
        if line.startswith("#"):
            inside = line.startswith("## ") and line[3:].strip().strip("`") == module
            continue
        if inside:
            found.append(line)
    return found


def mentioned_names(lines):
    """Every name a section mentions anywhere: a backticked `name` or `name(signature)` span, even mid-sentence
    ("raises `GitFailed`")."""
    return {_IDENT.match(s).group() for line in lines for s in re.findall(r"`([^`]+)`", line) if _NAME.match(s)}


def listed_names(lines):
    """({names a section lists}, {names it opens a bullet with}): a backticked `name` or `name(signature)` span that
    is followed by `:`, `,`, `;`, `.`, `)`, ` (` or the end of its line. Dotted spans, `(a, b)` tuples and a name
    in the middle of a sentence are prose, not a listing."""
    listed, opening = set(), set()
    for line in lines:
        spans = [s for s in re.findall(r"`([^`]+)`(?=$|[:,;.)]|\s\()", line) if _NAME.match(s)]
        listed.update(_IDENT.match(s).group() for s in spans)
        if line.startswith("- ") and spans and line[2:].find("`") == line[2:].find("`" + spans[0] + "`"):
            opening.add(_IDENT.match(spans[0]).group())
    return listed, opening


def defined_names(tree):
    """Names bound at module level (def, class, assignment), also inside if/try/with blocks."""
    names, todo = set(), list(tree.body)
    while todo:
        node = todo.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                names.update(n.id for n in ast.walk(target) if isinstance(n, ast.Name))
        elif isinstance(node, (ast.If, ast.Try, ast.With)):
            todo.extend(node.body + getattr(node, "orelse", []) + getattr(node, "finalbody", []))
            todo.extend(h for handler in getattr(node, "handlers", []) for h in handler.body)
    return names


def imported_modules(tree):
    """Names a module binds with a plain `import x` / `import x as y` (anywhere in it)."""
    return {(a.asname or a.name).split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}


def _bound_here(scope):
    """Names a function (or lambda, comprehension, or the module) binds itself: parameters and stores, not those of
    functions nested in it."""
    bound, todo = set(), list(ast.iter_child_nodes(scope))
    if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        args = scope.args
        bound.update(a.arg for a in args.posonlyargs + args.args + args.kwonlyargs + [x for x in (args.vararg, args.kwarg) if x])
    while todo:
        node = todo.pop()
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            bound.add(node.id)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            todo.extend(ast.iter_child_nodes(node))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
    return bound


def _attribute_reads(tree, aliases):
    """Every `alias.attr` read where `alias` names an imported sibling at that point (not a local of the same name),
    as the Attribute node."""
    found = []

    def visit(node, shadowed):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ListComp, ast.SetComp,
                             ast.DictComp, ast.GeneratorExp)) and node is not tree:
            shadowed = shadowed | _bound_here(node) if not isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)) \
                else shadowed | {n.id for g in node.generators for n in ast.walk(g.target) if isinstance(n, ast.Name)}
        if isinstance(node, ast.Attribute):
            base = node.value
            if isinstance(base, ast.Name) and base.id in aliases and base.id not in shadowed:
                found.append(node)
            elif (isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name)
                    and base.value.id in aliases and base.value.id not in shadowed):
                found.append(node)
        for child in ast.iter_child_nodes(node):
            visit(child, shadowed)

    visit(tree, _bound_here(tree))
    return found


def uses(index):
    """({sibling: {name: {modules using it}}}, [reaches `module: sibling.<imported module>.attr`])."""
    modules = _modules(index)
    imports = {name: imported_modules(tree) for name, tree in modules.items()}
    used, reaches = defaultdict(lambda: defaultdict(set)), []
    for name, tree in {**modules, **_users(index)}.items():  # the leg in tests/leg/ uses veri/'s names (#4051)
        aliases = {}
        for target, imported, alias in _sibling_imports(tree, modules):
            if target == name:
                continue
            for x in imported or []:
                if x in imports[target]:
                    reaches.append(f"{name}: from {target} import {x}")
                elif x != "*" and not (x.startswith("__") and x.endswith("__")):
                    used[target][x].add(name)
            if alias:
                aliases[alias] = target
        for node in _attribute_reads(tree, aliases):
            base = node.value
            if isinstance(base, ast.Name):
                target = aliases[base.id]
                if node.attr in imports[target]:
                    continue
                if not (node.attr.startswith("__") and node.attr.endswith("__")):
                    used[target][node.attr].add(name)
            elif base.attr in imports[aliases[base.value.id]]:
                reaches.append(f"{name}: {base.value.id}.{base.attr}.{node.attr}")
    return used, sorted(set(reaches))


def sections(index):
    """{shared module: (names its section lists, names it opens bullets with, names it mentions at all)}."""
    lines = _readme_lines()
    return {m: (*listed_names(section_lines(lines, m)), mentioned_names(section_lines(lines, m)))
            for m in sorted(_shared_modules(index))}


def listed_calls(lines):
    """[(name, [parameter names])] for each backticked `name(parameters)` span of a section whose parentheses
    hold a plain Python parameter list (defaults, `*`, `*args` and `**kwargs` allowed)."""
    calls = []
    for line in lines:
        for span in re.findall(r"`([^`]+)`", line):
            named = re.fullmatch(r"([A-Za-z_]\w*)\((.*)\)", span)
            if not named:
                continue
            try:
                function = ast.parse(f"def {named.group(1)}({named.group(2)}): pass").body[0]
            except SyntaxError:
                continue
            calls.append((named.group(1), _parameters(function)))
    return calls


def _parameters(function):
    """The parameter names of a def, in order, bar self and cls."""
    args = function.args
    named = [a.arg for a in args.posonlyargs + args.args + args.kwonlyargs + [x for x in (args.vararg, args.kwarg) if x]]
    return [n for n in named if n not in ("self", "cls")]


def call_problems(calls, tree):
    """Why each listed call disagrees with the module `tree`: its name is bound nowhere in the module, or it is a
    function there whose parameters (bar self and cls) are not the ones listed."""
    functions = defaultdict(list)
    bound = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[node.name].append(_parameters(node))
            bound.update(a.arg for a in node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                         + [x for x in (node.args.vararg, node.args.kwarg) if x])
        elif isinstance(node, ast.ClassDef):
            bound.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            bound.add(node.id)
    problems = []
    for name, listed in calls:
        if name in functions:
            if listed not in functions[name]:
                takes = functions[name][0]
                problems.append(f"{name}({', '.join(listed)}): the function takes ({', '.join(takes)})")
        elif name not in bound:
            problems.append(f"{name}({', '.join(listed)}): bound nowhere in the module")
    return problems


# ---- the parser, on small snippets ----

def test_a_bullet_lists_its_name_with_or_without_a_signature_and_several_to_a_line():
    listed, opening = listed_names([
        "- `read_ledger(path)`, `STEP_RE`: first and second.",
        "- Reading: `items_at(rev, path)` (OSError), `body(step)` the text.",
    ])

    assert listed == {"read_ledger", "STEP_RE", "items_at"}
    assert opening == {"read_ledger", "items_at"}
    assert mentioned_names(["- Reading: `items_at(rev, path)` (OSError), `body(step)` the text."]) == {"items_at", "body"}


def test_dotted_and_tuple_spans_are_prose_not_names():
    listed, _ = listed_names(["- `f(x)`: a `(index, state)` tuple read with `ledger.STEP_RE` and `-k`."])

    assert listed == {"f"}


def test_a_section_runs_to_the_next_heading_and_a_missing_one_is_empty():
    lines = ["# G", "## a", "- `x`", "## b", "- `y`", "### c", "- `z`"]

    assert section_lines(lines, "a") == ["- `x`"]
    assert section_lines(lines, "b") == ["- `y`"]
    assert section_lines(lines, "q") == []


def test_a_name_defined_in_a_block_counts_as_defined():
    tree = ast.parse("def f(): pass\nclass C: pass\nA, B = 1, 2\nif x:\n    D = 1\ntry:\n    pass\nexcept E:\n    G = 1\n")

    assert defined_names(tree) == {"f", "C", "A", "B", "D", "G"}


def test_uses_collects_from_imports_and_attribute_reads_through_aliases_and_flags_reaches_into_a_siblings_import():
    class Fake:
        names = ("a", "b")

        def tree(self, name):
            return ast.parse({"a": "import time\nfrom os import path\ndef f(): pass\n",
                              "b": "import a as m\nfrom a import f, time\nm.g\nm.time.sleep(1)\n"}[name])

    used, reaches = uses(Fake())

    assert {k: sorted(v) for k, v in used["a"].items()} == {"f": ["b"], "g": ["b"]}
    assert reaches == ["b: from a import time", "b: m.time.sleep"]


def test_a_user_module_outside_veri_counts_as_a_user_of_a_name_but_never_as_a_module_with_names_of_its_own_4051():
    class Fake:
        names = ("a",)

        def tree(self, name):
            return ast.parse("def f(): pass\ndef g(): pass\n")

        def user_trees(self):
            return {"pytest_leg": ast.parse("import a\nfrom a import f\ndef h(): pass\n")}

    used, _ = uses(Fake())

    assert ({k: sorted(v) for k, v in used.items() if v}, {k: sorted(v) for k, v in used["a"].items()}) == (
        {"a": ["f"]}, {"f": ["pytest_leg"]})



def test_a_call_form_span_lists_its_parameters_and_prose_in_parentheses_is_not_one():
    calls = listed_calls([
        "- `read(path, default=\"\", unless_empty=None)`: x. `main_tree(cwd=None, *, missing=)`: y. `f(a, ...)`: z.",
        "- `fields()` and `(index, state)` and `ledger.step_at(a)` and `run(*args, **kwargs)`.",
    ])

    assert calls == [("read", ["path", "default", "unless_empty"]), ("fields", []), ("run", ["args", "kwargs"])]


def test_a_listed_call_must_name_the_parameters_the_function_has_and_exist_in_the_module():
    tree = ast.parse("def f(a, b=1, *, c=None): pass\nclass S:\n    def m(self, x): pass\ndef g(run): return run()\n")

    assert call_problems([("f", ["a", "b", "c"]), ("m", ["x"]), ("run", [])], tree) == []
    assert call_problems([("f", ["a", "b"])], tree) == ["f(a, b): the function takes (a, b, c)"]
    assert call_problems([("f", ["a", "b", "d"])], tree) == ["f(a, b, d): the function takes (a, b, c)"]
    assert call_problems([("gone", ["x"])], tree) == ["gone(x): bound nowhere in the module"]


# ---- the audit ----

@pytest.mark.tree_audit("every module of veri/")
def test_every_name_a_sibling_uses_is_listed_in_the_modules_section(veri_modules_index):
    used, _ = uses(veri_modules_index)
    drift = [f"{m}.{n} (used by {', '.join(sorted(users))})"
             for m, (_, _, mentioned) in sections(veri_modules_index).items()
             for n, users in sorted(used[m].items()) if n not in mentioned and not _private(n)]

    assert not drift, f"names siblings use that veri/README.md's `## <module>` section does not list: {drift}"


@pytest.mark.tree_audit("every module of veri/")
def test_every_name_a_section_lists_is_used_by_a_sibling_or_allowed(veri_modules_index):
    used, _ = uses(veri_modules_index)
    unused = []
    for module, (listed, opening, _) in sections(veri_modules_index).items():
        defined = defined_names(veri_modules_index.tree(module))
        for name in sorted(listed & defined | opening):
            if name not in used[module] and f"{module}.{name}" not in USED_ONLY_BY_TESTS:
                unused.append(f"{module}.{name}" + ("" if name in defined else " (not defined)"))

    assert not unused, f"names listed in veri/README.md that no other module of veri/ uses: {unused}"


@pytest.mark.tree_audit("every module of veri/")
def test_the_allowance_for_names_only_the_suite_uses_is_a_shrinking_ratchet(veri_modules_index):
    used, _ = uses(veri_modules_index)
    secs = sections(veri_modules_index)
    stale = []
    for key, why in USED_ONLY_BY_TESTS.items():
        module, _, name = key.partition(".")
        if not why or name in used[module] or name not in secs.get(module, (set(), set()))[0] | secs.get(module, (set(), set()))[1]:
            stale.append(key)

    assert not stale, f"allowances no longer needed (used by a sibling, unlisted, or without a reason): {stale}"
    assert len(USED_ONLY_BY_TESTS) <= MOST_ALLOWANCES


@pytest.mark.tree_audit("every module of veri/")
def test_no_module_reaches_a_module_a_sibling_imported(veri_modules_index):
    _, reaches = uses(veri_modules_index)

    assert not reaches, f"modules of veri/ reach through a sibling to a module it imports (import it yourself): {reaches}"


@pytest.mark.tree_audit("every module of veri/")
def test_every_call_a_section_lists_has_the_parameters_the_module_defines(veri_modules_index):
    drift = [f"{module}: {problem}"
             for module in sorted(_shared_modules(veri_modules_index))
             for problem in call_problems(listed_calls(section_lines(_readme_lines(), module)), veri_modules_index.tree(module))]

    assert not drift, f"calls veri/README.md's `## <module>` sections list that the module does not define so: {drift}"
