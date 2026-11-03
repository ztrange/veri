"""Guard: skill_sections.py keeps no public helper that no other suite uses."""
import ast
import pathlib
import shutil

import pytest

PY_TESTS = pathlib.Path(__file__).resolve().parents[1]
MODULE = PY_TESTS / "skill_sections.py"
OWN_SUITE = "unit/test_skill_sections.py"


def _public_names(module):
    names = []
    for node in ast.parse(pathlib.Path(module).read_text()).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names.extend(t.id for t in targets if isinstance(t, ast.Name))
    return [n for n in names if not n.startswith("_")]


def _used_names(module, tree):
    stem = pathlib.Path(module).stem
    skip = {pathlib.Path(module).resolve(), (pathlib.Path(tree) / OWN_SUITE).resolve()}
    used = set()
    for path in sorted(pathlib.Path(tree).rglob("*.py")):
        if path.resolve() in skip:
            continue
        parsed = ast.parse(path.read_text())
        for node in ast.walk(parsed):
            if isinstance(node, ast.ImportFrom) and node.module == stem:
                used.update(alias.name for alias in node.names)
            elif isinstance(node, ast.Attribute):
                used.add(node.attr)
    return used


def unused_public_helpers(module, tree):
    used = _used_names(module, tree)
    return [name for name in _public_names(module) if name not in used]


@pytest.mark.tree_audit("every module under tests/py, for users of skill_sections helpers")
def test_skill_sections_defines_no_public_helper_that_no_other_suite_uses():
    unused = unused_public_helpers(MODULE, PY_TESTS)
    assert unused == [], f"skill_sections.py has unused public helpers: {unused}"


def test_unused_helper_check_names_a_planted_helper_and_passes_without_it(tmp_path):
    tree = tmp_path / "tree"
    tree.mkdir()
    clean = tree / "skill_sections.py"
    clean.write_text(MODULE.read_text())
    uses = ", ".join(_public_names(clean))
    (tree / "test_consumer.py").write_text(f"from skill_sections import {uses}\n")
    assert unused_public_helpers(clean, tree) == []

    planted = tmp_path / "planted"
    shutil.copytree(tree, planted)
    with (planted / "skill_sections.py").open("a") as handle:
        handle.write("\n\ndef planted_unused_helper():\n    return None\n")
    assert unused_public_helpers(planted / "skill_sections.py", planted) == ["planted_unused_helper"]
