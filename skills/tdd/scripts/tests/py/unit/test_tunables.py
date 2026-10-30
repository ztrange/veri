"""Cases for veri/tunables.py, the one reader of VERI_* tunables."""
import importlib
import os

import pytest

ENTRY_POINTS = {
    "VERI_CONDUCTOR_CTX_BUDGET": ("veri.orchestrate", [], {}),
    "VERI_CONDUCTOR_STOP_TIMEOUT": ("veri.orchestrate", [], {}),
    "VERI_KILL_POLL": ("veri.supervise", ["develop-red", "true"], {"VERI_TIMEOUT": "900"}),
    "REVISE_BUDGET": ("veri.run_conductor", ["7"], {"VERI_BASH_MAJOR": "5", "VERI_PYTHON_VERSION": "3.12.0"}),
}
CANDIDATES = ("abc", "-1", "0", "1.5.5", "1e3", "1e12", "nan", "inf", " 7")


def test_1313_every_tunable_in_the_readers_table_refuses_a_malformed_or_out_of_bounds_value_with_exit_2_one_line_naming_it_and_its_value_starting_nothing(
        monkeypatch, tmp_path, run_cli, fake_processes):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.chdir(tmp_path)
    for name in [n for n in os.environ if n.startswith("VERI_") and n != "VERI_VENV"]:
        monkeypatch.delenv(name)

    refusals = {}
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


def test_2705_revise_budget_is_registered_with_its_default_of_2_and_refuses_a_bad_value(monkeypatch):
    tunables = importlib.import_module("veri.tunables")
    monkeypatch.delenv("REVISE_BUDGET", raising=False)
    default = tunables.resolve("REVISE_BUDGET")
    monkeypatch.setenv("REVISE_BUDGET", "3")
    raised = tunables.resolve("REVISE_BUDGET")
    monkeypatch.setenv("REVISE_BUDGET", "lots")
    value, bad = tunables.resolve("REVISE_BUDGET")

    assert (default, raised, value, bad[0]) == ((2, None), (3, None), None, "lots")
