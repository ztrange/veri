import ast

import pytest

# tree_audit cases that glob the test files but may not go through tests_py_index, each with why.
EXEMPT = {
    "test_fast_tier_guard.py::test_1641_a_real_exemption_keyed_relative_to_tests_py_is_not_reported_stale_by_any_case_that_reads_the_real_table":
        "lists file paths for the fast-tier placement audit, which never parses them; veri.fast_tier_guard reads each file itself",
    "test_fast_tier_guard.py::test_every_guard_clean_pytest_file_lives_under_tests_py_unit_and_every_file_the_guard_names_stays_outside_it":
        "lists file paths for the fast-tier placement audit, which never parses them; veri.fast_tier_guard reads each file itself",
    "test_affected_suites.py::test_on_the_real_skill_md_and_suites_a_one_section_edit_selects_the_suites_reading_that_section_through_a_slicing_helper_and_every_suite_reading_skill_md_any_other_way_and_not_a_suite_slicing_only_other_sections":
        "copies the real suites into a git repo for affected-suites.sh, a process boundary that reads them itself",
}


def _is_tree_audit(decorator):
    return (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == "tree_audit")


def _module_strings(tree):
    """Module-level `NAME = "..."` constants, so `rglob(PATTERN)` reads as the literal it names."""
    strings = {}
    for node in tree.body:
        if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    strings[target.id] = node.value.value
    return strings


def _globs_test_files(node, strings):
    """A glob or rglob whose pattern's last part is `test_*.py`: `rglob("test_*.py")`, `glob("**/test_*.py")`,
    `glob("test_*.py") + glob("unit/test_*.py")`, `glob("py/unit/test_*.py")`, or any of them through a constant."""
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr in ("glob", "rglob") and node.args):
        return False
    arg = node.args[0]
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        pattern = arg.value
    elif isinstance(arg, ast.Name) and arg.id in strings:
        pattern = strings[arg.id]
    else:
        return False
    return pattern.rsplit("/", 1)[-1] == "test_*.py"


def sweepers(tree):
    """The tree_audit cases that glob the test files, in their own body or a module-level function they reach,
    without taking the tests_py_index fixture."""
    strings = _module_strings(tree)
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

    def sweeps(fn, seen):
        for node in ast.walk(fn):
            if _globs_test_files(node, strings):
                return True
            if isinstance(node, ast.Name) and node.id in functions and node.id not in seen:
                seen.add(node.id)
                if sweeps(functions[node.id], seen):
                    return True
        return False

    return [
        fn.name for fn in functions.values()
        if any(_is_tree_audit(d) for d in fn.decorator_list)
        and "tests_py_index" not in [a.arg for a in fn.args.args]
        and sweeps(fn, {fn.name})
    ]


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_tree_audit_case_sweeping_all_test_files_uses_the_shared_index_2168(tests_py_index):
    found = [f"{entry.path.name}::{name}" for entry in tests_py_index if entry.path.name != "conftest.py"
             for name in sweepers(entry.tree)]
    stray = [case for case in found if case not in EXEMPT]
    stale = [case for case in EXEMPT if case not in found]
    assert (stray, stale) == ([], []), (
        "tree_audit cases sweep every test file without the tests_py_index fixture:\n" + "\n".join(stray)
        + "\nexemptions naming no such case:\n" + "\n".join(stale))


@pytest.mark.parametrize("source", [
    'import pytest\n\n@pytest.mark.tree_audit("x")\ndef test_planted():\n'
    '    return sorted(T.glob("test_*.py")) + sorted((T / "unit").glob("test_*.py"))\n',
    'import pytest\nPAT = "test_*.py"\n\n@pytest.mark.tree_audit("x")\ndef test_planted():\n'
    '    return sorted(T.rglob(PAT))\n',
    'import pytest\n\ndef _files():\n    return T.glob("py/unit/test_*.py")\n\n'
    '@pytest.mark.tree_audit("x")\ndef test_planted():\n    return _files()\n',
], ids=["two-globs", "rglob-constant", "through-a-helper"])
def test_the_guard_names_a_planted_case_sweeping_by_each_shape_it_once_missed_2168(source):
    assert sweepers(ast.parse(source)) == ["test_planted"]
