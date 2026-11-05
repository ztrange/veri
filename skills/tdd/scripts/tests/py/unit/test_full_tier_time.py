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


def test_main_asked_for_a_command_after_recording_its_time_prints_those_seconds_and_exits_0(
        tmp_path, run_cli, full_tier_time):
    rec_code, _, _ = run_cli(full_tier_time, ["--record", "587", "make test"], cwd=tmp_path)

    code, out, err = run_cli(full_tier_time, ["make test"], cwd=tmp_path)

    assert (rec_code, code, out.strip()) == (0, 0, "587")


def test_main_asked_for_a_command_when_the_record_file_is_not_parseable_exits_2_with_a_stderr_line(
        tmp_path, run_cli, full_tier_time):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "full-tier-time.json").write_text("{not json")

    code, out, err = run_cli(full_tier_time, ["make test"], cwd=tmp_path)

    assert (code, out) == (2, "")
    assert err.strip() != ""


@pytest.mark.parametrize("argv", [
    ["--record", "12.5", "make test"],
    ["--record", "-3", "make test"],
    ["--record", "12"],
], ids=["fractional-seconds", "negative-seconds", "no-command"])
def test_main_asked_to_record_bad_seconds_or_no_command_prints_the_usage_line_and_exits_2_recording_nothing(
        tmp_path, run_cli, full_tier_time, argv):
    code, out, err = run_cli(full_tier_time, argv, cwd=tmp_path)

    assert (code, out) == (2, "")
    assert "usage: full-tier-time.sh [--record <seconds>] <command>" in err
    assert not (tmp_path / ".tdd" / "full-tier-time.json").exists()


def test_main_asked_to_record_non_ascii_digit_seconds_prints_the_usage_line_and_exits_2_recording_nothing(
        tmp_path, run_cli, full_tier_time):
    code, out, err = run_cli(full_tier_time, ["--record", "²", "make test"], cwd=tmp_path)

    assert (code, out) == (2, "")
    assert "usage: full-tier-time.sh [--record <seconds>] <command>" in err
    assert not (tmp_path / ".tdd" / "full-tier-time.json").exists()
