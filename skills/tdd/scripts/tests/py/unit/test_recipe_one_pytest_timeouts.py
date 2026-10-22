"""Guard for test_recipe_one_pytest_process.py: each case's time limit covers the make runs it starts."""
import ast
from pathlib import Path

SUBJECT = Path(__file__).resolve().parents[1] / "test_recipe_one_pytest_process.py"
DEFAULT_TIMEOUT = 30
SECONDS_PER_MAKE = 60


def starts_make(call):
    if isinstance(call.func, ast.Name):
        return call.func.id == "make"
    first = call.args[0] if call.args else None
    return (isinstance(call.func, ast.Attribute) and call.func.attr == "run" and isinstance(first, ast.List)
            and bool(first.elts) and isinstance(first.elts[0], ast.Constant) and first.elts[0].value == "make")


def make_calls(node, times=1):
    total = 0
    for child in ast.iter_child_nodes(node):
        inner = times
        if isinstance(child, ast.For) and isinstance(child.iter, (ast.Tuple, ast.List)):
            inner = times * len(child.iter.elts)
        if isinstance(child, ast.Call) and starts_make(child):
            total += times
        total += make_calls(child, inner)
    return total


def timeout_of(case):
    for deco in case.decorator_list:
        if isinstance(deco, ast.Call) and ast.unparse(deco.func) == "pytest.mark.timeout":
            return ast.literal_eval(deco.args[0])
    return DEFAULT_TIMEOUT


def test_every_recipe_one_case_that_starts_make_has_a_timeout_of_60_seconds_per_make_call_2154():
    cases = [n for n in ast.parse(SUBJECT.read_text()).body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    short = [(c.name, timeout_of(c), make_calls(c)) for c in cases
             if make_calls(c) and timeout_of(c) < SECONDS_PER_MAKE * make_calls(c)]
    assert not short, "timeout below %d s per make call (case, timeout, makes): %s" % (SECONDS_PER_MAKE, short)
