"""In-process cases for veri/watch_runs.py, the module watch-runs.sh is a shim over."""
import importlib
import json
import subprocess

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


def test_main_returns_2_with_a_usage_line_before_any_listing_when_target_or_max_wait_is_not_a_whole_number_of_at_least_1(
        monkeypatch, capsys, watch_runs):
    listings = []

    def live_conductors():
        listings.append(1)
        raise RuntimeError("listed before validating the arguments")

    monkeypatch.setattr(watch_runs, "live_conductors", live_conductors)
    monkeypatch.setattr(watch_runs, "wait", lambda: listings.append("wait"))

    outcomes = []
    for argv in (["--target", "0"], ["--target", "-1"], ["--max-wait", "abc"], ["--max-wait", ""], ["--target"]):
        code = watch_runs.main(argv)
        captured = capsys.readouterr()
        outcomes.append((argv, code, captured.out, captured.err.lower().startswith("usage")))

    assert outcomes == [(argv, 2, "", True) for argv, *_ in outcomes]
    assert listings == []


@pytest.mark.parametrize("argv", [
    pytest.param(["--max-wiat", "3"], id="unknown-flag"),
    pytest.param(["--target", "2", "junk"], id="trailing-junk"),
    pytest.param(["--target", "2", "--target", "3"], id="repeated-flag"),
    pytest.param(["--target", "2", "--max-wait"], id="second-flag-missing-its-value"),
])
def test_main_exits_2_with_the_usage_line_before_any_listing_on_an_argument_list_outside_the_accepted_shapes_1930(
        monkeypatch, capsys, watch_runs, argv):
    listings = []

    def wait():
        raise RuntimeError("polled")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: listings.append(1) or [])
    monkeypatch.setattr(watch_runs, "solvable_issues", lambda: [], raising=False)
    monkeypatch.setattr(watch_runs, "wait", wait)

    try:
        code = watch_runs.main(argv)
    except RuntimeError:
        code = "polled"

    assert (code, capsys.readouterr().err.startswith("usage: watch-runs.sh"), listings) == (2, True, [])


@pytest.mark.parametrize("argv", [
    pytest.param(["--target", "5", "--max-wait", "3"], id="target-first"),
    pytest.param(["--max-wait", "3", "--target", "5"], id="max-wait-first"),
])
def test_main_with_target_and_max_wait_in_either_order_prints_timeout_and_returns_3_when_the_wait_elapses_before_a_slot_frees_1930(
        monkeypatch, capsys, watch_runs, argv):
    now = [100.0]
    waits = []

    def wait():
        waits.append(1)
        now[0] += 1
        if len(waits) > 10:
            raise RuntimeError("never printed timeout")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["5"])
    monkeypatch.setattr(watch_runs, "solvable_issues", lambda: [], raising=False)
    monkeypatch.setattr(watch_runs, "clock", lambda: now[0], raising=False)
    monkeypatch.setattr(watch_runs, "wait", wait)

    code = watch_runs.main(argv)

    assert (code, capsys.readouterr().out) == (3, "timeout\n")


@pytest.mark.parametrize("argv", [
    pytest.param(["--target", "2", "--max-wait", "30"], id="target-first"),
    pytest.param(["--max-wait", "30", "--target", "2"], id="max-wait-first"),
])
def test_main_with_target_and_max_wait_in_either_order_prints_slot_free_and_returns_0_when_a_slot_frees_before_the_wait_elapses_1930(
        monkeypatch, capsys, watch_runs, argv):
    now = [100.0]
    waits = []

    def wait():
        waits.append(1)
        now[0] += 1
        if len(waits) > 10:
            raise RuntimeError("never printed slot-free")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["5"])
    monkeypatch.setattr(watch_runs, "solvable_issues", lambda: ["12", "15"], raising=False)
    monkeypatch.setattr(watch_runs, "clock", lambda: now[0], raising=False)
    monkeypatch.setattr(watch_runs, "wait", wait)

    code = watch_runs.main(argv)

    assert (code, capsys.readouterr().out) == (0, "slot-free 1/2 next 12\n")


def test_main_with_target_exits_2_and_passes_on_stderr_when_solvable_issues_exits_non_zero_1930(
        monkeypatch, capsys, watch_runs):
    waits = []

    def wait():
        waits.append(1)
        if len(waits) > 3:
            raise RuntimeError("waited on after the queue read failed")

    def run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 1, stdout="", stderr="gh: not logged in\n")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: ["5"])
    monkeypatch.setattr(watch_runs.subprocess, "run", run)
    monkeypatch.setattr(watch_runs, "wait", wait)

    try:
        code = watch_runs.main(["--target", "2"])
    except RuntimeError:
        code = "waited on"

    captured = capsys.readouterr()
    assert (code, captured.out, "gh: not logged in" in captured.err) == (2, "", True)


def test_main_reports_a_conductor_live_at_start_that_vanished_from_the_run_listing_and_returns_2_1930(
        monkeypatch, capsys, watch_runs):
    listings = iter([["5", "7"], ["7"]])
    monkeypatch.setattr(watch_runs, "live_conductors", lambda: next(listings))
    monkeypatch.setattr(watch_runs, "run_state", lambda issue: "")
    monkeypatch.setattr(watch_runs, "wait", lambda: None)

    code = watch_runs.main([])

    out = capsys.readouterr().out
    assert (code, "vanished" in out and "5" in out, "exited" in out) == (2, True, False)


def test_main_with_no_flags_and_no_live_conductor_at_start_prints_nothing_to_watch_and_returns_3_without_blocking_1930(
        monkeypatch, capsys, watch_runs):
    waits = []

    def wait():
        waits.append(1)
        if len(waits) > 3:
            raise RuntimeError("blocked with nothing to watch")

    monkeypatch.setattr(watch_runs, "live_conductors", lambda: [])
    monkeypatch.setattr(watch_runs, "wait", wait)

    try:
        code = watch_runs.main([])
    except RuntimeError:
        code = "blocked"

    out = capsys.readouterr().out
    assert (code, "nothing to watch" in out) == (3, True)


def test_main_reports_vanished_and_returns_2_when_a_conductor_live_at_start_drops_out_of_the_run_listing_1930(
        monkeypatch, capsys, watch_runs):
    both = {"runs": [{"issue": 5, "state": "running"}, {"issue": 7, "state": "running"}]}
    only_7 = {"runs": [{"issue": 7, "state": "running"}]}
    documents = iter([both])
    waits = []

    def wait():
        waits.append(1)
        if len(waits) > 3:
            raise RuntimeError("never reported the vanished run")

    monkeypatch.setattr(watch_runs.status, "json_document",
                        lambda scope=None: (0, json.dumps(next(documents, only_7))))
    monkeypatch.setattr(watch_runs, "wait", wait)

    code = watch_runs.main([])

    assert (code, capsys.readouterr().out) == (2, "vanished 5\n")


def test_solvable_issues_asks_the_solvable_issues_script_beside_watch_runs_through_an_unresolved_symlinked_directory(
        monkeypatch, tmp_path):
    import importlib.util
    import pathlib
    real_scripts = pathlib.Path(__file__).resolve().parents[3]
    link = tmp_path / "scripts"
    link.symlink_to(real_scripts)
    spec = importlib.util.spec_from_file_location("watch_runs_via_symlink", link / "veri" / "watch_runs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    module.solvable_issues()

    assert calls == [[f"{link}/veri/../solvable-issues.sh", "--not-running"]]
