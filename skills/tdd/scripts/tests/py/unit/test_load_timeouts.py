"""In-process cases for tests/leg/load_timeouts.py, the leg's plugin that records timed-out cases machine-wide and
lowers T on a load timeout (PRD 036.7), driven through the leg with pytest.main faked."""
import importlib
import json
import os
import sys
import time
import types

import pytest


TIMEOUT = "E   Failed: Timeout (>30.0s) from pytest-timeout."
SELF_STARTED = "Wed Nov 18 08:00:00 2026"


@pytest.fixture
def pytest_leg():
    return importlib.import_module("pytest_leg")


@pytest.fixture
def machine(monkeypatch, fake_processes):
    """A 16-core Linux machine outside any xdist worker whose ceiling record is <n>; ps answers this process's start."""
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    fake_processes.answers({"ps -o lstart= -p %d" % os.getpid(): (0, SELF_STARTED + "\n", "")},
                           default=(1, "", ""), exact=True)

    def measured(n):
        with open(os.environ["VERI_TEST_CEILING_FILE"], "w") as f:
            f.write("%d\n2026-11-19\n" % n)
    return measured


def leg_env(**extra):
    return {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", **extra}


def timing_out(monkeypatch, *nodeids):
    """Fakes pytest.main: its first pass reports each of <nodeids> failed by its per-case timeout to the load_timeouts
    plugin, when the leg named that plugin in PYTEST_PLUGINS, as pytest would dispatch the hook; it exits 1."""
    passes = []

    def run(args):
        passes.append(args)
        if len(passes) == 1 and "load_timeouts" in os.environ.get("PYTEST_PLUGINS", "").split(","):
            plugin = importlib.import_module("load_timeouts")
            for nodeid in nodeids:
                plugin.pytest_runtest_logreport(types.SimpleNamespace(nodeid=nodeid, failed=True, when="call", longreprtext=TIMEOUT))
        return pytest.ExitCode.TESTS_FAILED
    monkeypatch.setattr(pytest, "main", run)


def test_a_leg_that_claimed_its_workers_appends_epoch_pid_test_file_node_id_and_workers_per_timed_out_case_and_records_a_case_timeout_event(pytest_leg, run_cli, monkeypatch, tmp_path, machine):
    machine(6)
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    nodeid = "tests/py/unit/test_x.py::test_slow"
    timing_out(monkeypatch, nodeid)
    before = int(time.time())
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(), cwd=str(tree))[0]
    after = int(time.time())
    path = os.environ["VERI_TEST_TIMEOUTS_FILE"]
    lines = open(path).read().splitlines() if os.path.exists(path) else []
    fields = [line.split(" ") for line in lines]
    journal = tree / ".tdd" / "events.jsonl"
    events = [(e["nodeid"], e["workers"]) for e in map(json.loads, journal.read_text().splitlines() if journal.exists() else [])
              if e["event"] == "case-timeout"]

    assert (code, [f[1:] for f in fields], [before <= int(f[0]) <= after for f in fields], events) == (
        1, [[str(os.getpid()), "tests/py/unit/test_x.py", nodeid, "6"]], [True], [(nodeid, "6")])


def test_a_leg_run_with_veri_pytest_workers_exported_appends_nothing_to_the_timeouts_file_and_lowers_nothing(pytest_leg, run_cli, monkeypatch, tmp_path, machine):
    machine(6)
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    timing_out(monkeypatch, "tests/py/unit/test_x.py::test_slow", "tests/py/unit/test_y.py::test_slow")
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_WORKERS="4"), cwd=str(tree))[0]
    journal = tree / ".tdd" / "events.jsonl"
    events = [e["event"] for e in map(json.loads, journal.read_text().splitlines() if journal.exists() else [])]

    assert (code, os.path.exists(os.environ["VERI_TEST_TIMEOUTS_FILE"]), open(os.environ["VERI_TEST_CEILING_FILE"]).read(),
            [e for e in events if e in ("case-timeout", "t-lowered")]) == (1, False, "6\n2026-11-19\n", [])


def test_a_timeout_appended_while_the_timeouts_file_holds_another_test_files_line_within_the_window_writes_the_load_file_through_a_temporary_file_with_t_minus_2_and_the_time(pytest_leg, run_cli, monkeypatch, tmp_path, machine):
    machine(6)
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    with open(os.environ["VERI_TEST_TIMEOUTS_FILE"], "w") as f:
        f.write("%d 4242 tests/py/unit/test_y.py tests/py/unit/test_y.py::test_other 6\n" % (time.time() - 60))
    load = os.environ["VERI_TEST_LOAD_FILE"]
    replaced = []
    real_replace = os.replace
    monkeypatch.setattr(os, "replace", lambda src, dst: (replaced.append(os.fspath(dst)), real_replace(src, dst))[1])
    timing_out(monkeypatch, "tests/py/unit/test_x.py::test_slow")
    before = int(time.time())
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(), cwd=str(tree))[0]
    after = int(time.time())
    lines = open(load).read().splitlines() if os.path.exists(load) else []

    assert (code, lines[:1], [before <= int(line) <= after for line in lines[1:]], load in replaced) == (1, ["4"], [True], True)


