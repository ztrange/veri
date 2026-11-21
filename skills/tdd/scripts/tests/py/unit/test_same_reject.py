"""In-process cases for veri/same_reject.py, the module same-reject.sh is a shim over."""
import importlib

import pytest

USAGE = "usage: same-reject.sh <previous-reason-file> <current-reason-file>\n"


@pytest.fixture
def same_reject():
    return importlib.import_module("veri.same_reject")


def test_main_exits_2_with_a_usage_line_without_arguments_and_exits_2_when_either_file_is_missing_or_holds_no_reason(
        tmp_path, run_cli, same_reject):
    reasoned = tmp_path / "reasoned.txt"
    reasoned.write_text("VERDICT: REJECT\nREASON: WRONG_TEST\n")
    reasonless = tmp_path / "reasonless.txt"
    reasonless.write_text("")
    missing = tmp_path / "missing.txt"

    results = {}
    for argv in ([], [str(missing), str(reasoned)], [str(reasoned), str(missing)],
                 [str(reasonless), str(reasoned)], [str(reasoned), str(reasonless)]):
        code, out, err = run_cli(same_reject, argv)
        results[tuple(argv)] = (code, out, err == USAGE if not argv else err != "")

    assert results == {
        (): (2, "", True),
        (str(missing), str(reasoned)): (2, "", True),
        (str(reasoned), str(missing)): (2, "", True),
        (str(reasonless), str(reasoned)): (2, "", True),
        (str(reasoned), str(reasonless)): (2, "", True),
    }


def test_main_exits_0_when_the_reason_lines_are_equal_after_collapsing_runs_of_whitespace(
        tmp_path, run_cli, same_reject):
    previous = tmp_path / "previous.txt"
    previous.write_text("VERDICT: REJECT\nREASON: WRONG_TEST   the  test\tpins mechanism\n")
    current = tmp_path / "current.txt"
    current.write_text("REASON:  WRONG_TEST the test pins   mechanism \nVERDICT: REJECT\n")

    code, out, err = run_cli(same_reject, [str(previous), str(current)])

    assert (code, out, err) == (0, "", "")


def test_main_exits_1_when_the_reason_lines_differ_after_collapsing_runs_of_whitespace(
        tmp_path, run_cli, same_reject):
    previous = tmp_path / "previous.txt"
    previous.write_text("VERDICT: REJECT\nREASON: WRONG_TEST   the  test\tpins mechanism\n")
    current = tmp_path / "current.txt"
    current.write_text("VERDICT: REJECT\nREASON:  tests-frozen blocked   the edit\n")

    code, out, err = run_cli(same_reject, [str(previous), str(current)])

    assert (code, out, err) == (1, "", "")


def test_main_exits_0_for_two_identical_reason_files_with_no_reason_prefix_the_format_parse_verdict_writes_4550(
        tmp_path, run_cli, same_reject):
    previous = tmp_path / "previous.txt"
    previous.write_text("guard x is required by no test\nthe case pins mechanism\n")
    current = tmp_path / "current.txt"
    current.write_text("guard x is required by no test\nthe case pins mechanism\n")

    code, out, err = run_cli(same_reject, [str(previous), str(current)])

    assert (code, out, err) == (0, "", "")
