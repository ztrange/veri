"""The one reader of VERI_* tunables: no other module under veri/ reads one from the environment."""
import ast
import pathlib

VERI = pathlib.Path(__file__).resolve().parents[2] / "veri"

READS_DIRECTLY = frozenset((
    "add_ledger_step", "build_develop_prompt", "detach_command", "event", "github", "launch_floor", "leaf_model",
    "leaf_timeout", "parallel_conductors", "profile", "run_conductor", "run_leaf", "run_suite", "run_verdict",
    "skill_drift", "solvable_issues", "status", "step_budget", "stop_run", "supervise", "time_budget", "verify",
    "wait_ci", "wait_leaf", "workqueue",
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
