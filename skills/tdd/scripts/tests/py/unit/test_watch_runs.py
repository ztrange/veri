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


def test_main_with_target_prints_slot_free_with_the_first_solvable_issue_when_fewer_than_target_are_live(
        monkeypatch, capsys, watch_runs):
    waits = []

    def wait():
        waits.append(1)
        if len(waits) > 3:
            raise RuntimeError("never printed slot-free")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["5"])
    monkeypatch.setattr(watch_runs, "solvable_issues", lambda: ["12", "15"], raising=False)
    monkeypatch.setattr(watch_runs, "wait", wait)

    code = watch_runs.main(["--target", "2"])

    assert (code, capsys.readouterr().out) == (0, "slot-free 1/2 next 12\n")


def test_main_with_max_wait_prints_timeout_and_returns_3_when_nothing_actionable_happens_within_the_wait(
        monkeypatch, capsys, watch_runs):
    now = [100.0]
    waits = []

    def wait():
        waits.append(1)
        now[0] += 4
        if len(waits) > 10:
            raise RuntimeError("never printed timeout")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["5"])
    monkeypatch.setattr(watch_runs, "clock", lambda: now[0], raising=False)
    monkeypatch.setattr(watch_runs, "wait", wait)

    code = watch_runs.main(["--max-wait", "10"])

    assert (code, capsys.readouterr().out) == (3, "timeout\n")


def test_main_prints_nothing_across_polls_in_which_no_conductor_exits_and_no_slot_frees(
        monkeypatch, capsys, watch_runs):
    listings = iter([["5", "7"]] * 5 + [["7"]])
    printed_during_waits = []

    def wait():
        printed_during_waits.append(capsys.readouterr().out)

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: next(listings))
    monkeypatch.setattr(watch_runs, "run_state", lambda issue: "done")
    monkeypatch.setattr(watch_runs, "wait", wait)

    code = watch_runs.main([])

    assert (code, printed_during_waits, capsys.readouterr().out) == (0, [""] * 5, "exited 5 done\n")
