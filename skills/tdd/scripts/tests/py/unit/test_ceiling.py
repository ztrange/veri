"""test-ceiling.sh (veri/ceiling.py): the ramp that measures the highest test-worker count with no case timeout (#4418).

Every case fakes `make test` at the process boundary: the fake reads the workers and the selection off the command and
its environment, and reports each failing case through the recorder plugin, as the real leg's controller would."""
import subprocess
import types

import pytest

import ceiling
import ceiling_record
import pid_file

TIMEOUT = "E   Failed: Timeout (>30.0s) from pytest-timeout."
STARTED = "Wed Nov 18 10:00:00 2026"


@pytest.fixture
def make(monkeypatch, tmp_path):
    """Swaps `make test` for a fake: `outcome(workers, tests)` returns the (nodeid, failure text) of each failing case,
    or a bare exit code. Each call is kept as (workers, tests, argv)."""
    calls = []
    state = {"outcome": lambda workers, tests: []}

    def run(argv, env=None, **kwargs):
        workers = int(env["VERI_PYTEST_WORKERS"])
        tests = [arg[len("TESTS="):] for arg in argv if arg.startswith("TESTS=")]
        calls.append((workers, tests, argv))
        outcome = state["outcome"](workers, tests)
        if isinstance(outcome, int):
            return subprocess.CompletedProcess(argv, outcome)
        with monkeypatch.context() as patch:
            patch.setenv("VERI_CEILING_RECORD", env["VERI_CEILING_RECORD"])
            for nodeid, text in outcome:
                ceiling_record.pytest_runtest_logreport(
                    types.SimpleNamespace(nodeid=nodeid, failed=True, when="call", longreprtext=text))
        return subprocess.CompletedProcess(argv, 1 if outcome else 0)

    monkeypatch.setattr(ceiling.subprocess, "run", run)
    monkeypatch.setattr(ceiling, "commit", lambda: "0123456789abcdef0123456789abcdef01234567")
    monkeypatch.setattr(ceiling.os, "cpu_count", lambda: 6)
    monkeypatch.setattr(pid_file, "ps_field", lambda field, pid: STARTED)
    monkeypatch.setenv("VERI_TEST_CEILING_FILE", str(tmp_path / "ceiling-record"))

    def given(outcome):
        state["outcome"] = outcome

    return types.SimpleNamespace(calls=calls, given=given)


def test_every_step_green_ramps_make_test_at_2_4_6_up_to_the_logical_cores_and_prints_the_top_step(make, run_cli):
    code, out, err = run_cli(ceiling, [])

    assert code == 0, err
    assert [workers for workers, _, _ in make.calls] == [2, 4, 6]
    assert all(tests == [] and argv[0] == "make" and argv[-1] == "test" for _, tests, argv in make.calls)
    assert "ceiling: 6 workers" in out


@pytest.mark.parametrize("bound, steps", [("5", [2, 4]), ("2", [2]), ("8", [2, 4, 6, 8])])
def test_max_ends_the_ramp_at_the_highest_even_step_not_above_it(make, run_cli, bound, steps):
    code, out, err = run_cli(ceiling, ["--max", bound])

    assert code == 0, err
    assert [workers for workers, _, _ in make.calls] == steps
    assert "ceiling: %d workers" % steps[-1] in out


@pytest.mark.parametrize("argv", [["--max"], ["--max", "x"], ["--max", "1"], ["--max", "0"], ["--fast"],
                                  ["--max", "4", "extra"]])
def test_a_bad_argument_is_exit_2_with_the_usage_line_and_runs_no_suite(make, run_cli, argv):
    code, out, err = run_cli(ceiling, argv)

    assert code == 2
    assert "usage: test-ceiling.sh [--max <n>]" in err
    assert make.calls == []


SLOW = "skills/tdd/scripts/tests/py/test_x.py::test_slow"


def test_a_case_that_times_out_under_load_and_passes_alone_stops_the_ramp_at_the_last_step_with_none(make, run_cli):
    make.given(lambda workers, tests: [(SLOW, TIMEOUT)] if workers == 4 and not tests else [])

    code, out, err = run_cli(ceiling, [])

    assert code == 0, err
    assert [(workers, tests) for workers, tests, _ in make.calls] == [(2, []), (4, []), (1, [SLOW])]
    assert "ceiling: 2 workers" in out


def test_a_case_that_times_out_alone_too_is_exit_2_naming_it_as_hung(make, run_cli):
    make.given(lambda workers, tests: [(SLOW, TIMEOUT)] if workers == 4 or tests else [])

    code, out, err = run_cli(ceiling, [])

    assert code == 2
    assert [(workers, tests) for workers, tests, _ in make.calls] == [(2, []), (4, []), (1, [SLOW])]
    assert "hung" in err and SLOW in err
    assert "ceiling:" not in out


RED = "skills/tdd/scripts/tests/py/test_x.py::test_red"


