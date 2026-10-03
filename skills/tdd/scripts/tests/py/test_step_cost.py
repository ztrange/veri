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


@pytest.mark.parametrize("log, expected", [
    ('{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30134540000000004"}\n'
     '{"ts": 2, "issue": "448", "actor": "developer", "phase": "green", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}\n'
     '{"ts": 3, "issue": "448", "actor": "conductor", "phase": "scope", "step": "", "event": "usage", "total_cost_usd": "0.25"}\n',
     (0, "1.55\n")),
    ('{"ts": 1, "issue": "448", "actor": "verifier", "phase": "red", "step": "step one", "event": "verdict", "verdict": "PASS"}\n'
     '{"ts": 2, "issue": "448", "actor": "developer", "phase": "green", "step": "step one", "event": "test-run", "exit": "0"}\n',
     (3, "")),
], ids=["every-usage-event-step-less-included", "no-usage-event"])
def test_main_run_sums_every_usage_event_step_less_ones_included_and_returns_3_with_nothing_printed_when_there_is_none(log, expected, tmp_path, monkeypatch, capsys, step_cost):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(log)
    monkeypatch.chdir(tmp_path)

    code = step_cost.main(["--run"])

    out, err = capsys.readouterr()
    assert (code, out) == expected


@pytest.mark.parametrize("log, expected", [
    ('{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}\n'
     '{"ts": 2, "issue": "448", "actor": "conductor", "phase": "scope", "step": "", "event": "usage", "total_cost_usd": "0.25"}\n'
     '{"ts": 3, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30134540000000004"}\n'
     '{"ts": 4, "issue": "448", "actor": "verifier", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "0.5"}\n'
     '{"ts": 5, "issue": "448", "actor": "conductor", "phase": "scope", "event": "usage", "total_cost_usd": "0.10"}\n'
     '{"ts": 6, "issue": "448", "actor": "verifier", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.12"}\n',
     (0, "1.50 2\n0.35 2\n0.42 2\n")),
    ('{"ts": 1, "issue": "448", "actor": "verifier", "phase": "red", "step": "step one", "event": "verdict", "verdict": "PASS"}\n',
     (3, "")),
], ids=["rows-in-first-mention-order-step-less-its-own-row", "no-usage-event"])
def test_main_steps_prints_one_dollars_and_leaves_line_per_step_in_first_mention_order_step_less_events_their_own_row_and_returns_3_when_there_is_none(log, expected, tmp_path, monkeypatch, capsys, step_cost):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(log)
    monkeypatch.chdir(tmp_path)

    code = step_cost.main(["--steps"])

    out, err = capsys.readouterr()
    assert (code, out) == expected


@pytest.mark.parametrize("log, expected", [
    ('{"ts": 1, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30"}\n'
     '{"ts": 2, "issue": "448", "actor": "verifier", "phase": "red", "step": "step one", "event": "usage"}\n'
     '{"ts": 3, "issue": "448", "actor": "developer", "phase": "green", "step": "step one", "event": "usage", "total_cost_usd": ""}\n'
     '{"ts": 4, "issue": "448", "actor": "developer", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}\n',
     {"--steps": (0, "0.30 3\n1.00 1\n"), "step one": (0, "0.30\n"), "--run": (0, "1.30\n")}),
    ('{"ts": 1, "issue": "448", "actor": "verifier", "phase": "red", "step": "step three", "event": "verdict", "verdict": "PASS"}\n'
     '{"ts": 2, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "0.30"}\n'
     '{"ts": 3, "issue": "448", "actor": "developer", "phase": "green", "step": "step one", "event": "test-run", "exit": "0", "total_cost_usd": "5.0"}\n'
     '{"ts": 4, "issue": "448", "actor": "verifier", "phase": "green", "step": "step one", "event": "usage", "total_cost_usd": "0.20"}\n'
     '{"ts": 5, "issue": "448", "actor": "verifier", "phase": "green", "step": "step one", "event": "verdict", "verdict": "PASS"}\n',
     {"--steps": (0, "0.50 2\n"), "step one": (0, "0.50\n"), "step three": (3, ""), "--run": (0, "0.50\n")}),
], ids=["absent-or-empty-cost-adds-zero-and-counts-as-a-leaf", "non-usage-events-create-no-step-and-add-no-cost"])
def test_main_counts_a_usage_event_with_an_absent_or_empty_cost_as_a_zero_cost_leaf_and_ignores_events_that_are_not_usage_events_in_every_call(log, expected, tmp_path, monkeypatch, capsys, step_cost):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(log)
    monkeypatch.chdir(tmp_path)

    observed = {}
    for arg in expected:
        code = step_cost.main([arg])
        out, err = capsys.readouterr()
        observed[arg] = (code, out)

    assert observed == expected
