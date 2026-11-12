"""pin-target.sh: the verify-pin target is the step's own red report's TARGET_TEST."""
import importlib

import pytest


@pytest.fixture
def pin_target():
    return importlib.import_module("veri.pin_target")


def test_main_prints_the_step_red_reports_target_not_a_red_missing_reports_3324(
        tmp_path, run_cli, pin_target):
    red = tmp_path / "develop-red.out"
    red.write_text("TEST_PATH: t.py\nTARGET_TEST: test_a_refuses\nAGAINST_UNMODIFIED: FAILS\n")
    missing = tmp_path / "develop-red-missing.out"
    missing.write_text("TEST_PATH: t.py\nTARGET_TEST: test_b_accepts\nAGAINST_UNMODIFIED: PASSES\n")

    code, out, err = run_cli(pin_target, [str(red), str(missing)], cwd=tmp_path)

    assert (code, out.strip()) == (0, "test_a_refuses"), err


def test_main_prints_only_the_first_target_of_a_red_report_with_several_3324(
        tmp_path, run_cli, pin_target):
    red = tmp_path / "develop-red.out"
    red.write_text("TARGET_TEST: test_first\nTARGET_TEST: test_second\nAGAINST_UNMODIFIED: FAILS\n")

    code, out, err = run_cli(pin_target, [str(red)], cwd=tmp_path)

    assert (code, out) == (0, "test_first\n"), err


def test_main_reads_the_target_from_a_stream_json_red_report_3324(
        tmp_path, run_cli, pin_target):
    import json
    report = ("TEST_PATH: t.py\nTARGET_TEST: test_a_refuses\n"
              "AGAINST_UNMODIFIED: PASSES\n")
    red = tmp_path / "develop-red.out"
    red.write_text("\n".join(json.dumps(r) for r in [
        {"type": "system", "subtype": "init"},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "TARGET_TEST: test_draft"}]}},
        {"type": "result", "subtype": "success", "is_error": False, "result": report},
    ]) + "\n")

    code, out, err = run_cli(pin_target, [str(red)], cwd=tmp_path)

    assert (code, out.strip()) == (0, "test_a_refuses"), err


def test_main_skips_non_object_lines_and_non_text_results_in_a_stream_json_report_3324(
        tmp_path, run_cli, pin_target):
    import json
    report = "TARGET_TEST: test_a_refuses\nAGAINST_UNMODIFIED: PASSES\n"
    red = tmp_path / "develop-red.out"
    red.write_text("\n".join([
        "42",
        json.dumps({"type": "result", "subtype": "success", "result": report}),
        json.dumps({"type": "result", "subtype": "error", "result": None}),
    ]) + "\n")

    code, out, err = run_cli(pin_target, [str(red)], cwd=tmp_path)

    assert (code, out.strip()) == (0, "test_a_refuses"), err


def test_main_exits_2_printing_nothing_for_an_unreadable_report_3324(
        tmp_path, run_cli, pin_target):
    missing = tmp_path / "no-such-develop-red.out"

    code, out, err = run_cli(pin_target, [str(missing)], cwd=tmp_path)

    assert (code, out) == (2, ""), err


def test_main_exits_2_printing_nothing_for_a_readable_report_with_no_target_3324(
        tmp_path, run_cli, pin_target):
    red = tmp_path / "develop-red.out"
    red.write_text("TEST_PATH: t.py\nAGAINST_UNMODIFIED: PASSES\n")

    code, out, err = run_cli(pin_target, [str(red)], cwd=tmp_path)

    assert (code, out) == (2, ""), err
