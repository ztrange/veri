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


def _use_fixture_adjudicate_md(parse_adjudication, tmp_path, monkeypatch, bullets):
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "ADJUDICATE.md").write_text("### Eligible causes\n\n" + bullets)
    monkeypatch.setattr(parse_adjudication, "__file__", str(skill / "scripts" / "veri" / "parse_adjudication.py"))


def test_main_on_a_route_line_whose_token_the_cause_lists_prints_route_token_then_reason_exiting_0(run_cli, parse_adjudication, tmp_path, monkeypatch):
    _use_fixture_adjudicate_md(parse_adjudication, tmp_path, monkeypatch, "- `ci-timeout`: `fix-it`\n")
    leaf = tmp_path / "adjudicate-ci-timeout.out"
    leaf.write_text("ADJUDICATION: route fix-it — the failure is a known flake\n")
    code, out, err = run_cli(parse_adjudication, [str(leaf)])
    assert (code, out) == (0, "route fix-it\nthe failure is a known flake\n")


def test_main_on_a_route_line_whose_token_the_cause_does_not_list_exits_2_with_nothing_on_stdout(run_cli, parse_adjudication, tmp_path, monkeypatch):
    _use_fixture_adjudicate_md(parse_adjudication, tmp_path, monkeypatch, "- `ci-timeout`: `fix-it`\n")
    listed = tmp_path / "listed.out"
    listed.write_text("ADJUDICATION: route fix-it — known flake\n")
    unlisted = tmp_path / "unlisted.out"
    unlisted.write_text("ADJUDICATION: route elsewhere — known flake\n")
    assert run_cli(parse_adjudication, [str(listed)])[:2] == (0, "route fix-it\nknown flake\n")
    code, out, err = run_cli(parse_adjudication, [str(unlisted)])
    assert (code, out) == (2, "")


def test_main_on_a_non_route_outcome_followed_by_a_listed_route_token_exits_2_with_nothing_on_stdout(run_cli, parse_adjudication, tmp_path, monkeypatch):
    _use_fixture_adjudicate_md(parse_adjudication, tmp_path, monkeypatch, "- `ci-timeout`: `fix-it`\n")
    route = tmp_path / "route.out"
    route.write_text("ADJUDICATION: route fix-it — known flake\n")
    retry = tmp_path / "retry.out"
    retry.write_text("ADJUDICATION: retry fix-it — x\n")
    assert run_cli(parse_adjudication, [str(route)])[:2] == (0, "route fix-it\nknown flake\n")
    code, out, err = run_cli(parse_adjudication, [str(retry)])
    assert (code, out) == (2, "")


def test_main_takes_the_route_tokens_a_cause_may_use_from_the_eligible_causes_list_in_adjudicate_md(run_cli, parse_adjudication, tmp_path, monkeypatch):
    skill = tmp_path / "skill"
    (skill / "scripts" / "veri").mkdir(parents=True)
    (skill / "ADJUDICATE.md").write_text(
        "### Eligible causes\n\n- `some-cause`: `route-a`\n- `ci-timeout`: none\n"
    )
    monkeypatch.setattr(parse_adjudication, "__file__", str(skill / "scripts" / "veri" / "parse_adjudication.py"))
    listed = tmp_path / "adjudicate-some-cause.out"
    listed.write_text("ADJUDICATION: route route-a — known flake\n")
    (tmp_path / "other").mkdir()
    unlisted = tmp_path / "other" / "adjudicate-some-cause.out"
    unlisted.write_text("ADJUDICATION: route route-b — known flake\n")
    assert run_cli(parse_adjudication, [str(listed)])[:2] == (0, "route route-a\nknown flake\n")
    code, out, err = run_cli(parse_adjudication, [str(unlisted)])
    assert (code, out) == (2, "")


def test_main_on_a_route_token_that_is_only_part_of_a_listed_token_exits_2_with_nothing_on_stdout(run_cli, parse_adjudication, tmp_path, monkeypatch):
    _use_fixture_adjudicate_md(parse_adjudication, tmp_path, monkeypatch, "- `ci-timeout`: `route-a`\n")
    whole = tmp_path / "whole.out"
    whole.write_text("ADJUDICATION: route route-a — known flake\n")
    assert run_cli(parse_adjudication, [str(whole)])[:2] == (0, "route route-a\nknown flake\n")
    for i, part in enumerate(["route-", "a", "oute-a"]):
        leaf = tmp_path / f"part{i}.out"
        leaf.write_text(f"ADJUDICATION: route {part} — known flake\n")
        code, out, err = run_cli(parse_adjudication, [str(leaf)])
        assert (code, out) == (2, ""), part


def test_main_on_a_route_line_when_the_cause_lists_no_route_token_exits_2_with_nothing_on_stdout(run_cli, parse_adjudication, tmp_path, monkeypatch):
    _use_fixture_adjudicate_md(parse_adjudication, tmp_path, monkeypatch, "- `ci-timeout`: none\n")
    leaf = tmp_path / "adjudicate-ci-timeout.out"
    leaf.write_text("ADJUDICATION: route fix-it — known flake\n")
    code, out, err = run_cli(parse_adjudication, [str(leaf)])
    assert (code, out) == (2, "")
