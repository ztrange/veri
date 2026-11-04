"""In-process cases for veri/suite_flakes.py, the module suite-flakes.sh is a shim over."""
import importlib


def test_2957_suite_flakes_with_no_argument_prints_a_usage_line_naming_the_script_and_exits_2(run_cli):
    suite_flakes = importlib.import_module("veri.suite_flakes")

    code, out, err = run_cli(suite_flakes, [])

    assert (code, out, "suite-flakes.sh" in err) == (2, "", True)
