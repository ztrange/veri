"""Cases for veri/tunables.py, the one reader of VERI_* tunables."""
import importlib
import os

import pytest

ENTRY_POINTS = {
    "VERI_CONDUCTOR_CTX_BUDGET": ("veri.orchestrate", [], {}),
    "VERI_RESET_GROWTH_CONDUCTOR": ("veri.restart_conductor", ["7"], {}),
    "VERI_CONDUCTOR_STOP_TIMEOUT": ("veri.orchestrate", [], {}),
    "REVISE_BUDGET": ("veri.run_conductor", ["1"], {"VERI_BASH_MAJOR": "5"}),
    "VERI_REBASED_TIP_SUITE": ("veri.run_conductor", ["1"], {"VERI_BASH_MAJOR": "5"}),
    "VERI_BRANCH_SUITE": ("veri.run_conductor", ["1"], {"VERI_BASH_MAJOR": "5"}),
    "VERI_BASELINE_FULL_TIER": ("veri.run_conductor", ["1"], {"VERI_BASH_MAJOR": "5"}),
    "VERI_COMMENT_CHUNK": ("veri.report_cache", ["refresh"], {}),
    "VERI_KILL_POLL": ("veri.supervise", ["develop-red", "true"], {"VERI_TIMEOUT": "900"}),
}
CANDIDATES = ("abc", "-1", "0", "1.5.5", "1e3", "1e12", "nan", "inf", " 7")


def test_1313_every_tunable_in_the_readers_table_refuses_a_malformed_or_out_of_bounds_value_with_exit_2_one_line_naming_it_and_its_value_starting_nothing(
        monkeypatch, tmp_path, run_cli, fake_processes):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("VERI_") and n != "VERI_VENV"]:
        monkeypatch.delenv(name)

    refusals = {}
    assert tunables.TABLE["REVISE_BUDGET"].default == "2"
    for name, parse in tunables.TABLE.items():
        module, argv, env = ENTRY_POINTS[name]
        rejected = []
        for value in CANDIDATES:
            try:
                parse(value)
            except ValueError:
                rejected.append(value)
        assert rejected, "%s: no candidate value is refused by its parser" % name
        for value in rejected:
            for other in tunables.TABLE:
                monkeypatch.delenv(other, raising=False)
            calls = fake_processes()
            code, out, err = run_cli(importlib.import_module(module), argv, env=dict(env, **{name: value}), cwd=tmp_path)
            refusals[(name, value)] = (code, out, len(err.splitlines()), name in err, value in err,
                                       "Traceback" in err, tuple(calls))

    assert refusals
    assert set(refusals.values()) == {(2, "", 1, True, True, False, ())}


def test_2705_revise_budget_unset_resolves_to_the_default_of_2_with_no_error(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.delenv("REVISE_BUDGET", raising=False)

    assert tunables.resolve("REVISE_BUDGET") == (2, None)


def test_2841_rebased_tip_suite_set_to_a_value_but_local_or_ci_makes_run_conductor_exit_2_naming_it_and_the_value(
        monkeypatch, tmp_path, run_cli, fake_processes):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("VERI_") and n != "VERI_VENV"]:
        monkeypatch.delenv(name)
    module, argv, env = ENTRY_POINTS["VERI_REBASED_TIP_SUITE"]
    calls = fake_processes()

    code, out, err = run_cli(importlib.import_module(module), argv,
                             env=dict(env, VERI_REBASED_TIP_SUITE="bogus"), cwd=tmp_path)

    assert "VERI_REBASED_TIP_SUITE" in tunables.TABLE
    assert (code, out, len(err.splitlines()), "VERI_REBASED_TIP_SUITE" in err, "bogus" in err, tuple(calls)) == (
        2, "", 1, True, True, ())


