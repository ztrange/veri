"""In-process cases for veri/step_cost.py, the module step-cost.sh is a shim over."""
import importlib
import os

import pytest


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


@pytest.mark.parametrize("log, expected", [
    (r'{"ts": 1, "issue": "521", "actor": "developer", "phase": "red", "step": "cost a step \u2014 its title \u27e6criterion 1\u27e7", "event": "usage", "total_cost_usd": "0.30"}' '\n'
     r'{"ts": 2, "issue": "521", "actor": "verifier", "phase": "red", "step": "cost a step \u2014 its title \u27e6criterion 1\u27e7", "event": "usage", "total_cost_usd": "0.12"}' '\n'
     r'{"ts": 3, "issue": "521", "actor": "developer", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}' '\n',
     {"--steps": (0, "0.42 2\n1.00 1\n"), "cost a step — its title ⟦criterion 1⟧": (0, "0.42\n")}),
    (r'{"ts": 1, "issue": "620", "actor": "developer", "phase": "red", "step": "prints \"ok\" on success", "event": "usage", "total_cost_usd": "0.30"}' '\n'
     r'{"ts": 2, "issue": "620", "actor": "verifier", "phase": "red", "step": "prints \"ok\" on success", "event": "usage", "total_cost_usd": "0.20"}' '\n'
     r'{"ts": 3, "issue": "620", "actor": "developer", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}' '\n',
     {'prints "ok" on success': (0, "0.50\n")}),
    (r'{"ts": 1, "issue": "620", "actor": "developer", "phase": "red", "step": "a \\\"quoted\\\" path", "event": "usage", "total_cost_usd": "0.25"}' '\n'
     r'{"ts": 2, "issue": "620", "actor": "verifier", "phase": "red", "step": "a \\\"quoted\\\" path", "event": "usage", "total_cost_usd": "0.10"}' '\n'
     r'{"ts": 3, "issue": "620", "actor": "developer", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}' '\n',
     {r'a \"quoted\" path': (0, "0.35\n")}),
    (r'{"ts": 1, "issue": "620", "actor": "developer", "phase": "red", "step": "ends in a backslash \\", "event": "usage", "total_cost_usd": "0.40"}' '\n'
     r'{"ts": 2, "issue": "620", "actor": "verifier", "phase": "red", "step": "ends in a backslash \\", "event": "usage", "total_cost_usd": "0.15"}' '\n'
     r'{"ts": 3, "issue": "620", "actor": "developer", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}' '\n',
     {"ends in a backslash \\": (0, "0.55\n")}),
], ids=["em-dash-and-criterion-brackets", "double-quote", "backslash-then-double-quote", "trailing-backslash"])
def test_main_sums_a_step_title_carrying_an_em_dash_criterion_brackets_a_double_quote_or_a_backslash_to_its_usage_events_and_returns_0(log, expected, tmp_path, monkeypatch, capsys, step_cost):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(log, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    observed = {}
    for arg in expected:
        code = step_cost.main([arg])
        out, err = capsys.readouterr()
        observed[arg] = (code, out)

    assert observed == expected


QUOTED_TITLES = [
    (r'{"ts": 1, "issue": "620", "actor": "developer", "phase": "red", "step": "prints \"ok\" on success", "event": "usage", "total_cost_usd": "1.00"}' '\n'
     r'{"ts": 2, "issue": "620", "actor": "verifier", "phase": "red", "step": "prints \"ok\" on success", "event": "usage", "total_cost_usd": "0.50"}' '\n'
     r'{"ts": 3, "issue": "620", "actor": "developer", "phase": "red", "step": "prints \"err\" on failure", "event": "usage", "total_cost_usd": "1.00"}' '\n',
     {"--steps": (0, "1.50 2\n1.00 1\n")}),
    (r'{"ts": 1, "issue": "620", "actor": "developer", "phase": "red", "step": "prints \"ok\" on success", "event": "usage", "total_cost_usd": "1.00"}' '\n'
     r'{"ts": 2, "issue": "620", "actor": "developer", "phase": "red", "step": "a \\\"quoted\\\" path", "event": "usage", "total_cost_usd": "0.25"}' '\n'
     r'{"ts": 3, "issue": "620", "actor": "developer", "phase": "red", "step": "ends in a backslash \\", "event": "usage", "total_cost_usd": "0.40"}' '\n'
     r'{"ts": 4, "issue": "620", "actor": "verifier", "phase": "red", "step": "prints \"ok\" on success", "event": "usage", "total_cost_usd": "0.50"}' '\n'
     r'{"ts": 5, "issue": "620", "actor": "verifier", "phase": "red", "step": "a \\\"quoted\\\" path", "event": "usage", "total_cost_usd": "0.10"}' '\n'
     r'{"ts": 6, "issue": "620", "actor": "developer", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "2.00"}' '\n',
     {"--steps": (0, "1.50 2\n0.35 2\n0.40 1\n2.00 1\n"), 'prints "ok" on success': (0, "1.50\n"),
      r'a \"quoted\" path': (0, "0.35\n"), "ends in a backslash \\": (0, "0.40\n"), "step two": (0, "2.00\n")}),
    (r'{"ts": 1, "issue": "620", "actor": "developer", "phase": "red", "step": "prints \"ok\" on success", "event": "usage", "total_cost_usd": "1.00"}' '\n'
     r'{"ts": 2, "issue": "620", "actor": "verifier", "phase": "red", "step": "prints \"ok\" on success", "event": "usage", "total_cost_usd": "0.50"}' '\n'
     r'{"ts": 3, "issue": "620", "actor": "developer", "phase": "red", "step": "prints \"err\" on failure", "event": "usage", "total_cost_usd": "0.25"}' '\n'
     r'{"ts": 4, "issue": "620", "actor": "developer", "phase": "red", "step": "a \\\"quoted\\\" path", "event": "usage", "total_cost_usd": "0.10"}' '\n'
     r'{"ts": 5, "issue": "620", "actor": "developer", "phase": "red", "step": "ends in a backslash \\", "event": "usage", "total_cost_usd": "0.04"}' '\n',
     {"--run": (0, "1.89\n")}),
    (r'{"ts": 1, "issue": "620", "actor": "developer", "phase": "red", "step": "prints \"ok\" on success", "event": "usage", "total_cost_usd": "1.00"}' '\n'
     r'{"ts": 2, "issue": "620", "actor": "developer", "phase": "red", "step": "cost a step \u2014 its title \u27e6criterion 7\u27e7", "event": "usage", "total_cost_usd": "0.30"}' '\n'
     r'{"ts": 3, "issue": "620", "actor": "verifier", "phase": "red", "step": "cost a step \u2014 its title \u27e6criterion 7\u27e7", "event": "usage", "total_cost_usd": "0.12"}' '\n'
     r'{"ts": 4, "issue": "620", "actor": "developer", "phase": "red", "step": "step two", "event": "usage", "total_cost_usd": "1.0"}' '\n',
     {"--steps": (0, "1.00 1\n0.42 2\n1.00 1\n"), "cost a step — its title ⟦criterion 7⟧": (0, "0.42\n")}),
    (r'{"ts": 1, "issue": "620", "actor": "developer", "phase": "red", "step": "prints \"ok\" on success", "event": "usage", "total_cost_usd": "1.00"}' '\n'
     r'{"ts": 2, "issue": "620", "actor": "verifier", "phase": "red", "step": "prints \"ok\" on success", "event": "usage", "total_cost_usd": "0.50"}' '\n'
     r'{"ts": 3, "issue": "620", "actor": "developer", "phase": "red", "step": "a \\\"quoted\\\" path", "event": "usage", "total_cost_usd": "0.25"}' '\n',
     {'prints "ok"': (3, "")}),
]


@pytest.mark.parametrize("log, expected", QUOTED_TITLES, ids=[
    "steps-separate-rows-for-titles-equal-up-to-their-first-double-quote",
    "each-title-figure-equals-its-steps-row",
    "run-counts-each-quoted-title-event-once",
    "unicode-escaped-title-beside-a-quoted-one",
    "a-step-no-event-carries-exits-3"])
def test_main_keeps_titles_carrying_double_quotes_apart_in_every_call_and_matches_each_to_its_own_usage_events(log, expected, tmp_path, monkeypatch, capsys, step_cost):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "events.jsonl").write_text(log, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    observed = {}
    for arg in expected:
        code = step_cost.main([arg])
        out, err = capsys.readouterr()
        observed[arg] = (code, out)

    assert observed == expected


def test_main_sums_step_less_events_for_an_empty_argument_and_returns_2_for_an_unknown_option_two_arguments_or_a_missing_log(tmp_path, monkeypatch, capsys, step_cost):
    run = tmp_path / "run"
    (run / ".tdd").mkdir(parents=True)
    (run / ".tdd" / "events.jsonl").write_text(
        '{"ts": 1, "issue": "448", "actor": "conductor", "phase": "scope", "step": "", "event": "usage", "total_cost_usd": "0.25"}\n'
        '{"ts": 2, "issue": "448", "actor": "conductor", "phase": "scope", "event": "usage", "total_cost_usd": "0.10"}\n'
        '{"ts": 3, "issue": "448", "actor": "developer", "phase": "red", "step": "step one", "event": "usage", "total_cost_usd": "1.0"}\n')
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    observed = {}
    monkeypatch.chdir(run)
    for name, argv in (("empty-step", [""]), ("unknown-option", ["-x"]), ("two-arguments", ["step one", "--run"])):
        code = step_cost.main(argv)
        out, err = capsys.readouterr()
        observed[name] = (code, out)
    monkeypatch.chdir(elsewhere)
    code = step_cost.main(["step one"])
    out, err = capsys.readouterr()
    observed["missing-log"] = (code, out, err)

    assert observed == {
        "empty-step": (0, "0.35\n"),
        "unknown-option": (2, ""),
        "two-arguments": (2, ""),
        "missing-log": (2, "", "step-cost.sh: cannot read .tdd/events.jsonl in %s — run from the run's worktree\n" % elsewhere),
    }


def test_main_names_the_logical_pwd_not_the_symlink_resolved_path_when_the_log_is_missing(tmp_path, monkeypatch, capsys, step_cost):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real)
    monkeypatch.chdir(link)
    monkeypatch.setenv("PWD", str(link))

    code = step_cost.main(["step one"])

    out, err = capsys.readouterr()
    assert (code, out, err) == (
        2, "", "step-cost.sh: cannot read .tdd/events.jsonl in %s — run from the run's worktree\n" % link)


@pytest.mark.parametrize("pwd", [".", "/nonexistent-veri-pwd"], ids=["relative", "missing"])
def test_main_names_the_physical_directory_when_the_log_is_missing_and_pwd_is_relative_or_names_no_directory(pwd, tmp_path, monkeypatch, capsys, step_cost):
    monkeypatch.chdir(tmp_path)
    here = os.getcwd()
    monkeypatch.setenv("PWD", pwd)

    code = step_cost.main(["step one"])

    out, err = capsys.readouterr()
    assert (code, out, err) == (
        2, "", "step-cost.sh: cannot read .tdd/events.jsonl in %s — run from the run's worktree\n" % here)
