"""In-process cases for veri/step_cost.py, the module step-cost.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def step_cost():
    return importlib.import_module("veri.step_cost")


def test_the_module_docstring_says_it_reports_leaf_spend_only_and_the_conductors_spending_is_in_no_usage_event(step_cost):
    doc = " ".join((step_cost.__doc__ or "").split())
    missing = [part for part in ("leaf spend only", "conductor's own spending is in no `usage` event")
               if part not in doc]
    assert missing == []


@pytest.mark.parametrize("argv", [[], ["--bogus"]])
def test_main_returns_2_with_the_usage_line_on_stderr_and_nothing_on_stdout_for_no_argument_or_an_unknown_option(argv, capsys, step_cost):
    code = step_cost.main(argv)

    out, err = capsys.readouterr()
    assert (code, out, "usage: step-cost.sh <step-text> | --run | --steps" in err) == (2, "", True)


def test_main_prints_a_steps_usage_events_total_cost_usd_sum_to_two_decimals_and_returns_0(tmp_path, monkeypatch, capsys, step_cost):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(
        '{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30134540000000004"}\n'
        '{"ts": 2, "issue": "448", "actor": "developer", "phase": "green", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}\n'
        '{"ts": 3, "issue": "448", "actor": "verifier", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.12"}\n')
    monkeypatch.chdir(tmp_path)

    code = step_cost.main(["step one"])

    out, err = capsys.readouterr()
    assert (code, out) == (0, "0.42\n")
