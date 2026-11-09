"""In-process cases for veri/baseline_full_tier.py, the module baseline-full-tier.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def baseline_full_tier():
    return importlib.import_module("veri.baseline_full_tier")


def test_main_called_with_no_argument_prints_the_usage_line_to_stderr_and_exits_2_3436(
        tmp_path, run_cli, baseline_full_tier):
    code, out, err = run_cli(baseline_full_tier, [], cwd=tmp_path)

    assert (code, out) == (2, "")
    assert "baseline-full-tier.sh" in err
    assert "usage" in err


def test_main_with_baseline_full_tier_unset_prints_run_and_exits_0_3436(
        tmp_path, run_cli, baseline_full_tier):
    code, out, err = run_cli(baseline_full_tier, ["3436", "make test"], cwd=tmp_path)

    assert (code, out.strip()) == (0, "run")
