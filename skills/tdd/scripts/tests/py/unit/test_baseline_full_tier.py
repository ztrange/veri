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


def test_main_with_reuse_and_a_recorded_time_prints_reuse_and_the_seconds_and_exits_0_3436(
        tmp_path, run_cli, baseline_full_tier):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    (tmp_path / ".git").mkdir()
    code, _, _ = run_cli(full_tier_time, ["--record", "727", "make test"], cwd=tmp_path)
    assert code == 0

    code, out, err = run_cli(baseline_full_tier, ["3436", "make test"],
                             env={"VERI_BASELINE_FULL_TIER": "reuse"}, cwd=tmp_path)

    assert (code, out.strip()) == (0, "reuse 727")


def test_main_prints_run_when_unset_with_a_recorded_time_and_under_reuse_with_none_recorded_3436(
        tmp_path, run_cli, baseline_full_tier):
    full_tier_time = importlib.import_module("veri.full_tier_time")
    (tmp_path / ".git").mkdir()
    code, _, _ = run_cli(full_tier_time, ["--record", "727", "make test"], cwd=tmp_path)
    assert code == 0

    unset = run_cli(baseline_full_tier, ["3436", "make test"], cwd=tmp_path)
    reuse_unrecorded = run_cli(baseline_full_tier, ["3436", "make other"],
                               env={"VERI_BASELINE_FULL_TIER": "reuse"}, cwd=tmp_path)
    reuse_recorded = run_cli(baseline_full_tier, ["3436", "make test"],
                             env={"VERI_BASELINE_FULL_TIER": "reuse"}, cwd=tmp_path)

    assert (unset[0], unset[1].strip()) == (0, "run")
    assert (reuse_unrecorded[0], reuse_unrecorded[1].strip()) == (0, "run")
    assert reuse_recorded[1].strip() == "reuse 727"
