"""test-ceiling.sh (veri/ceiling.py): the ramp that measures the highest test-worker count with no case timeout (#4418).

Every case fakes `make test` at the process boundary: the fake reads the workers and the selection off the command and
its environment, and reports each failing case through the recorder plugin, as the real leg's controller would."""
import re
import types

import pytest

import ceiling
import ceiling_record
import pid_file

TIMEOUT = "E   Failed: Timeout (>30.0s) from pytest-timeout."
STARTED = "Wed Nov 18 10:00:00 2026"


@pytest.fixture
def make(monkeypatch, tmp_path, fake_processes):
    """Answers `make test` through fake_processes: `outcome(workers, tests)` returns the (nodeid, failure text) of each
    failing case, or a bare exit code. Each call is kept as (workers, tests, argv)."""
    calls = []
    units = []
    state = {"outcome": lambda workers, tests: [], "unit": lambda workers: 0}

    def run(line, env=None, **kwargs):
        argv = fake.argvs[-1]
        workers = int(env["VERI_PYTEST_WORKERS"])
        if argv[-1] == "unit":
            units.append(workers)
            return state["unit"](workers), "", ""
        tests = [arg[len("TESTS="):] for arg in argv if arg.startswith("TESTS=")]
        calls.append((workers, tests, argv))
        outcome = state["outcome"](workers, tests)
        if isinstance(outcome, int):
            return outcome, "", ""
        with monkeypatch.context() as patch:
            patch.setenv("VERI_CEILING_RECORD", env["VERI_CEILING_RECORD"])
            for nodeid, text in outcome:
                ceiling_record.pytest_runtest_logreport(
                    types.SimpleNamespace(nodeid=nodeid, failed=True, when="call", longreprtext=text))
        return (1 if outcome else 0), "", ""

    fake = fake_processes.answers({"make": run})
    monkeypatch.setattr(ceiling, "commit", lambda: "0123456789abcdef0123456789abcdef01234567")
    monkeypatch.setattr(ceiling.os, "cpu_count", lambda: 6)
    monkeypatch.setattr(pid_file, "ps_field", lambda field, pid: STARTED)
    monkeypatch.setenv("VERI_TEST_CEILING_FILE", str(tmp_path / "ceiling-record"))

    def given(outcome):
        state["outcome"] = outcome

    def unit(outcome):
        state["unit"] = outcome

    return types.SimpleNamespace(calls=calls, given=given, units=units, unit=unit)


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


def test_exit_0_replaces_the_record_whole_through_a_temporary_file_with_the_ceiling_first(make, run_cli,
                                                                                          tmp_path, monkeypatch):
    record = tmp_path / "ceiling-record"
    record.write_text("8\nan earlier record\nwith more lines\nthan\nthe new\none\nwill\nhave\n")
    ticks = iter(range(0, 10000, 100))
    monkeypatch.setattr(ceiling, "clock", lambda: next(ticks))
    monkeypatch.setattr(ceiling.os, "getloadavg", lambda: (1.5, 2.25, 3.0))
    replaced = []
    real_replace = ceiling.os.replace
    monkeypatch.setattr(ceiling.os, "replace", lambda src, dst: replaced.append((src, dst)) or real_replace(src, dst))
    make.given(lambda workers, tests: [(SLOW, TIMEOUT)] if workers == 6 and not tests else [])

    code, out, err = run_cli(ceiling, [])

    assert code == 0, err
    assert "ceiling: 4 workers" in out
    lines = record.read_text().splitlines()
    assert lines[0] == "4"
    assert re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d.*", lines[1])
    assert lines[2:7] == ["0123456789abcdef0123456789abcdef01234567", "1.50 2.25 3.00", "2 100 0", "4 100 0", "6 100 1"]
    assert [dst for _, dst in replaced] == [str(record)]
    assert ceiling.os.path.dirname(replaced[0][0]) == str(tmp_path)
    assert sorted(path.name for path in tmp_path.iterdir() if "ceiling" in path.name) == ["ceiling-record"]


EARLIER = "8\nan earlier record\n"


@pytest.mark.parametrize("outcome, exit_code", [
    (lambda workers, tests: [(SLOW, TIMEOUT)] if workers == 2 and not tests else [], 1),
    (lambda workers, tests: [(RED, "E   assert 1 == 2")] if workers == 4 else [], 2),
    (lambda workers, tests: [(SLOW, TIMEOUT)] if workers == 4 or tests else [], 2),
])
def test_exit_1_and_exit_2_leave_an_earlier_record_unchanged(make, run_cli, tmp_path, outcome, exit_code):
    record = tmp_path / "ceiling-record"
    record.write_text(EARLIER)
    make.given(outcome)

    code, _, _ = run_cli(ceiling, [])

    assert code == exit_code
    assert record.read_text() == EARLIER


