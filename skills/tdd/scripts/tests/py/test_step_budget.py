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
