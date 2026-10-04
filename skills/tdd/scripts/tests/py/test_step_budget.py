"""In-process cases for veri/step_budget.py, the module step-budget.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def step_budget():
    return importlib.import_module("veri.step_budget")


def test_main_with_both_budgets_unset_prints_the_defaults_and_refuses_an_argument_with_the_usage_line(monkeypatch, capsys, step_budget):
    monkeypatch.delenv("VERI_STEP_BUDGET", raising=False)
    monkeypatch.delenv("VERI_RUN_BUDGET", raising=False)
    seen = []
    for argv in ([], ["0"]):
        code = step_budget.main(argv)
        out, err = capsys.readouterr()
        seen.append((code, out, err))
    assert [code for code, _, _ in seen if code not in range(4)] == []
    assert seen == [
        (0, "12\n120\n", ""),
        (2, "", "usage: step-budget.sh (takes no arguments)\n"),
    ]


def test_main_checks_the_budgets_echoing_them_as_given_and_refusing_a_bad_one_after_the_arguments(monkeypatch, capsys, step_budget):
    def bad(var, value):
        return "step-budget: %s must be a non-negative decimal number: %s\n" % (var, value)

    usage = "usage: step-budget.sh (takes no arguments)\n"
    cases = [
        ({"VERI_STEP_BUDGET": "7.5", "VERI_RUN_BUDGET": "42.25"}, [], (0, "7.5\n42.25\n", "")),
        ({"VERI_STEP_BUDGET": "0", "VERI_RUN_BUDGET": "007.50"}, [], (0, "0\n007.50\n", "")),
        ({"VERI_RUN_BUDGET": "3"}, [], (0, "12\n3\n", "")),
        ({"VERI_STEP_BUDGET": ""}, [], (2, "", bad("VERI_STEP_BUDGET", ""))),
        ({"VERI_RUN_BUDGET": ""}, [], (2, "", bad("VERI_RUN_BUDGET", ""))),
    ]
    for value in ("twelve", "-5", "1.", ".5", "1e3", " 5", "5\n", "٣"):
        cases.append(({"VERI_STEP_BUDGET": value}, [], (2, "", bad("VERI_STEP_BUDGET", value))))
        cases.append(({"VERI_RUN_BUDGET": value}, [], (2, "", bad("VERI_RUN_BUDGET", value))))
    cases += [
        ({"VERI_STEP_BUDGET": "twelve", "VERI_RUN_BUDGET": "-5"}, [], (2, "", bad("VERI_STEP_BUDGET", "twelve"))),
        ({"VERI_STEP_BUDGET": "x"}, ["extra"], (2, "", usage)),
        ({}, [""], (2, "", usage)),
    ]
    seen = []
    expected = []
    for env, argv, want in cases:
        monkeypatch.delenv("VERI_STEP_BUDGET", raising=False)
        monkeypatch.delenv("VERI_RUN_BUDGET", raising=False)
        for name, value in env.items():
            monkeypatch.setenv(name, value)
        code = step_budget.main(argv)
        out, err = capsys.readouterr()
        seen.append((env, argv, (code, out, err)))
        expected.append((env, argv, want))
    assert seen == expected
