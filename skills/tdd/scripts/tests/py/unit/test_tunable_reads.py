"""The one reader of VERI_* tunables: no other module under veri/ reads one from the environment."""
import ast
import pathlib
import pytest

VERI = pathlib.Path(__file__).resolve().parents[3] / "veri"

READS_DIRECTLY = frozenset((
    "github", "launch_floor", "run_verdict", "skill_drift", "solvable_issues", "stop_run",
))


def direct_reads(path):
    source = path.read_text()
    lines = source.splitlines()
    tree = ast.parse(source)
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}

    def keyed_by_a_variable(node):
        parent = parents.get(node)
        if isinstance(parent, ast.Call):
            return node is parent.func and bool(parent.args) and not isinstance(parent.args[0], ast.Constant)
        if isinstance(parent, ast.Attribute) and isinstance(parents.get(parent), ast.Call):
            args = parents[parent].args
            return parent.attr in ("get", "pop", "setdefault") and bool(args) and not isinstance(args[0], ast.Constant)
        if isinstance(parent, ast.Subscript):
            return not isinstance(parent.slice, ast.Constant)
        if isinstance(parent, ast.Compare):
            return parent.comparators[0] is node and not isinstance(parent.left, ast.Constant)
        return False

    veri_names = {node.targets[0].id for node in ast.walk(tree)
                  if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                  and isinstance(node.value, ast.Constant) and str(node.value.value).startswith("VERI_")}

    def copy_read_by_name_later(node):
        spread = False
        parent = parents.get(node)
        if isinstance(parent, ast.Attribute) and parent.attr == "copy":
            parent = parents.get(parent)
        elif isinstance(parent, ast.Dict):
            if len(parent.keys) != 1:
                return False
            parent = parents.get(parent)
            spread = True
        elif not (isinstance(parent, ast.Assign)
                  or (isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name) and parent.func.id == "dict")):
            return False
        assign = parent if isinstance(parent, ast.Assign) else parents.get(parent)
        if not (isinstance(assign, ast.Assign) and isinstance(assign.targets[0], ast.Name)):
            return False
        copy = assign.targets[0].id
        def discarded_pop(use):
            parent = parents.get(use)
            if isinstance(parent, ast.Subscript):
                return not isinstance(parent.ctx, ast.Load)
            call = parents.get(parent)
            return isinstance(call, ast.Call) and isinstance(parents.get(call), ast.Expr)

        def keyed_by_a_veri_name(use):
            parent = parents.get(use)
            if isinstance(parent, ast.Attribute):
                parent = parents.get(parent)
                key = parent.args[0] if isinstance(parent, ast.Call) and parent.args else None
            else:
                key = parent.slice if isinstance(parent, ast.Subscript) else None
            if isinstance(key, ast.Name):
                return key.id in veri_names
            return isinstance(key, ast.Constant) and str(key.value).startswith("VERI_")

        return any(isinstance(use, ast.Name) and use.id == copy and use.lineno > assign.lineno
                   and not discarded_pop(use)
                   and (keyed_by_a_veri_name(use) if spread else
                        "VERI_" in lines[use.lineno - 1] or keyed_by_a_veri_name(use)) for use in ast.walk(tree))

    def passed_as_an_argument(node):
        call = parents.get(node)
        if not (isinstance(call, ast.Call) and node in call.args
                and not (isinstance(call.func, ast.Name) and call.func.id == "dict")):
            return False
        local = [fn for fn in ast.walk(tree) if isinstance(fn, ast.FunctionDef)
                 and isinstance(call.func, ast.Name) and fn.name == call.func.id]
        return any("VERI_" in "\n".join(lines[fn.lineno - 1:fn.end_lineno]) for fn in local)

    imported = {alias.asname or alias.name for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module == "os"
                for alias in node.names if alias.name in ("environ", "environb", "getenv", "*")}
    if "*" in imported:
        imported |= {"environ", "environb", "getenv"}

    os_names = {"os"} | {alias.asname for node in ast.walk(tree) if isinstance(node, ast.Import)
                         for alias in node.names if alias.name == "os" and alias.asname}

    def is_environment(node):
        if isinstance(node, ast.Name):
            return node.id in imported
        return (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in os_names
                and node.attr in ("environ", "environb", "getenv"))

    def tunables_environment(node):
        return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "environment"
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "tunables")

    return ["%s:%d" % (path, node.lineno) for node in ast.walk(tree)
            if tunables_environment(node) and copy_read_by_name_later(node)] + \
           ["%s:%d" % (path, node.lineno) for node in ast.walk(tree)
            if is_environment(node)
            and ("VERI_" in lines[node.lineno - 1] or keyed_by_a_variable(node) or copy_read_by_name_later(node)
                 or passed_as_an_argument(node))]


