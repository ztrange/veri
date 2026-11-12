"""Small cases for veri.role_growth: role-growth.sh, run in-process."""
import importlib


def test_no_argument_prints_usage_naming_role_growth_and_exits_2(run_cli):
    role_growth = importlib.import_module("veri.role_growth")

    code, _, err = run_cli(role_growth, [])

    assert (code, "role-growth.sh" in err) == (2, True)
