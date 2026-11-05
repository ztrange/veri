"""In-process cases for veri/full_tier_time.py, the module full-tier-time.sh is a shim over."""
import importlib
import json
import os

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


def test_main_asked_for_a_command_with_no_record_while_the_file_holds_another_commands_time_prints_nothing_and_exits_3(
        tmp_path, run_cli, full_tier_time):
    rec_code, _, _ = run_cli(full_tier_time, ["--record", "587", "make unit"], cwd=tmp_path)

    code, out, err = run_cli(full_tier_time, ["make test"], cwd=tmp_path)

    assert (rec_code, code, out) == (0, 3, "")


def test_main_recording_a_command_again_replaces_its_time_and_leaves_another_commands_time_unchanged(
        tmp_path, run_cli, full_tier_time):
    run_cli(full_tier_time, ["--record", "587", "make test"], cwd=tmp_path)
    run_cli(full_tier_time, ["--record", "42", "make unit"], cwd=tmp_path)
    run_cli(full_tier_time, ["--record", "601", "make test"], cwd=tmp_path)

    replaced = run_cli(full_tier_time, ["make test"], cwd=tmp_path)
    other = run_cli(full_tier_time, ["make unit"], cwd=tmp_path)

    assert (replaced[0], replaced[1].strip(), other[0], other[1].strip()) == (0, "601", 0, "42")


@pytest.mark.parametrize("stored", ['"abc"', "null", '""', '"-5"', '"1.5"'],
                         ids=["word", "null", "empty", "negative", "fractional"])
def test_main_asked_for_a_command_whose_stored_time_is_not_a_whole_number_exits_2_with_one_stderr_line_naming_the_file(
        tmp_path, run_cli, full_tier_time, stored):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "full-tier-time.json").write_text('{"make test": %s}' % stored)

    code, out, err = run_cli(full_tier_time, ["make test"], cwd=tmp_path)

    assert (code, out, len(err.splitlines()), "full-tier-time.json" in err) == (2, "", 1, True)


@pytest.mark.parametrize("stored", ["{not json", "[1, 2]", "5", '{"other": "abc"}', '{"other": null}'],
                         ids=["bad-json", "list", "number", "word-value", "null-value"])
def test_main_asked_to_record_over_a_corrupt_record_replaces_it_with_a_record_holding_the_new_time(
        tmp_path, run_cli, full_tier_time, stored):
    (tmp_path / ".tdd").mkdir()
    path = tmp_path / ".tdd" / "full-tier-time.json"
    path.write_text(stored)

    code, _, _ = run_cli(full_tier_time, ["--record", "42", "make test"], cwd=tmp_path)

    assert (code, json.loads(path.read_text())) == (0, {"make test": "42"})


def test_main_asked_to_record_over_an_undecodable_record_replaces_it_with_a_record_holding_the_new_time(
        tmp_path, run_cli, full_tier_time):
    (tmp_path / ".tdd").mkdir()
    path = tmp_path / ".tdd" / "full-tier-time.json"
    path.write_bytes(b"\xff\xfe\x00")

    code, _, _ = run_cli(full_tier_time, ["--record", "42", "make test"], cwd=tmp_path)

    assert (code, json.loads(path.read_text())) == (0, {"make test": "42"})


def test_main_asked_to_record_when_the_write_fails_midway_leaves_the_old_record_intact_and_no_stray_file(
        tmp_path, run_cli, full_tier_time, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    path = tmp_path / ".tdd" / "full-tier-time.json"
    path.write_text('{"make test": "7"}')

    def dump_then_die(obj, f, *args, **kwargs):
        f.write('{"make te')
        f.flush()
        raise OSError("disk full")

    monkeypatch.setattr(full_tier_time.json, "dump", dump_then_die)

    code, _, _ = run_cli(full_tier_time, ["--record", "42", "make test"], cwd=tmp_path)

    assert (code, path.read_text(), os.listdir(tmp_path / ".tdd")) == (
        2, '{"make test": "7"}', ["full-tier-time.json"])


@pytest.mark.parametrize("digit", ["\u00b2", "\u0663"], ids=["superscript-two", "arabic-indic-three"])
def test_main_asked_for_a_command_whose_stored_time_is_a_non_ascii_digit_exits_2_with_one_stderr_line(
        tmp_path, run_cli, full_tier_time, digit):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "full-tier-time.json").write_text(
        json.dumps({"make test": digit}), encoding="utf-8")

    code, out, err = run_cli(full_tier_time, ["make test"], cwd=tmp_path)

    assert (code, out, len(err.splitlines())) == (2, "", 1)


def test_main_asked_for_a_command_with_a_valid_time_while_another_entry_is_not_a_whole_number_exits_2(
        tmp_path, run_cli, full_tier_time):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "full-tier-time.json").write_text('{"make test": "5", "other": "abc"}')

    code, out, err = run_cli(full_tier_time, ["make test"], cwd=tmp_path)

    assert (code, out, len(err.splitlines())) == (2, "", 1)


def _unreadable_record(tmp_path, full_tier_time, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    path = tmp_path / ".tdd" / "full-tier-time.json"
    path.write_text('{"other": "9"}')

    def denied(*args, **kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(full_tier_time.json, "load", denied)
    return path


def test_main_asked_to_record_over_an_unreadable_record_replaces_the_whole_file_with_the_new_time(
        tmp_path, run_cli, full_tier_time, monkeypatch):
    path = _unreadable_record(tmp_path, full_tier_time, monkeypatch)

    code, _, _ = run_cli(full_tier_time, ["--record", "42", "make test"], cwd=tmp_path)

    assert (code, json.loads(path.read_text())) == (0, {"make test": "42"})


def test_main_asked_for_a_command_when_the_record_is_unreadable_exits_2_with_one_stderr_line(
        tmp_path, run_cli, full_tier_time, monkeypatch):
    _unreadable_record(tmp_path, full_tier_time, monkeypatch)

    code, out, err = run_cli(full_tier_time, ["make test"], cwd=tmp_path)

    assert (code, out, len(err.splitlines()), "unreadable record" in err) == (2, "", 1, True)


@pytest.mark.parametrize("exc", [RuntimeError, KeyboardInterrupt])
def test_main_asked_to_record_when_the_write_dies_with_a_non_os_error_leaves_the_old_record_intact_and_no_stray_file(
        tmp_path, run_cli, full_tier_time, monkeypatch, exc):
    (tmp_path / ".tdd").mkdir()
    path = tmp_path / ".tdd" / "full-tier-time.json"
    path.write_text('{"make test": "7"}')

    def dump_then_die(obj, f, *args, **kwargs):
        f.write('{"make te')
        f.flush()
        raise exc("boom")

    monkeypatch.setattr(full_tier_time.json, "dump", dump_then_die)

    try:
        run_cli(full_tier_time, ["--record", "42", "make test"], cwd=tmp_path)
    except BaseException:
        pass

    assert (path.read_text(), os.listdir(tmp_path / ".tdd")) == (
        '{"make test": "7"}', ["full-tier-time.json"])


def test_main_asked_to_record_creates_its_partial_file_next_to_the_record(
        tmp_path, run_cli, full_tier_time, monkeypatch):
    dirs = []
    real = full_tier_time.tempfile.mkstemp

    def spy(*args, **kwargs):
        dirs.append(kwargs.get("dir"))
        return real(*args, **kwargs)

    monkeypatch.setattr(full_tier_time.tempfile, "mkstemp", spy)

    run_cli(full_tier_time, ["--record", "42", "make test"], cwd=tmp_path)

    assert dirs == [str(tmp_path / ".tdd")]