def test_timeouts_from_one_test_file_only_however_many_write_no_load_file(pytest_leg, run_cli, monkeypatch, tmp_path, machine):
    machine(6)
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    with open(os.environ["VERI_TEST_TIMEOUTS_FILE"], "w") as f:
        f.write("%d 4242 tests/py/unit/test_x.py tests/py/unit/test_x.py::test_other 6\n" % (time.time() - 60))
    timing_out(monkeypatch, *["tests/py/unit/test_x.py::test_slow_%d" % n for n in range(5)])
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(), cwd=str(tree))[0]

    assert (code, len(open(os.environ["VERI_TEST_TIMEOUTS_FILE"]).read().splitlines()),
            os.path.exists(os.environ["VERI_TEST_LOAD_FILE"])) == (1, 6, False)


def test_a_line_older_than_veri_load_window_seconds_does_not_count_toward_a_load_timeout(pytest_leg, run_cli, monkeypatch, tmp_path, machine):
    machine(6)
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    with open(os.environ["VERI_TEST_TIMEOUTS_FILE"], "w") as f:
        f.write("%d 4242 tests/py/unit/test_y.py tests/py/unit/test_y.py::test_other 6\n" % (time.time() - 120))
    timing_out(monkeypatch, "tests/py/unit/test_x.py::test_slow")
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_LOAD_WINDOW="60"), cwd=str(tree))[0]

    assert (code, os.path.exists(os.environ["VERI_TEST_LOAD_FILE"])) == (1, False)


def test_veri_load_window_defaults_to_600_seconds(pytest_leg, run_cli, monkeypatch, tmp_path, machine):
    machine(6)
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    with open(os.environ["VERI_TEST_TIMEOUTS_FILE"], "w") as f:
        f.write("%d 4242 tests/py/unit/test_y.py tests/py/unit/test_y.py::test_old 6\n" % (time.time() - 660))
    timing_out(monkeypatch, "tests/py/unit/test_x.py::test_slow")
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(), cwd=str(tree))[0]

    assert (code, os.path.exists(os.environ["VERI_TEST_LOAD_FILE"])) == (1, False)


def other_file_timed_out(seconds_ago=60):
    with open(os.environ["VERI_TEST_TIMEOUTS_FILE"], "a") as f:
        f.write("%d 4242 tests/py/unit/test_y.py tests/py/unit/test_y.py::test_other 6\n" % (time.time() - seconds_ago))


def test_a_lowering_never_writes_a_t_below_2(pytest_leg, run_cli, monkeypatch, tmp_path, machine):
    machine(3)
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    other_file_timed_out()
    timing_out(monkeypatch, "tests/py/unit/test_x.py::test_slow")
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(), cwd=str(tree))[0]
    load = os.environ["VERI_TEST_LOAD_FILE"]

    assert (code, open(load).read().splitlines()[:1] if os.path.exists(load) else None) == (1, ["2"])


@pytest.mark.parametrize("held, expected", [("3\n1763539200\n", 3), ("9\n1763539200\n", 6), ("2\n", 2),
                                            ("1\n1763539200\n", 6), ("three\n", 6), ("", 6)])
def test_while_the_load_file_holds_a_whole_number_of_at_least_2_budget_is_the_lesser_of_t_without_it_and_that_number_and_anything_else_is_ignored(pytest_leg, machine, held, expected):
    machine(6)
    with open(os.environ["VERI_TEST_LOAD_FILE"], "w") as f:
        f.write(held)

    assert pytest_leg.budget()[0] == expected


def test_the_load_file_lowers_t_below_the_cap_file_too(pytest_leg, machine):
    machine(8)
    with open(os.environ["VERI_TEST_CAP_FILE"], "w") as f:
        f.write("6\n")
    with open(os.environ["VERI_TEST_LOAD_FILE"], "w") as f:
        f.write("4\n1763539200\n")

    assert pytest_leg.budget()[0] == 4


def test_a_load_timeout_within_veri_load_window_seconds_of_the_lowering_on_record_lowers_nothing_more(pytest_leg, run_cli, monkeypatch, tmp_path, machine):
    machine(6)
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    record = "4\n%d\n" % (time.time() - 60)
    with open(os.environ["VERI_TEST_LOAD_FILE"], "w") as f:
        f.write(record)
    other_file_timed_out()
    timing_out(monkeypatch, "tests/py/unit/test_x.py::test_slow")
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(), cwd=str(tree))[0]

    assert (code, open(os.environ["VERI_TEST_LOAD_FILE"]).read()) == (1, record)


def test_a_load_timeout_past_veri_load_window_seconds_of_the_lowering_on_record_lowers_again(pytest_leg, run_cli, monkeypatch, tmp_path, machine):
    machine(8)
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    with open(os.environ["VERI_TEST_LOAD_FILE"], "w") as f:
        f.write("6\n%d\n" % (time.time() - 700))
    other_file_timed_out()
    timing_out(monkeypatch, "tests/py/unit/test_x.py::test_slow")
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(), cwd=str(tree))[0]

    assert (code, open(os.environ["VERI_TEST_LOAD_FILE"]).read().splitlines()[:1]) == (1, ["4"])
