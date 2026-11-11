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
