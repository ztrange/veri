"""In-process cases for veri/time_budget.py, the module time-budget.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture(autouse=True)
def defaults(monkeypatch):
    monkeypatch.delenv("VERI_UNIT_BUDGET", raising=False)
    monkeypatch.delenv("VERI_TIME_WARN_RATIO", raising=False)


@pytest.fixture
def time_budget():
    return importlib.import_module("veri.time_budget")


def test_main_prints_the_defaults_with_or_without_an_argument_and_returns_2_on_a_non_numeric_budget(capfd, monkeypatch, time_budget):
    answers = []
    for argv in ([], ["--bogus"]):
        code = time_budget.main(argv)
        answers.append((code,) + capfd.readouterr())
    monkeypatch.setenv("VERI_UNIT_BUDGET", "ten")
    code = time_budget.main([])
    answers.append((code,) + capfd.readouterr())
    assert answers == [
        (0, "10\n1.5\n", ""),
        (0, "10\n1.5\n", ""),
        (2, "", "time-budget: VERI_UNIT_BUDGET must be a number of seconds: ten\n"),
    ]
