"""Cases for when skills/tdd/SKILL.md has the conductor tick an issue criterion and how its step 2 plans the off-cycle step kinds."""
import ast
import pathlib


def test_2468_every_non_test_function_defined_in_this_file_is_called_at_least_once_in_it():
    tree = ast.parse(pathlib.Path(__file__).read_text())
    defined = [n.name for n in tree.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("test_")]
    called = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    orphans = [name for name in defined if name not in called]
    assert not orphans, "never called in this file: " + ", ".join(orphans)
