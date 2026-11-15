import ast

import pytest

# tree_audit cases that glob the test files but may not go through tests_py_index, each with why.
EXEMPT = {
    "test_fast_tier_guard.py::test_1641_a_real_exemption_keyed_relative_to_tests_py_is_not_reported_stale_by_any_case_that_reads_the_real_table":
        "lists file paths for the fast-tier placement audit, which never parses them; veri.fast_tier_guard reads each file itself",
    "test_fast_tier_guard.py::test_every_guard_clean_pytest_file_lives_under_tests_py_unit_and_every_file_the_guard_names_stays_outside_it":
        "lists file paths for the fast-tier placement audit, which never parses them; veri.fast_tier_guard reads each file itself",
}

# tree_audit cases that glob `*.py` under veri/ without veri_modules_index, each with why.
STAGES_A_COPY = "copies veri/*.py byte for byte into a staged scripts tree to run build_develop_prompt from there; it parses nothing"
VERI_EXEMPT = {
    "test_stale_bytecode_process.py::test_every_directly_runnable_module_keeps_its_bytecode_out_of_the_tree_2405":
        "globs a copy of veri/ made in tmp_path and runs each module as a process; the real tree is only copied",
    "test_module_importers.py::test_every_module_has_an_importer_besides_its_own_suite_or_is_kept":
        "greps the lines of veri/, the tests/py helpers, the shims and the Makefile alike as raw text for import-like mentions",
    "test_module_importers.py::test_the_scan_names_a_planted_helper_and_a_planted_module_and_passes_without_them":
        "greps the lines of veri/, the tests/py helpers, the shims and the Makefile alike as raw text for import-like mentions",
    "test_veri_modules_index.py::test_the_index_names_every_python_module_of_veri_by_its_stem":
        "pins the index against an independent glob of veri/",
}
VERI_EXEMPT.update({
    "test_build_develop_prompt.py::test_main_refuses_the_first_unreadable_file_in_the_bash_order_with_no_usage_line_and_reads_only_the_files_the_phase_spec_and_step_select": STAGES_A_COPY,
    "test_build_develop_prompt.py::test_main_renders_a_red_prompt_with_each_file_stripped_of_trailing_newlines_the_timed_test_run_path_as_reached_and_non_utf8_bytes_passed_through": STAGES_A_COPY,
    "test_build_develop_prompt.py::test_main_drops_nul_bytes_from_the_template_the_shared_rules_and_the_spec_it_renders": STAGES_A_COPY,
    "test_build_develop_prompt.py::test_main_resolves_includes_in_the_template_the_shared_rules_and_the_green_paragraphs_before_substituting_and_leaves_them_literal_in_the_spec_step_reason_and_bug_paragraph": STAGES_A_COPY,
    "test_build_develop_prompt.py::test_main_substitutes_every_placeholder_sequentially_globally_and_literally_in_the_bash_order_for_every_phase": STAGES_A_COPY,
    "test_build_develop_prompt.py::test_main_reads_veri_refactor_budget_for_the_refactor_phase_only_rendering_5_when_unset_or_empty_and_any_other_value_verbatim": STAGES_A_COPY,
    "test_build_develop_prompt.py::test_main_answers_what_the_bash_contract_cases_before_the_out_of_scope_class_asserted": STAGES_A_COPY,
    "test_build_develop_prompt.py::test_main_answers_what_the_bash_contract_cases_from_the_out_of_scope_class_to_the_over_budget_reason_asserted": STAGES_A_COPY,
    "test_build_develop_prompt.py::test_main_answers_what_the_bash_contract_cases_from_the_rebase_prompt_to_the_end_asserted": STAGES_A_COPY,
    "test_build_develop_prompt.py::test_main_renders_every_phase_other_than_over_budget_without_reading_the_over_budget_template_1468": STAGES_A_COPY,
    "test_build_develop_prompt.py::test_main_renders_revise_green_for_an_unmarked_step_as_the_builder_without_the_replaces_case_paragraph_does_1468": STAGES_A_COPY,
})

# tree_audit cases taking tests_py_index that may still read an entry's tree or call ast.walk, each with why.
WALKING_EXEMPT = {
    "test_tree_index_guard.py::test_every_tree_audit_case_sweeping_all_test_files_uses_the_shared_index_2168":
        "this guard: it reads decorators, fixtures and calls, which the index's definitions do not carry",
    "test_readers_tree_index.py::test_two_readers_audits_in_one_session_walk_each_test_file_once_2170":
        "reads each entry's tree only to key its spy on ast.walk by node, counting the audits' walks",
    "test_readers_tree_index.py::test_phased_and_refactor_loop_audits_in_one_session_walk_each_test_file_once_2170":
        "reads each entry's tree only to key its spy on ast.walk by node, counting the audits' walks",
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


def _reaches(fn, functions, found):
    """Whether `found` holds of a node in `fn` or in a module-level function it reaches."""
    seen = {fn.name}

    def reaches(current):
        for node in ast.walk(current):
            if found(node):
                return True
            if isinstance(node, ast.Name) and node.id in functions and node.id not in seen:
                seen.add(node.id)
                if reaches(functions[node.id]):
                    return True
        return False

    return reaches(fn)


def _tree_audits(functions, taking_index):
    return [fn for fn in functions.values()
            if any(_is_tree_audit(d) for d in fn.decorator_list)
            and ("tests_py_index" in [a.arg for a in fn.args.args]) == taking_index]


def sweepers(tree):
    """The tree_audit cases that glob the test files, in their own body or a module-level function they reach,
    without taking the tests_py_index fixture."""
    strings = _module_strings(tree)
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    return [fn.name for fn in _tree_audits(functions, False)
            if _reaches(fn, functions, lambda node: _globs_test_files(node, strings))]


def _globs_python_files(node):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr in ("glob", "rglob") and bool(node.args)
            and isinstance(node.args[0], ast.Constant) and node.args[0].value == "*.py")


