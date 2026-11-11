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
