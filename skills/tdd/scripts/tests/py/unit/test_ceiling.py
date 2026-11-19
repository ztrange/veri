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