def _names_veri(node):
    """The directory `veri`: the string "veri" (`SCRIPTS / "veri"`) or a name spelt veri/VERI."""
    return ((isinstance(node, ast.Constant) and node.value == "veri")
            or (isinstance(node, ast.Name) and node.id.lower() == "veri"))


def veri_sweepers(tree):
    """The tree_audit cases that glob `*.py` and name veri, in their own body or a module-level function they reach:
    a sweep of veri/ that reads and parses the modules itself instead of asking veri_modules_index."""
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    return [fn.name for fn in functions.values()
            if any(_is_tree_audit(d) for d in fn.decorator_list)
            and _reaches(fn, functions, _globs_python_files) and _reaches(fn, functions, _names_veri)]


def _walks_an_entrys_tree(node):
    """Any `ast.walk(...)` call, and any read of a `.tree` attribute: an audit doing `tree = entry.tree` and then
    walking `tree.body` node by node is as much its own walk as `ast.walk(entry.tree)`."""
    if isinstance(node, ast.Attribute) and node.attr == "tree":
        return True
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "walk"
            and isinstance(node.func.value, ast.Name) and node.func.value.id == "ast")


def walkers(tree):
    """The tree_audit cases taking tests_py_index that call ast.walk or read a `.tree`, in their own body or a
    module-level function they reach."""
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    return [fn.name for fn in _tree_audits(functions, True)
            if _reaches(fn, functions, _walks_an_entrys_tree)]


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_tree_audit_case_sweeping_all_test_files_uses_the_shared_index_2168(tests_py_index):
    found = [f"{entry.path.name}::{name}" for entry in tests_py_index if entry.path.name != "conftest.py"
             for name in sweepers(entry.tree)]
    walking = [f"{entry.path.name}::{name}" for entry in tests_py_index if entry.path.name != "conftest.py"
               for name in walkers(entry.tree)]
    own_walks = [case for case in walking if case not in WALKING_EXEMPT]
    stale_walks = [case for case in WALKING_EXEMPT if case not in walking]
    assert (own_walks, stale_walks) == ([], []), (
        "tree_audit cases walk an entry's tree instead of querying the index:\n" + "\n".join(own_walks)
        + "\nwalking exemptions naming no such case:\n" + "\n".join(stale_walks))
    veri_found = [f"{entry.path.name}::{name}" for entry in tests_py_index if entry.path.name != "conftest.py"
                  for name in veri_sweepers(entry.tree)]
    own_sweeps = [case for case in veri_found if case not in VERI_EXEMPT]
    stale_sweeps = [case for case in VERI_EXEMPT if case not in veri_found]
    assert (own_sweeps, stale_sweeps) == ([], []), (
        "tree_audit cases glob veri/*.py instead of querying veri_modules_index:\n" + "\n".join(own_sweeps)
        + "\nveri sweep exemptions naming no such case:\n" + "\n".join(stale_sweeps))
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


@pytest.mark.parametrize("source", [
    'import pytest\n\n@pytest.mark.tree_audit("x")\ndef test_planted():\n'
    '    return sorted((SCRIPTS / "veri").glob("*.py"))\n',
    'import pytest\nVERI = P / "veri"\n\n@pytest.mark.tree_audit("x")\ndef test_planted():\n'
    '    return sorted(VERI.glob("*.py"))\n',
    'import pytest\n\ndef _files(package):\n    return package.glob("*.py")\n\n'
    '@pytest.mark.tree_audit("x")\ndef test_planted():\n    return _files(ROOT / "skills" / "veri")\n',
    'import pytest\n\n@pytest.mark.tree_audit("x")\ndef test_planted():\n'
    '    return (SCRIPTS / "veri").rglob("*.py")\n',
], ids=["inline-path", "module-constant", "through-a-helper-argument", "rglob"])
def test_the_guard_names_a_planted_case_globbing_veri_without_the_modules_index(source):
    assert veri_sweepers(ast.parse(source)) == ["test_planted"]


@pytest.mark.parametrize("source", [
    'import pytest\n\n@pytest.mark.tree_audit("x")\ndef test_planted(veri_modules_index):\n'
    '    return veri_modules_index.names\n',
    'import pytest\n\n@pytest.mark.tree_audit("x")\ndef test_planted():\n'
    '    return sorted(SCRIPTS.glob("*.sh"))\n',
    'import pytest\n\n@pytest.mark.tree_audit("x")\ndef test_planted():\n'
    '    return sorted((SCRIPTS / "prompts").glob("*.md"))\n',
    'import pytest\n\ndef test_planted():\n    return sorted((SCRIPTS / "veri").glob("*.py"))\n',
], ids=["the-index", "shim-glob", "prompt-glob", "not-a-tree-audit"])
def test_the_guard_leaves_alone_a_case_that_reads_through_the_index_or_globs_something_else(source):
    assert veri_sweepers(ast.parse(source)) == []