def test_2841_rebased_tip_suite_unset_resolves_to_local_with_no_error(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.delenv("VERI_REBASED_TIP_SUITE", raising=False)

    assert tunables.resolve("VERI_REBASED_TIP_SUITE") == ("local", None)


def test_2841_rebased_tip_suite_set_to_ci_resolves_to_ci_with_no_error(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.setenv("VERI_REBASED_TIP_SUITE", "ci")

    assert tunables.resolve("VERI_REBASED_TIP_SUITE") == ("ci", None)


def test_branch_suite_set_to_a_value_but_local_or_ci_makes_run_conductor_exit_2_naming_it_and_the_value(
        monkeypatch, tmp_path, run_cli, fake_processes):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("VERI_") and n != "VERI_VENV"]:
        monkeypatch.delenv(name)
    module, argv, env = ENTRY_POINTS["VERI_BRANCH_SUITE"]
    calls = fake_processes()

    code, out, err = run_cli(importlib.import_module(module), argv,
                             env=dict(env, VERI_BRANCH_SUITE="bogus"), cwd=tmp_path)

    assert "VERI_BRANCH_SUITE" in tunables.TABLE
    assert (code, out, len(err.splitlines()), "VERI_BRANCH_SUITE" in err, "bogus" in err, tuple(calls)) == (
        2, "", 1, True, True, ())


def test_branch_suite_unset_resolves_to_local_with_no_error_and_ci_resolves_to_ci(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.delenv("VERI_BRANCH_SUITE", raising=False)
    assert tunables.resolve("VERI_BRANCH_SUITE") == ("local", None)
    monkeypatch.setenv("VERI_BRANCH_SUITE", "ci")
    assert tunables.resolve("VERI_BRANCH_SUITE") == ("ci", None)


def test_2847_baseline_full_tier_set_to_a_value_but_run_or_reuse_makes_run_conductor_exit_2_naming_it_and_the_value(
        monkeypatch, tmp_path, run_cli, fake_processes):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("VERI_") and n != "VERI_VENV"]:
        monkeypatch.delenv(name)
    module, argv, env = ENTRY_POINTS["VERI_BASELINE_FULL_TIER"]
    calls = fake_processes()

    code, out, err = run_cli(importlib.import_module(module), argv,
                             env=dict(env, VERI_BASELINE_FULL_TIER="bogus"), cwd=tmp_path)

    assert "VERI_BASELINE_FULL_TIER" in tunables.TABLE
    assert (code, out, len(err.splitlines()), "VERI_BASELINE_FULL_TIER" in err, "bogus" in err, tuple(calls)) == (
        2, "", 1, True, True, ())


def test_2847_baseline_full_tier_unset_resolves_to_reuse_with_no_error(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.delenv("VERI_BASELINE_FULL_TIER", raising=False)

    assert tunables.resolve("VERI_BASELINE_FULL_TIER") == ("reuse", None)


def test_2847_baseline_full_tier_set_to_reuse_resolves_to_reuse_with_no_error(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.setenv("VERI_BASELINE_FULL_TIER", "reuse")

    assert tunables.resolve("VERI_BASELINE_FULL_TIER") == ("reuse", None)


@pytest.mark.parametrize("raw", ["x", "Run", "reuse ", " run", "REUSE", "skip", "none", "auto", "always", "1"])
def test_2847_baseline_full_tier_set_to_any_value_but_run_or_reuse_is_refused_naming_the_value(
        monkeypatch, raw):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.setenv("VERI_BASELINE_FULL_TIER", raw)

    value, error = tunables.resolve("VERI_BASELINE_FULL_TIER")

    assert (value, error[0]) == (None, raw)


def test_2847_baseline_full_tier_set_empty_resolves_to_the_default_reuse(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.setenv("VERI_BASELINE_FULL_TIER", "")

    assert tunables.resolve("VERI_BASELINE_FULL_TIER") == ("reuse", None)


def test_3223_reset_growth_conductor_is_in_the_readers_table_defaulting_to_70000_and_refusing_zero():
    tunables = importlib.import_module("veri.tunables")

    entry = tunables.TABLE["VERI_RESET_GROWTH_CONDUCTOR"]

    assert (entry.default, entry("1"), entry("70000")) == ("70000", 1, 70000)
    with pytest.raises(ValueError):
        entry("0")


DEFAULTED = {
    "VERI_REFACTOR_BUDGET": ("5", "0", "x"),
    "VERI_ISSUE_REFACTOR_BUDGET": ("10", "0", "-1"),
    "VERI_STEP_GROWTH": ("5", "0", "1.5"),
    "VERI_NO_VERDICT_RETRIES": ("1", "010", None),
    "VERI_SKILL_EDIT_BUDGET": ("3", "1", "0"),
    "VERI_ADJUDICATE_BUDGET": ("2", "0", "-1"),
    "VERI_STUCK_RETRIES": ("1", "0", "x"),
    "VERI_HEARTBEAT": ("180", "1", "1.5"),
    "VERI_TOOL_IDLE": ("600", "1", "1e3"),
    "VERI_TIMEOUT": ("900", "1", " 7"),
    "VERI_DISPATCH_RETRY_SLEEP": ("5", "0", "x"),
    "VERI_GH_REFUSAL_RETRIES": ("3", "0", "-1"),
    "VERI_LABEL": ("ready-for-agent", "ready-for-agent:mu", None),
    "VERI_MODEL": ("", "opus", None),
    "VERI_MODEL_DEVELOPER": ("sonnet", "opus", None),
    "VERI_MODEL_VERIFIER": ("sonnet", "opus", None),
    "VERI_MODEL_REVISE": ("opus", "sonnet", None),
    "VERI_MODEL_ADJUDICATOR": ("opus", "sonnet", None),
    "VERI_MODEL_CONDUCTOR": ("opus", "sonnet", None),
}


@pytest.mark.parametrize("name", sorted(DEFAULTED))
def test_a_defaulted_tunable_states_its_one_default_and_its_parse_in_the_tunables_module(name):
    tunables = importlib.import_module("veri.tunables")
    default, good, bad = DEFAULTED[name]

    assert tunables.default(name) == default
    assert tunables.parses(name, good)
    if bad is not None:
        assert not tunables.parses(name, bad)


@pytest.mark.parametrize("name", sorted(DEFAULTED))
def test_get_reads_the_environment_and_falls_back_to_the_default_only_when_unset(monkeypatch, name):
    tunables = importlib.import_module("veri.tunables")
    default = DEFAULTED[name][0]
    monkeypatch.delenv(name, raising=False)
    assert tunables.get(name) == default
    monkeypatch.setenv(name, "")
    assert tunables.get(name) == ""
    assert tunables.get(name, unless_empty=True) == default
    monkeypatch.setenv(name, "7")
    assert tunables.get(name) == tunables.get(name, unless_empty=True) == "7"


def test_a_name_in_the_refusing_table_keeps_its_default_through_the_same_function():
    tunables = importlib.import_module("veri.tunables")

    assert (tunables.default("REVISE_BUDGET"), tunables.default("VERI_BASELINE_FULL_TIER")) == ("2", "reuse")


def test_no_name_is_defined_in_both_tables():
    tunables = importlib.import_module("veri.tunables")

    assert not set(tunables.TABLE) & set(tunables.DEFAULTED)
