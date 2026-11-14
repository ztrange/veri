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
