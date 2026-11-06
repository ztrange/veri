"""In-process cases for veri/plan_reverify.py, the module plan-reverify.sh is a shim over."""
import importlib


def test_main_called_with_no_argument_exits_2_printing_the_usage_line_on_stderr(run_cli):
    plan_reverify = importlib.import_module("veri.plan_reverify")

    code, out, err = run_cli(plan_reverify, [])

    assert (code, out, err) == (2, "", "usage: plan-reverify.sh <ledger-file>\n")


def test_main_exits_0_when_the_events_file_beside_the_ledger_is_absent(run_cli, tmp_path):
    plan_reverify = importlib.import_module("veri.plan_reverify")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] 1. a step\n")

    code, out, err = run_cli(plan_reverify, [str(ledger)])

    assert code == 0