def test_a_record_that_cannot_be_renamed_into_place_leaves_the_earlier_one_and_no_temporary_file(make, run_cli,
                                                                                                tmp_path, monkeypatch):
    record = tmp_path / "ceiling-record"
    record.write_text(EARLIER)

    def refuse(src, dst):
        raise OSError("refused")

    monkeypatch.setattr(ceiling.os, "replace", refuse)

    code, _, err = run_cli(ceiling, ["--max", "2"])

    assert code == 2
    assert "refused" in err
    assert record.read_text() == EARLIER
    assert sorted(path.name for path in tmp_path.iterdir() if "ceiling" in path.name) == ["ceiling-record"]


def capped(text):
    """Writes <text> to the cap file the hermetic fixture points VERI_TEST_CAP_FILE at; returns its path."""
    path = ceiling.os.environ["VERI_TEST_CAP_FILE"]
    with open(path, "w") as f:
        f.write(text)
    return path


@pytest.mark.parametrize("cap, argv, steps, bound", [
    ("4\n", [], [2, 4], "the cap file"), ("5\n", [], [2, 4, 5], "the cap file"), ("8\n", [], [2, 4, 6], "the logical cores"),
    ("8\n", ["--max", "3"], [2, 3], "--max 3"), ("3\n", ["--max", "5"], [2, 3], "the cap file"),
    ("2\n", [], [2], "the cap file"), ("3\n", ["--max", "3"], [2, 3], "the cap file"), ("6\n", [], [2, 4, 6], "the cap file"),
], ids=["cap-4", "cap-5-odd", "cores", "max-3-odd", "cap-below-max", "cap-2-the-least", "cap-ties-max", "cap-ties-cores"])
def test_4457_with_a_cap_the_ramp_runs_up_to_the_least_of_the_cores_max_and_the_cap_an_odd_top_included_and_names_that_bound(
        make, run_cli, cap, argv, steps, bound):
    path = capped(cap)
    code, out, err = run_cli(ceiling, argv)

    assert (code, [workers for workers, _, _ in make.calls], "ceiling: %d workers" % steps[-1] in out, bound in out,
            (path in out) == (bound == "the cap file")) == (0, steps, True, True, True), (out, err)


def test_4457_with_a_cap_a_ramp_stopped_by_a_load_timeout_names_no_bound(make, run_cli):
    capped("6\n")
    make.given(lambda workers, tests: [(SLOW, TIMEOUT)] if workers == 4 and not tests else [])
    code, out, err = run_cli(ceiling, [])

    assert (code, [workers for workers, _, _ in make.calls], out.splitlines()[0].startswith("ceiling: 2 workers"), "bound" in out, "stopped" in out) == (
        0, [2, 4, 1], True, False, False), (out, err)


@pytest.mark.parametrize("cap", ["six\n", "1\n", "", "a directory"])
def test_4457_a_cap_file_the_ramp_cannot_use_is_one_stderr_line_naming_it_and_the_ramp_runs_as_with_no_cap(make, run_cli, cap):
    path = ceiling.os.environ["VERI_TEST_CAP_FILE"]
    if cap == "a directory":
        ceiling.os.mkdir(path)
    else:
        capped(cap)
    code, out, err = run_cli(ceiling, [])

    assert (code, [workers for workers, _, _ in make.calls], len(err.splitlines()), path in err, "bound" in out) == (
        0, [2, 4, 6], 1, True, False), (out, err)


def test_4456_a_ramp_that_found_a_ceiling_runs_one_registered_make_unit_after_it_and_records_both_idle_durations(
        make, run_cli, tmp_path, monkeypatch):
    record = tmp_path / "ceiling-record"
    legs = tmp_path / "legs"
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    ticks = iter([0, 300, 300, 700, 700, 1300, 1300, 1342])
    monkeypatch.setattr(ceiling, "clock", lambda: next(ticks))
    seen = []
    make.unit(lambda workers: seen.append(registry(legs)) or 0)
    make.given(lambda workers, tests: [(SLOW, TIMEOUT)] if workers == 6 and not tests else [])

    code, out, err = run_cli(ceiling, [])

    lines = record.read_text().splitlines()
    assert (code, make.units, seen, lines[0], lines[-3:], registry(legs)) == (
        0, [4], [{str(ceiling.os.getpid()): "4\n%s\n" % STARTED}], "4", ["6 600 1", "idle all 400", "idle fast 42"], {}), err


def test_4456_a_red_make_unit_after_the_ramp_is_exit_2_naming_it_and_leaves_the_earlier_record(make, run_cli, tmp_path):
    record = tmp_path / "ceiling-record"
    record.write_text(EARLIER)
    make.unit(lambda workers: 1)

    code, out, err = run_cli(ceiling, [])

    assert (code, "make unit" in err, "exited 1" in err, record.read_text(), "ceiling:" in out) == (
        2, True, True, EARLIER, False), err