def test_a_case_failing_other_than_by_its_timeout_is_exit_2_naming_it_with_no_re_run(make, run_cli):
    make.given(lambda workers, tests: [(RED, "E   assert 1 == 2")] if workers == 4 else [])

    code, out, err = run_cli(ceiling, [])

    assert code == 2
    assert [(workers, tests) for workers, tests, _ in make.calls] == [(2, []), (4, [])]
    assert RED in err
    assert "ceiling:" not in out


def test_a_timed_out_case_failing_alone_other_than_by_its_timeout_is_exit_2_naming_it(make, run_cli):
    make.given(lambda workers, tests: [(SLOW, TIMEOUT if not tests else "E   assert 1 == 2")] if workers == 4 or tests else [])

    code, out, err = run_cli(ceiling, [])

    assert code == 2
    assert SLOW in err and "failed alone" in err
    assert "ceiling:" not in out


def test_the_recorder_writes_only_a_failed_report_and_only_outside_an_xdist_worker(monkeypatch, tmp_path):
    record = tmp_path / "record"
    monkeypatch.setenv("VERI_CEILING_RECORD", str(record))
    report = lambda nodeid, failed: types.SimpleNamespace(nodeid=nodeid, failed=failed, when="call", longreprtext=TIMEOUT)

    ceiling_record.pytest_runtest_logreport(report("a::passed", False))
    with monkeypatch.context() as patch:
        patch.setenv("PYTEST_XDIST_WORKER", "gw0")
        ceiling_record.pytest_runtest_logreport(report("a::in_worker", True))
    ceiling_record.pytest_runtest_logreport(report("a::failed", True))

    assert ceiling.failures(str(record)) == {"a::failed": True}


def test_a_load_timeout_at_2_workers_is_exit_1_no_ceiling_of_at_least_2(make, run_cli):
    make.given(lambda workers, tests: [(SLOW, TIMEOUT)] if workers == 2 and not tests else [])

    code, out, err = run_cli(ceiling, [])

    assert code == 1, err
    assert [(workers, tests) for workers, tests, _ in make.calls] == [(2, []), (1, [SLOW])]
    assert "no ceiling of at least 2" in err
    assert "ceiling:" not in out


@pytest.mark.parametrize("exit_code", [1, 2])
def test_a_suite_run_exiting_non_zero_with_no_failed_case_recorded_is_exit_2_naming_its_code(make, run_cli, exit_code):
    make.given(lambda workers, tests: exit_code if workers == 4 else [])

    code, out, err = run_cli(ceiling, [])

    assert code == 2
    assert [workers for workers, _, _ in make.calls] == [2, 4]
    assert "make test exited %d at 4 workers" % exit_code in err
    assert "ceiling:" not in out


def test_a_re_run_alone_exiting_non_zero_with_no_failed_case_recorded_is_exit_2_naming_it(make, run_cli):
    make.given(lambda workers, tests: 2 if tests else [(SLOW, TIMEOUT)] if workers == 4 else [])

    code, out, err = run_cli(ceiling, [])

    assert code == 2
    assert "make test exited 2 running %s alone" % SLOW in err
    assert "ceiling:" not in out


def registry(legs):
    return {path.name: path.read_text() for path in legs.iterdir()} if legs.is_dir() else {}


def test_each_step_registers_its_workers_in_the_legs_registry_for_its_duration_re_runs_included(make, run_cli,
                                                                                                tmp_path, monkeypatch):
    legs = tmp_path / "legs"
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    seen = []
    make.given(lambda workers, tests: seen.append(registry(legs)) or ([(SLOW, TIMEOUT)] if workers == 4 and not tests else []))

    code, out, err = run_cli(ceiling, [])

    assert code == 0, err
    me = str(ceiling.os.getpid())
    assert seen == [{me: "2\n%s\n" % STARTED}, {me: "4\n%s\n" % STARTED}, {me: "4\n%s\n" % STARTED}]
    assert registry(legs) == {}


def test_a_step_with_no_answer_still_removes_its_registry_entry(make, run_cli, tmp_path, monkeypatch):
    legs = tmp_path / "legs"
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    make.given(lambda workers, tests: [(RED, "E   assert 1 == 2")])

    code, _, _ = run_cli(ceiling, [])

    assert code == 2
    assert registry(legs) == {}


def test_a_step_waits_with_one_stderr_line_naming_the_other_live_legs_until_none_is_registered(make, run_cli,
                                                                                                 tmp_path, monkeypatch):
    legs = tmp_path / "legs"
    legs.mkdir()
    other = legs / str(ceiling.os.getppid())
    other.write_text("3\n%s\n" % STARTED)
    naps = []

    def nap(seconds):
        naps.append(seconds)
        if len(naps) == 2:
            other.unlink()

    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    monkeypatch.setattr(ceiling, "sleep", nap)
    seen = []
    make.given(lambda workers, tests: seen.append(sorted(registry(legs))) or [])

    code, out, err = run_cli(ceiling, ["--max", "2"])

    assert code == 0, err
    assert len(naps) == 2
    assert seen == [[str(ceiling.os.getpid())]]
    waits = [line for line in err.splitlines() if "waiting" in line]
    assert len(waits) == 1 and str(ceiling.os.getppid()) in waits[0] and "3 workers" in waits[0]
