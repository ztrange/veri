"""In-process cases for veri/diff_leaf_deviation.py, the module diff-leaf-deviation.sh is a shim over."""
import importlib


def test_issue_3351_no_argument_prints_usage_on_stderr_and_exits_2(run_cli):
    diff_leaf_deviation = importlib.import_module("veri.diff_leaf_deviation")

    code, out, err = run_cli(diff_leaf_deviation, [])

    assert (code, out, err) == (2, "", "usage: diff-leaf-deviation.sh <leaf> <step-base-sha> <ledger>\n")
