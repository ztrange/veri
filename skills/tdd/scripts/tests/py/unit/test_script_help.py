"""In-process cases for veri/script_help.py, the module script-help.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def script_help():
    return importlib.import_module("veri.script_help")


def test_main_with_no_argument_exits_2_printing_the_usage_line_script_help_sh(run_cli, script_help):
    code, out, err = run_cli(script_help, [])

    assert (code, out, err) == (2, "", "usage: script-help.sh <name>\n")


def test_main_with_a_name_that_has_no_entry_in_scripts_md_exits_3_printing_nothing_on_stdout(run_cli, script_help):
    code, out, err = run_cli(script_help, ["no-such-script.sh"])

    assert (code, out) == (3, "")
