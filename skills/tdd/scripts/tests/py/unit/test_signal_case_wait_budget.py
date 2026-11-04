"""The signal case's worst-case leaf waits fit inside its own timeout mark (#2940)."""
import ast
from pathlib import Path

import leaf_waits

SUITE = Path(__file__).resolve().parents[1] / "test_supervise.py"
CASE = (
    "test_cli_on_term_int_or_hup_writes_2_exits_2_and_leaves_no_leaf_while_an_ignored_int_"
    "lets_the_leaf_finish_with_its_own_0_and_wait_leaf_against_a_live_supervisor_exits_3_silently"
)


def case_timeout():
    for node in ast.parse(SUITE.read_text()).body:
        if isinstance(node, ast.FunctionDef) and node.name == CASE:
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and ast.unparse(dec.func) == "pytest.mark.timeout":
                    return ast.literal_eval(dec.args[0])
    raise AssertionError("the signal case carries no timeout mark")


def test_2940_the_death_bound_exceeds_30_s_and_the_signal_cases_worst_case_waits_fit_its_timeout():
    worst = 3 * leaf_waits.LEAF_DEATH_BOUND + 5 * leaf_waits.LEAF_START_BOUND
    assert (leaf_waits.LEAF_DEATH_BOUND > 30.0, worst < case_timeout()) == (True, True)