@pytest.mark.tree_audit("every module under veri/")
def test_no_module_but_the_reader_and_the_exempt_ones_reads_a_veri_name_from_the_environment():
    modules = sorted(path for path in VERI.glob("*.py") if path.stem not in ("tunables", *READS_DIRECTLY))

    assert [read for path in modules for read in direct_reads(path)] == []


def test_supervise_verify_wait_leaf_wait_ci_and_detach_command_take_their_veri_values_from_the_one_reader():
    modules = [VERI / ("%s.py" % name) for name in ("supervise", "verify", "wait_leaf", "wait_ci", "detach_command")]

    assert [read for path in modules for read in direct_reads(path)] == []


def test_leaf_timeout_leaf_model_build_develop_prompt_add_ledger_step_step_budget_and_time_budget_take_their_veri_values_from_the_one_reader():
    names = ("leaf_timeout", "leaf_model", "build_develop_prompt", "add_ledger_step", "step_budget", "time_budget")
    modules = [VERI / ("%s.py" % name) for name in names]

    assert [read for path in modules for read in direct_reads(path)] == []


def test_parallel_conductors_orchestrate_run_conductor_workqueue_profile_and_status_take_their_veri_values_from_the_one_reader():
    names = ("parallel_conductors", "orchestrate", "run_conductor", "workqueue", "profile", "status")
    modules = [VERI / ("%s.py" % name) for name in names]

    assert [read for path in modules for read in direct_reads(path)] == []


def test_github_solvable_issues_skill_drift_launch_floor_and_event_take_their_veri_values_from_the_one_reader():
    names = ("github", "solvable_issues", "skill_drift", "launch_floor", "event")
    modules = [VERI / ("%s.py" % name) for name in names]

    assert [read for path in modules for read in direct_reads(path)] == []


@pytest.mark.tree_audit("every module under veri/")
def test_run_leaf_run_verdict_and_stop_run_take_their_veri_values_from_the_one_reader_and_no_module_is_exempt():
    modules = sorted(path for path in VERI.glob("*.py") if path.stem != "tunables")

    assert [read for path in modules for read in direct_reads(path)] == []


def test_stop_reason_takes_its_veri_values_from_the_one_reader():
    assert direct_reads(VERI / "stop_reason.py") == []


def test_merge_lock_takes_its_veri_values_from_the_one_reader():
    assert direct_reads(VERI / "merge_lock.py") == []


def test_the_guard_names_the_line_of_a_planted_read_whose_veri_name_is_held_in_a_variable(tmp_path):
    planted = tmp_path / "planted.py"
    planted.write_text('import os\nname = "VERI_X"\nvalue = os.environ.get(name)\n')

    assert direct_reads(planted) == ["%s:3" % planted]


def test_the_guard_names_the_line_of_a_planted_dict_copy_of_the_environment_read_with_a_veri_name_later(tmp_path):
    planted = tmp_path / "planted.py"
    planted.write_text('import os\nenv = dict(os.environ)\nvalue = env.get("VERI_X")\n')

    assert direct_reads(planted) == ["%s:2" % planted]


def test_the_guard_names_the_line_of_a_planted_environment_passed_as_an_argument_when_a_veri_name_is_then_read_from_it(tmp_path):
    planted = tmp_path / "planted.py"
    planted.write_text('import os\ndef context(env):\n    return env.get("VERI_X")\nvalue = context(os.environ)\n')

    assert direct_reads(planted) == ["%s:4" % planted]


def test_the_guard_names_the_line_of_a_planted_veri_read_through_a_bare_environ_imported_from_os(tmp_path):
    planted = tmp_path / "planted.py"
    planted.write_text('from os import environ\nvalue = environ.get("VERI_X")\n')

    assert direct_reads(planted) == ["%s:2" % planted]


def test_grade_prose_takes_its_veri_values_from_the_one_reader_2062():
    assert direct_reads(VERI / "grade_prose.py") == []


def test_next_unchecked_takes_its_veri_values_from_the_one_reader_2368():
    assert direct_reads(VERI / "next_unchecked.py") == []


def test_queued_merge_takes_its_veri_values_from_the_one_reader_2585():
    assert direct_reads(VERI / "queued_merge.py") == []


def test_mutation_probe_takes_its_veri_values_from_the_one_reader_2506():
    assert direct_reads(VERI / "mutation_probe.py") == []
