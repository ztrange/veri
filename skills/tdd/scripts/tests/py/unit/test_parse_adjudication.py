"""In-process cases for veri/parse_adjudication.py, the module parse-adjudication.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def parse_adjudication():
    return importlib.import_module("veri.parse_adjudication")


def test_main_with_no_argument_exits_2_printing_the_usage_line_on_stderr(run_cli, parse_adjudication):
    code, out, err = run_cli(parse_adjudication, [])
    assert (code, out, err) == (2, "", "usage: parse-adjudication.sh <leaf-output>\n")


def test_main_prints_the_last_adjudication_lines_outcome_then_reason_exiting_0(run_cli, parse_adjudication, tmp_path):
    leaf = tmp_path / "leaf.out"
    leaf.write_text(
        "thinking\n"
        "ADJUDICATION: bail — first guess\n"
        "more thinking\n"
        "ADJUDICATION: retry — CI is still queued behind a busy runner\n"
    )
    code, out, err = run_cli(parse_adjudication, [str(leaf)])
    assert (code, out) == (0, "retry\nCI is still queued behind a busy runner\n")


def test_main_on_a_file_with_no_adjudication_line_exits_2_with_nothing_on_stdout(run_cli, parse_adjudication, tmp_path):
    leaf = tmp_path / "leaf.out"
    leaf.write_text("thinking\nno verdict here\n")
    code, out, err = run_cli(parse_adjudication, [str(leaf)])
    assert (code, out) == (2, "")


def test_main_on_a_last_line_with_an_outcome_other_than_retry_bail_or_route_exits_2_with_nothing_on_stdout(run_cli, parse_adjudication, tmp_path):
    leaf = tmp_path / "leaf.out"
    leaf.write_text("ADJUDICATION: retry — fine\nADJUDICATION: shrug — no idea\n")
    code, out, err = run_cli(parse_adjudication, [str(leaf)])
    assert (code, out) == (2, "")
