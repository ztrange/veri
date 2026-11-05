"""In-process cases for veri/full_tier_time.py, the module full-tier-time.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def full_tier_time():
    return importlib.import_module("veri.full_tier_time")


def test_main_asked_for_a_command_with_no_record_prints_nothing_and_exits_3(
        tmp_path, run_cli, full_tier_time):
    code, out, err = run_cli(full_tier_time, ["make test"], cwd=tmp_path)

    assert (code, out) == (3, "")


def test_main_called_with_no_argument_prints_the_usage_line_to_stderr_and_exits_2(
        tmp_path, run_cli, full_tier_time):
    code, out, err = run_cli(full_tier_time, [], cwd=tmp_path)

    assert (code, out) == (2, "")
    assert "usage: full-tier-time.sh [--record <seconds>] <command>" in err
