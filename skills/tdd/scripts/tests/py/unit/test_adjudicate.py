"""In-process cases for veri/adjudicate.py, the module adjudicate.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def adjudicate():
    return importlib.import_module("veri.adjudicate")


def test_main_with_no_argument_exits_2_printing_the_usage_line_on_stderr(run_cli, adjudicate):
    code, out, err = run_cli(adjudicate, [])
    assert (code, out, err) == (
        2,
        "",
        "usage: adjudicate.sh --check-budget | left <n> | record <n> <cause> <leaf-output>\n",
    )


def test_check_budget_exits_0_silently_when_the_budget_is_unset(run_cli, adjudicate, monkeypatch):
    monkeypatch.delenv("VERI_ADJUDICATE_BUDGET", raising=False)
    code, out, err = run_cli(adjudicate, ["--check-budget"])
    assert (code, out, err) == (0, "", "")


def test_check_budget_exits_2_naming_the_variable_for_a_budget_that_is_not_a_whole_number(
    run_cli, adjudicate, monkeypatch
):
    for bad in ("-1", "two", "1.5"):
        monkeypatch.setenv("VERI_ADJUDICATE_BUDGET", bad)
        code, out, err = run_cli(adjudicate, ["--check-budget"])
        assert (code, out, "VERI_ADJUDICATE_BUDGET" in err) == (2, "", True), bad


def test_left_exits_0_when_the_adjudications_since_the_last_conductor_start_are_fewer_than_the_budget(
    run_cli, adjudicate, monkeypatch, tmp_path
):
    import json

    monkeypatch.delenv("VERI_ADJUDICATE_BUDGET", raising=False)
    adjudicated = {"issue": "7", "event": "adjudicated", "cause": "ci-timeout", "outcome": "retry"}
    events = [
        {"issue": "7", "event": "conductor-start"},
        adjudicated,
        adjudicated,
        {"issue": "7", "event": "conductor-start"},
        adjudicated,
        {**adjudicated, "issue": "8"},
    ]
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    code, out, err = run_cli(adjudicate, ["left", "7"], cwd=tmp_path)
    assert (code, out, err) == (0, "", "")
