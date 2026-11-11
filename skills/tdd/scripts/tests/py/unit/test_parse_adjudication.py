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


def test_main_on_a_route_line_whose_token_the_cause_lists_prints_route_token_then_reason_exiting_0(run_cli, parse_adjudication, tmp_path, monkeypatch):
    monkeypatch.setattr(parse_adjudication, "ELIGIBLE_ROUTES", {"ci-timeout": ("fix-it",)}, raising=False)
    leaf = tmp_path / "adjudicate-ci-timeout.out"
    leaf.write_text("ADJUDICATION: route fix-it — the failure is a known flake\n")
    code, out, err = run_cli(parse_adjudication, [str(leaf)])
    assert (code, out) == (0, "route fix-it\nthe failure is a known flake\n")


def test_main_on_a_route_line_whose_token_the_cause_does_not_list_exits_2_with_nothing_on_stdout(run_cli, parse_adjudication, tmp_path, monkeypatch):
    monkeypatch.setattr(parse_adjudication, "ELIGIBLE_ROUTES", {"ci-timeout": ("fix-it",)}, raising=False)
    listed = tmp_path / "listed.out"
    listed.write_text("ADJUDICATION: route fix-it — known flake\n")
    unlisted = tmp_path / "unlisted.out"
    unlisted.write_text("ADJUDICATION: route elsewhere — known flake\n")
    assert run_cli(parse_adjudication, [str(listed)])[:2] == (0, "route fix-it\nknown flake\n")
    code, out, err = run_cli(parse_adjudication, [str(unlisted)])
    assert (code, out) == (2, "")


def test_main_on_a_non_route_outcome_followed_by_a_listed_route_token_exits_2_with_nothing_on_stdout(run_cli, parse_adjudication, tmp_path, monkeypatch):
    monkeypatch.setattr(parse_adjudication, "ELIGIBLE_ROUTES", {"ci-timeout": ("fix-it",)}, raising=False)
    route = tmp_path / "route.out"
    route.write_text("ADJUDICATION: route fix-it — known flake\n")
    retry = tmp_path / "retry.out"
    retry.write_text("ADJUDICATION: retry fix-it — x\n")
    assert run_cli(parse_adjudication, [str(route)])[:2] == (0, "route fix-it\nknown flake\n")
    code, out, err = run_cli(parse_adjudication, [str(retry)])
    assert (code, out) == (2, "")
