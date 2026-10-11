"""The one reader of VERI_* tunables: no other module under veri/ reads one from the environment."""
import ast
import pathlib

VERI = pathlib.Path(__file__).resolve().parents[2] / "veri"

READS_DIRECTLY = frozenset((
    "event", "github", "launch_floor", "run_leaf", "run_suite", "run_verdict", "skill_drift", "solvable_issues",
    "stop_run",
))


def direct_reads(path):
    source = path.read_text()
    lines = source.splitlines()
    return ["%s:%d" % (path, node.lineno) for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "os"
            and node.attr in ("environ", "environb", "getenv") and "VERI_" in lines[node.lineno - 1]]


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


def test_github_solvable_issues_skill_drift_launch_floor_run_suite_and_event_take_their_veri_values_from_the_one_reader():
    names = ("github", "solvable_issues", "skill_drift", "launch_floor", "run_suite", "event")
    modules = [VERI / ("%s.py" % name) for name in names]

    assert [read for path in modules for read in direct_reads(path)] == []
