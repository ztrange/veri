"""Each develop-leaf report reader's keys, as it names them in its calls to report.py, are declared by a
REPORT-FORMAT line of the prompts whose report it reads (#3944, PRD 017.2 R21).

A key is read off the reader's source: the key argument of every `report_values` / `report_read` call,
followed through constants, the reader's own functions' parameters and loop variables. A key the case
cannot follow fails it, so a reader that computes its keys must be made followable or listed here.
`suite_reported` is not listed: the keys it reads beyond `SUITE:` come from the declarations themselves.
`same_reject` and `parse_adjudication` read verifier and adjudicator reports, which declare no format.
"""
import ast
import importlib
import re

from conftest import SCRIPTS

PROMPTS = SCRIPTS / "prompts"
VERI = SCRIPTS / "veri"

# reader module -> the prompts whose report it reads (a spliced partial counts as its prompt's).
READERS = {
    "candidates": ("develop-refactor",),
    "comment": ("develop-red", "develop-green", "develop-refactor"),
    "cover_outcome": ("develop-cover",),
    "coverage_blocker": ("develop-cover",),
    "exhausted_outcome": ("develop-exhausted", "develop-over-budget"),
    "pin_target": ("develop-red", "develop-red-missing"),
    "quality_findings": ("develop-test-quality",),
    "red_divergence": ("develop-red", "develop-revise"),
    "red_setup": ("develop-red", "develop-revise"),
    "refactor_owed": ("develop-refactor", "develop-cover"),
    "seam_outcome": ("develop-seam",),
    "structural_predicate": ("develop-predicate",),
    "tidy_first": ("develop-green",),
    "unreplaced_cases": ("develop-red", "develop-replaces-report"),
    "wrong_test_route": ("develop-green", "develop-revise", "_develop-wrong-test-format"),
}

# (reader, key) read only off a verifier's report, which declares no REPORT-FORMAT.
VERIFIER_KEYS = {
    ("wrong_test_route", "LATER_STEP"): "verify-green's REJECT names the later step",
}

# (reader, key) gaps this case found when it landed, each owed in graded prose (no Requirements row
# covered the edit); an entry fails the case once its gap is fixed, so it is removed with the fix.
OWED = {
    # Asked in develop-revise.md's step 4, above `### Report`; declaring it on `revise` would make it required
    # for that format's suite exemption (suite_reported.py:57-58), and no revise-<phase>.md prompt is read today.
    ("wrong_test_route", "MISSING_TEST"):
        "develop-revise.md asks for MISSING_TEST: on OUTCOME: IMPOSSIBLE; its REPORT-FORMAT revise omits it",
}

CALLS = ("report_values", "report_read")


class Unfollowed(Exception):
    pass


def _expand(text):
    return re.sub(r"\{\{INCLUDE:([^}]*)\}\}", lambda m: _expand((PROMPTS / m[1]).read_text()), text)


def declared_keys(prompt):
    report_formats = importlib.import_module("veri.report_formats")
    return {key.removesuffix(":") for f in report_formats.parse(_expand((PROMPTS / f"{prompt}.md").read_text()))
            for key in f["keys"]}


def _name(func):
    return func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else None


def _argument(call, index, keyword):
    for kw in call.keywords:
        if kw.arg == keyword:
            return kw.value
    if index < len(call.args) and not any(isinstance(a, ast.Starred) for a in call.args[:index + 1]):
        return call.args[index]
    return None


class Reader:
    def __init__(self, module):
        self.module = module
        self.tree = ast.parse((VERI / f"{module}.py").read_text())
        self.parents = {child: node for node in ast.walk(self.tree) for child in ast.iter_child_nodes(node)}

    def keys(self):
        keys = set()
        for call in ast.walk(self.tree):
            if isinstance(call, ast.Call) and _name(call.func) in CALLS:
                key = _argument(call, 1, "key" if _name(call.func) == "report_values" else "keys")
                if key is None:
                    raise Unfollowed(f"{self.module}:{call.lineno}: no key argument")
                keys |= self.resolve(key)
        return keys

    def _scopes(self, node):
        while node in self.parents:
            node = self.parents[node]
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ListComp, ast.SetComp,
                                 ast.DictComp, ast.GeneratorExp, ast.Module)):
                yield node

    def _binding(self, name, at):
        for scope in self._scopes(at):
            if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                params = scope.args.posonlyargs + scope.args.args
                for i, arg in enumerate(params):
                    if arg.arg == name:
                        return self._parameter(scope, i, name)
            if isinstance(scope, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                for gen in scope.generators:
                    if isinstance(gen.target, ast.Name) and gen.target.id == name:
                        return self.resolve(gen.iter)
            body = getattr(scope, "body", None)
            body = body if isinstance(body, list) else []
            nodes = body if isinstance(scope, ast.Module) else (n for stmt in body for n in ast.walk(stmt))
            for node in nodes:
                if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                    return self.resolve(node.value)
                if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and node.target.id == name:
                    return self.resolve(node.iter)
        raise Unfollowed(f"{self.module}:{at.lineno}: {name} is bound nowhere this case follows")

    def _parameter(self, func, index, name):
        if isinstance(func, ast.Lambda):
            raise Unfollowed(f"{self.module}:{func.lineno}: a lambda's parameter {name}")
        values = set()
        defaults = dict(zip([a.arg for a in func.args.args][::-1], func.args.defaults[::-1], strict=False))
        if name in defaults:
            values |= self.resolve(defaults[name])
        calls = [c for c in ast.walk(self.tree) if isinstance(c, ast.Call) and _name(c.func) == func.name]
        if not calls:
            raise Unfollowed(f"{self.module}:{func.lineno}: {func.name} is never called here")
        for call in calls:
            arg = _argument(call, index, name)
            if arg is not None:
                values |= self.resolve(arg)
        return values

    def resolve(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return {node.value}
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            return set().union(*(self.resolve(e) for e in node.elts))
        if isinstance(node, ast.Starred):
            return self.resolve(node.value)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return self.resolve(node.left) | self.resolve(node.right)
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice):
            bounds = [ast.literal_eval(b) if b is not None else None
                      for b in (node.slice.lower, node.slice.upper, node.slice.step)]
            return {value[slice(*bounds)] for value in self.resolve(node.value)}
        if isinstance(node, ast.Name):
            return self._binding(node.id, node)
        raise Unfollowed(f"{self.module}:{node.lineno}: {ast.unparse(node)} is not a key this case can follow")


def undeclared():
    """(reader, key, prompts) for each key a reader reads that no declaration of its prompts holds."""
    found = []
    for module, prompts in READERS.items():
        declared = set().union(*(declared_keys(p) for p in prompts))
        for key in sorted(Reader(module).keys()):
            if key not in declared and (module, key) not in VERIFIER_KEYS:
                found.append((module, key, prompts))
    return found


def test_every_key_a_develop_leaf_reader_reads_is_declared_by_a_report_format_of_the_prompts_whose_report_it_reads_3944():
    gaps = [(m, k, p) for m, k, p in undeclared() if (m, k) not in OWED]
    stale = [entry for entry in OWED if entry not in {(m, k) for m, k, _ in undeclared()}]

    assert not gaps, "\n".join(f"{m} reads {k}:, declared by no REPORT-FORMAT line of {', '.join(p)}"
                               for m, k, p in gaps)
    assert not stale, f"no longer a gap, so drop it from OWED: {stale}"
