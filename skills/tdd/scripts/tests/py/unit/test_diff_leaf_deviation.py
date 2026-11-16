"""In-process cases for veri/diff_leaf_deviation.py, the module diff-leaf-deviation.sh is a shim over."""
import importlib


def test_issue_3351_no_argument_prints_usage_on_stderr_and_exits_2(run_cli):
    diff_leaf_deviation = importlib.import_module("veri.diff_leaf_deviation")

    code, out, err = run_cli(diff_leaf_deviation, [])

    assert (code, out, err) == (2, "", "usage: diff-leaf-deviation.sh <leaf> <step-base-sha> <ledger>\n")


def test_issue_3351_four_arguments_print_usage_on_stderr_and_exit_2(run_cli):
    diff_leaf_deviation = importlib.import_module("veri.diff_leaf_deviation")

    code, out, err = run_cli(diff_leaf_deviation, ["develop-diff", "abc1234", ".tdd/issue-42.md", "extra"])

    assert (code, out, err) == (2, "", "usage: diff-leaf-deviation.sh <leaf> <step-base-sha> <ledger>\n")


def test_a_failing_git_call_prints_diff_leaf_deviation_git_args_failed_and_its_stderr_and_exits_2_4043(
        run_cli, fake_processes, tmp_path):
    diff_leaf_deviation = importlib.import_module("veri.diff_leaf_deviation")
    fake_processes.answers({"git rev-list": (128, "", "fatal: bad revision 'abc1234..HEAD'\n")})

    code, out, err = run_cli(diff_leaf_deviation, ["develop-diff", "abc1234", ".tdd/issue-42.md"], cwd=tmp_path)

    assert (code, out, err) == (
        2, "", "diff-leaf-deviation.sh: git rev-list --count abc1234..HEAD failed: fatal: bad revision 'abc1234..HEAD'\n")
