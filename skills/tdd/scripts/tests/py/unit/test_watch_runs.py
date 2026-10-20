"""In-process cases for veri/watch_runs.py, the module watch-runs.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def watch_runs():
    return importlib.import_module("veri.watch_runs")


def test_main_prints_exited_with_the_first_word_of_the_state_when_a_conductor_live_at_start_exits(
        monkeypatch, capsys, watch_runs):
    listings = iter([["5", "7"], ["5", "7"], ["7"]])
    waits = []
    monkeypatch.setattr(watch_runs, "live_conductors", lambda: next(listings))
    monkeypatch.setattr(watch_runs, "run_state", lambda issue: {"5": "bailed red tests-pass", "7": "running"}[issue])
    monkeypatch.setattr(watch_runs, "wait", lambda: waits.append(1))

    code = watch_runs.main([])

    assert (code, capsys.readouterr().out) == (0, "exited 5 bailed\n")
    assert len(waits) == 2
