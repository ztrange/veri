"""In-process cases for tests/leg/pytest_leg.py, the launcher that makes the pytest leg's refusals and then runs pytest."""
import importlib
import os
import sys

import pytest



@pytest.fixture
def pytest_leg():
    return importlib.import_module("pytest_leg")


def leg_env(**extra):
    """The env a case hands the launcher to pass its three importable checks, plus the case's own variables."""
    return {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", **extra}


def without_selection(args):
    return importlib.import_module("pytest_leg").split_marks(args)[0]


def test_the_leg_and_its_four_plugins_live_under_tests_leg_while_the_modules_launches_share_stay_in_veri_4051(pytest_leg):
    """PRD 025.16 PL1: veri/ holds no test-runner code; the leg is loaded from skills/tdd/scripts/tests/leg/."""
    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    leg = ["pytest_leg", "network_guard", "small_case_guard", "serial_seen", "private_tmp_path"]
    shared = ["full_run_lock", "launch_floor", "tunables"]
    where = {name: sorted(d for d in ("veri", os.path.join("tests", "leg"))
                          if os.path.isfile(os.path.join(scripts, d, name + ".py"))) for name in leg + shared}

    assert (where, os.path.dirname(os.path.realpath(pytest_leg.__file__))) == (
        {**{name: [os.path.join("tests", "leg")] for name in leg}, **{name: ["veri"] for name in shared}},
        os.path.join(os.path.realpath(scripts), "tests", "leg"))


def test_an_interpreter_below_the_floor_exits_2_naming_the_floor_the_interpreter_and_its_version(pytest_leg, run_cli):
    code, out, err = run_cli(pytest_leg, [], env={"VERI_PYTHON_VERSION": "3.11.9"})
    assert (code, out, err) == (
        2,
        "",
        "veri needs Python 3.12 or newer for the suites under skills/tdd/scripts/tests/py/; %s is version 3.11.9.\n"
        % sys.executable,
    )


def test_an_interpreter_that_cannot_import_pytest_exits_2_naming_pytest_the_interpreter_and_make_install_dev(pytest_leg, run_cli):
    code, out, err = run_cli(pytest_leg, [], env={"VERI_PYTEST_IMPORTABLE": "0"})
    assert (code, out, err) == (
        2,
        "",
        "veri needs pytest for the suites under skills/tdd/scripts/tests/py/; %s cannot import pytest. "
        "Install it with `make install-dev`.\n" % sys.executable,
    )


def test_an_interpreter_that_can_import_pytest_but_not_pytest_timeout_exits_2_naming_pytest_timeout_the_interpreter_and_make_install_dev(pytest_leg, run_cli):
    code, out, err = run_cli(pytest_leg, [], env={"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "0"})
    assert (code, out, err) == (
        2,
        "",
        "veri needs pytest-timeout for the suites under skills/tdd/scripts/tests/py/; %s cannot import pytest_timeout. "
        "Install it with `make install-dev`.\n" % sys.executable,
    )


def test_an_interpreter_that_can_import_pytest_and_pytest_timeout_but_not_xdist_exits_2_naming_pytest_xdist_the_interpreter_and_make_install_dev(pytest_leg, run_cli, monkeypatch):
    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    code, out, err = run_cli(pytest_leg, [], env={"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "0"})
    assert (code, out, err) == (
        2,
        "",
        "veri needs pytest-xdist for the suites under skills/tdd/scripts/tests/py/; %s cannot import xdist. "
        "Install it with `make install-dev`.\n" % sys.executable,
    )


def test_a_worker_count_that_is_not_a_whole_number_of_at_least_1_exits_2_naming_the_variable_and_the_value_before_pytest_runs(pytest_leg, run_cli, monkeypatch):
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(list(args)) or pytest.ExitCode.OK)
    for value in ("0", "-2", "two", "1.5"):
        code, out, err = run_cli(pytest_leg, [], env=leg_env(VERI_PYTEST_WORKERS=value))
        assert (code, out) == (2, ""), value
        assert "VERI_PYTEST_WORKERS" in err and value in err, value
    assert calls == []


def test_4254_an_idle_window_that_is_not_a_whole_number_of_at_least_1_set_but_empty_included_exits_2_in_one_line_naming_it_before_pytest_runs(pytest_leg, run_cli, monkeypatch):
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(list(args)) or pytest.ExitCode.OK)
    for value in ("0", "-2", "two", "1.5", "", "05x"):
        code, out, err = run_cli(pytest_leg, [], env=leg_env(VERI_PYTEST_WORKERS="1", VERI_PYTEST_IDLE=value))
        assert (code, out, len(err.splitlines())) == (2, "", 1), (value, err)
        assert "VERI_PYTEST_IDLE" in err and value in err, value
    assert calls == []


def test_4254_the_idle_window_is_a_tunable_whose_default_1200_outlasts_the_longest_timeout_mark_900(pytest_leg):
    tunables = importlib.import_module("veri.tunables")
    assert tunables.TUNABLES["VERI_PYTEST_IDLE"].default == "1200"


def test_past_its_checks_the_launcher_runs_pytest_on_its_arguments_and_exits_1_for_a_status_that_is_not_ok(pytest_leg, run_cli, monkeypatch):
    calls = []

    def spy(args):
        calls.append(list(args))
        return pytest.ExitCode.NO_TESTS_COLLECTED

    monkeypatch.setattr(pytest, "main", spy)
    code, out, err = run_cli(pytest_leg, ["-q", "some/dir"], env={"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"})
    assert (code, out, err) == (1, "", "")
    assert [without_selection([a for a in args if not a.startswith("--basetemp=")]) for args in calls] == [["-q", "some/dir"]] * 2


def test_a_worker_count_of_n_at_least_2_hands_pytest_n_n_while_1_hands_it_no_worker_option(pytest_leg, run_cli, monkeypatch):
    calls = []

    def spy(args):
        calls.append([a for a in args if not a.startswith("--basetemp=")])
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    for workers in ("4", "1"):
        env = leg_env(VERI_PYTEST_WORKERS=workers)
        assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    parallel, serial_pass, single, single_serial_pass = [without_selection(c) for c in calls]
    assert "-n" in parallel and parallel[parallel.index("-n") + 1] == "4" or "-n4" in parallel or "--numprocesses=4" in parallel
    assert serial_pass == single == single_serial_pass == ["-q", "some/dir"]


def test_with_no_worker_count_the_launcher_hands_pytest_one_worker_per_available_core_and_runs_serially_on_a_single_core(pytest_leg, run_cli, monkeypatch, tmp_path):
    import os

    calls = []

    def spy(args):
        calls.append([a for a in args if not a.startswith("--basetemp=")])
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    cores = {}
    monkeypatch.setattr(os, "cpu_count", lambda: cores["n"])
    monkeypatch.setattr(os, "process_cpu_count", lambda: cores["n"], raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(cores["n"])), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    for cores["n"], workers in ((6, None), (6, ""), (1, None)):
        env = leg_env(VERI_PYTEST_LEGS=str(tmp_path / "legs"))
        if workers is not None:
            env["VERI_PYTEST_WORKERS"] = workers
        assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    unset, unset_serial, empty, empty_serial, single, single_serial = [without_selection(c) for c in calls]
    for parallel in (unset, empty):
        assert parallel[parallel.index("-n") + 1] == "6" if "-n" in parallel else "-n6" in parallel or "--numprocesses=6" in parallel
    assert unset_serial == empty_serial == single == single_serial == ["-q", "some/dir"]


def test_2100_with_no_worker_count_a_leg_starting_beside_registered_legs_takes_only_the_cores_they_leave_free_and_at_least_1(pytest_leg, run_cli, monkeypatch, tmp_path):
    import os

    calls = []

    def spy(args):
        calls.append([a for a in args if not a.startswith("--basetemp=")])
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    live = [os.getpid(), os.getppid()]
    for registered in ((16,), (8, 8)):
        legs = tmp_path / ("legs-%d" % len(registered))
        legs.mkdir()
        for pid, count in zip(live, registered):
            (legs / str(pid)).write_text("%d\n" % count)
        env = leg_env(VERI_PYTEST_LEGS=str(legs))
        assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    beside_one, _, beside_two, _ = [without_selection(c) for c in calls]
    assert beside_one == beside_two == ["-q", "some/dir"]


def test_2100_a_leg_starting_with_no_worker_count_when_live_registered_legs_already_take_every_core_runs_and_registers_exactly_1_worker(pytest_leg, run_cli, monkeypatch, tmp_path):
    import os

    calls, registered = [], []
    others = [2**22 + 701, 2**22 + 702]
    real_kill = os.kill

    def kill(pid, sig):
        return None if pid in others else real_kill(pid, sig)

    def spy(args):
        calls.append(without_selection([a for a in args if not a.startswith("--basetemp=")]))
        registered.append((legs / str(os.getpid())).read_text().strip())
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(os, "kill", kill)
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    for registered_counts in ((16,), (16, 8)):
        legs = tmp_path / ("legs-%d" % len(registered_counts))
        legs.mkdir()
        for pid, count in zip(others, registered_counts):
            (legs / str(pid)).write_text("%d\n" % count)
        env = leg_env(VERI_PYTEST_LEGS=str(legs))
        assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    assert registered[0::2] == ["1", "1"]
    assert calls[0::2] == [["-q", "some/dir"]] * 2


def test_2100_with_neither_worker_count_nor_legs_directory_set_legs_under_two_different_tmpdirs_share_one_registry_under_the_user_home_so_the_second_takes_1_beside_the_first_s_16(pytest_leg, run_cli, monkeypatch, tmp_path):
    import os
    import tempfile

    calls = []
    nested = []

    def spy(args):
        calls.append([a for a in args if not a.startswith("--basetemp=")])
        if not nested:
            nested.append(True)
            monkeypatch.setenv("TMPDIR", str(tmp_path / "tmp-b"))
            monkeypatch.setattr(tempfile, "tempdir", None)
            assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    (tmp_path / "tmp-a").mkdir()
    (tmp_path / "tmp-b").mkdir()
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("TMPDIR", str(tmp_path / "tmp-a"))
    monkeypatch.setattr(tempfile, "tempdir", None)
    monkeypatch.delenv("VERI_PYTEST_LEGS")
    env = leg_env()
    assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    assert without_selection(calls[1]) == ["-q", "some/dir"]


def test_2100_a_registry_entry_whose_pid_no_longer_answers_kill_0_holds_no_share_so_a_leg_beside_only_a_stale_16_worker_entry_takes_all_16_cores(pytest_leg, run_cli, monkeypatch, tmp_path):
    import os

    calls = []

    def spy(args):
        calls.append(without_selection(args))
        return pytest.ExitCode.OK

    stale = 2**22 + 12345
    real_kill = os.kill

    def kill(pid, sig):
        if pid == stale:
            raise ProcessLookupError(pid)
        return real_kill(pid, sig)

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(os, "kill", kill)
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    legs = tmp_path / "legs"
    legs.mkdir()
    (legs / str(stale)).write_text("16\n")
    env = leg_env(VERI_PYTEST_LEGS=str(legs))
    assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    assert calls[0][:2] == ["-n", "16"] or "-n16" in calls[0]


def test_2100_a_registry_entry_whose_pid_is_alive_but_owned_by_another_user_still_holds_its_share_so_a_leg_beside_only_such_a_16_worker_entry_takes_1(pytest_leg, run_cli, monkeypatch, tmp_path):
    import os

    calls = []

    def spy(args):
        calls.append(without_selection(args))
        return pytest.ExitCode.OK

    foreign = 2**22 + 54321
    real_kill = os.kill

    def kill(pid, sig):
        if pid == foreign:
            raise PermissionError(pid)
        return real_kill(pid, sig)

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(os, "kill", kill)
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    legs = tmp_path / "legs"
    legs.mkdir()
    (legs / str(foreign)).write_text("16\n")
    env = leg_env(VERI_PYTEST_LEGS=str(legs))
    assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    assert "-n" not in calls[0] and not any(a.startswith("-n") for a in calls[0])


def test_2100_a_set_worker_count_is_used_as_given_even_beside_a_live_16_worker_entry_on_16_cores(pytest_leg, run_cli, monkeypatch, tmp_path):
    import os

    calls = []

    def spy(args):
        calls.append([a for a in args if not a.startswith("--basetemp=")])
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    legs = tmp_path / "legs"
    legs.mkdir()
    (legs / str(os.getpid())).write_text("16\n")
    env = leg_env(VERI_PYTEST_LEGS=str(legs), VERI_PYTEST_WORKERS="3")
    assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    parallel = without_selection(calls[0])
    assert parallel[parallel.index("-n") + 1] == "3" if "-n" in parallel else "-n3" in parallel or "--numprocesses=3" in parallel


def test_2100_two_legs_whose_registrations_interleave_at_the_read_together_register_at_most_16_workers_on_16_cores_the_second_getting_only_what_the_first_left(pytest_leg, monkeypatch, tmp_path):
    import os
    import threading

    legs = tmp_path / "legs"
    handed = {}
    reads = []

    def workers_of(args):
        return int(args[args.index("-n") + 1]) if "-n" in args else 1

    def spy(args):
        handed.setdefault(threading.current_thread().name, workers_of(args))
        if threading.current_thread() is threading.main_thread() and second.ident is not None:
            second.join(10)
        return pytest.ExitCode.OK

    real_read = pytest_leg.registered_workers
    second = threading.Thread(name="second", target=lambda: pytest_leg.main(["-q", "some/dir"]))
    real_getpid = os.getpid

    def interleaved_read(directory):
        total = real_read(directory)
        reads.append(total)
        if len(reads) == 1:
            second.start()
            second.join(0.3)
        return total

    import signal

    real_signal = signal.signal

    def main_thread_only(signum, handler):
        return real_signal(signum, handler) if threading.current_thread() is threading.main_thread() else None

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(signal, "signal", main_thread_only)
    monkeypatch.setattr(pytest_leg, "registered_workers", interleaved_read)
    monkeypatch.setattr(os, "getpid", lambda: os.getppid() if threading.current_thread().name == "second" else real_getpid())
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    for name, value in leg_env(VERI_PYTEST_LEGS=str(legs)).items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("VERI_PYTEST_WORKERS", raising=False)
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    try:
        assert pytest_leg.main(["-q", "some/dir"]) == 0
    finally:
        if second.ident is not None:
            second.join(10)
    assert (handed.get("MainThread"), handed.get("second")) == (16, 1)


def test_2100_with_no_worker_count_a_leg_registers_its_worker_count_in_the_legs_registry_while_pytest_runs_and_removes_it_after_whatever_the_status(pytest_leg, run_cli, monkeypatch, tmp_path):
    import os

    legs = tmp_path / "legs"
    during, handed = [], []
    statuses = iter([pytest.ExitCode.TESTS_FAILED, pytest.ExitCode.TESTS_FAILED, pytest.ExitCode.OK, pytest.ExitCode.OK])

    def spy(args):
        during.append(sorted(p.read_text().strip() for p in legs.iterdir()) if legs.is_dir() else None)
        handed.append(without_selection(args))
        return next(statuses)

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(os, "cpu_count", lambda: 6)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 6, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(6)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    env = leg_env(VERI_PYTEST_LEGS=str(legs))
    codes, after = [], []
    for _ in range(2):
        codes.append(run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0])
        after.append(sorted(p.name for p in legs.iterdir()) if legs.is_dir() else [])
    assert (codes, during, after) == ([1, 0], [["6"]] * 4, [[], []])
    assert handed[0][:2] == handed[2][:2] == ["-n", "6"] or "-n6" in handed[0] and "-n6" in handed[2]


def test_launched_from_inside_an_xdist_worker_with_no_worker_count_the_launcher_runs_serially_while_an_explicit_count_still_wins(pytest_leg, run_cli, monkeypatch):
    import os

    calls = []

    def spy(args):
        calls.append([a for a in args if not a.startswith("--basetemp=")])
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(os, "cpu_count", lambda: 6)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 6, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(6)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    for workers in (None, "3"):
        env = leg_env(PYTEST_XDIST_WORKER="gw0")
        if workers is not None:
            env["VERI_PYTEST_WORKERS"] = workers
        assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    nested, nested_serial, explicit, explicit_serial = [without_selection(c) for c in calls]
    assert nested == nested_serial == explicit_serial == ["-q", "some/dir"]
    assert explicit[explicit.index("-n") + 1] == "3" if "-n" in explicit else "-n3" in explicit or "--numprocesses=3" in explicit


def test_each_run_hands_pytest_a_base_directory_of_its_own_that_exists_during_the_run_and_is_gone_after_whatever_the_status(pytest_leg, run_cli, monkeypatch):
    import os

    seen = []
    statuses = iter([pytest.ExitCode.OK, pytest.ExitCode.OK, pytest.ExitCode.OK, pytest.ExitCode.TESTS_FAILED])

    def spy(args):
        given = [a.split("=", 1)[1] for a in args if a.startswith("--basetemp=")]
        seen.append((given[0] if given else None, bool(given) and os.path.isdir(given[0])))
        return next(statuses)

    monkeypatch.setattr(pytest, "main", spy)
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}
    codes = [run_cli(pytest_leg, ["-q"], env=env)[0] for _ in range(2)]
    bases = [base for base, _ in seen]
    assert None not in bases
    assert [existed for _, existed in seen] == [True] * 4
    assert not set(bases[:2]) & set(bases[2:])
    assert [os.path.exists(base) for base in bases] == [False] * 4
    assert codes == [0, 1]


def test_2184_a_leg_records_its_own_pid_in_its_veri_pytest_folder_where_it_is_readable_while_pytest_runs(pytest_leg, run_cli, monkeypatch):
    import os

    recorded = []

    def spy(args):
        base = [a.split("=", 1)[1] for a in args if a.startswith("--basetemp=")][0]
        run = os.path.dirname(base)
        recorded.append([open(os.path.join(run, name)).read().strip() for name in os.listdir(run) if os.path.isfile(os.path.join(run, name))])
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}
    run_cli(pytest_leg, [], env=env)
    assert recorded and str(os.getpid()) in recorded[0]


def test_2184_when_the_leg_s_main_returns_the_sighup_handler_in_force_before_it_started_is_in_force_again(pytest_leg, monkeypatch):
    import signal

    for name, value in leg_env(VERI_PYTEST_WORKERS="1", PYTEST_PLUGINS="").items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)

    def prior(signum, frame):
        pass

    original = signal.signal(signal.SIGHUP, prior)
    try:
        assert pytest_leg.main(["some/dir"]) == 0
        assert signal.getsignal(signal.SIGHUP) is prior
    finally:
        signal.signal(signal.SIGHUP, original)


def test_a_parallel_pass_lets_an_idle_worker_take_cases_queued_on_a_busy_one_and_a_one_worker_run_hands_pytest_no_distribution(pytest_leg, run_cli, monkeypatch):
    calls = []

    def spy(args):
        calls.append([a for a in args if not a.startswith("--basetemp=")])
        return pytest.ExitCode.OK

    def dist_of(args):
        return [args[i + 1] for i, a in enumerate(args) if a == "--dist"] + [a for a in args if a.startswith("--dist=")]

    monkeypatch.setattr(pytest, "main", spy)
    assert run_cli(pytest_leg, ["some/dir"], env=leg_env(VERI_PYTEST_WORKERS="2"))[0] == 0
    assert dist_of(calls[0]) == ["worksteal"]

    calls.clear()
    assert run_cli(pytest_leg, ["some/dir"], env=leg_env(VERI_PYTEST_WORKERS="1"))[0] == 0
    assert [dist_of(c) for c in calls] == [[]] * len(calls)


def test_a_serial_marked_case_is_scheduled_in_a_pass_of_its_own_after_the_parallel_pass_keeping_the_m_selection_and_exiting_0_only_when_both_pass_2092(pytest_leg, run_cli, monkeypatch):
    from _pytest.mark.expression import Expression

    calls = []
    statuses = iter([pytest.ExitCode.OK, pytest.ExitCode.TESTS_FAILED])

    def spy(args):
        calls.append([a for a in args if not a.startswith("--basetemp=")])
        return next(statuses)

    def selects(args, marks):
        expressions = [args[i + 1] for i, a in enumerate(args) if a == "-m"]
        return all(Expression.compile(e).evaluate(lambda name: name in marks) for e in expressions)

    monkeypatch.setattr(pytest, "main", spy)
    env = leg_env(VERI_PYTEST_WORKERS="4")
    code = run_cli(pytest_leg, ["-m", "not process", "some/dir"], env=env)[0]
    assert len(calls) == 2, calls
    parallel, serial = calls
    assert "-n" in parallel and "-n" not in serial
    assert [selects(parallel, m) for m in ({"serial"}, set(), {"process"}, {"process", "serial"})] == [False, True, False, False]
    assert [selects(serial, m) for m in ({"serial"}, set(), {"process"}, {"process", "serial"})] == [True, False, False, False]
    assert code == 1

    calls.clear()
    statuses = iter([pytest.ExitCode.OK, pytest.ExitCode.OK])
    assert run_cli(pytest_leg, ["some/dir"], env=env)[0] == 0


@pytest.mark.parametrize("parallel, serial, code", [
    (pytest.ExitCode.OK, pytest.ExitCode.NO_TESTS_COLLECTED, 0),
    (pytest.ExitCode.NO_TESTS_COLLECTED, pytest.ExitCode.OK, 0),
    (pytest.ExitCode.TESTS_FAILED, pytest.ExitCode.OK, 1),
    (pytest.ExitCode.OK, pytest.ExitCode.TESTS_FAILED, 1),
    (pytest.ExitCode.TESTS_FAILED, pytest.ExitCode.NO_TESTS_COLLECTED, 1),
    (pytest.ExitCode.NO_TESTS_COLLECTED, pytest.ExitCode.TESTS_FAILED, 1),
])
def test_a_pass_that_collects_nothing_counts_as_passed_beside_a_passing_one_while_a_failure_in_either_pass_exits_1_2092(pytest_leg, run_cli, monkeypatch, parallel, serial, code):
    statuses = iter([parallel, serial])
    monkeypatch.setattr(pytest, "main", lambda args: next(statuses))
    env = leg_env(VERI_PYTEST_WORKERS="4")

    assert run_cli(pytest_leg, ["some/dir"], env=env)[0] == code
    assert next(statuses, None) is None


@pytest.mark.parametrize("outcome", [pytest.ExitCode.OK, RuntimeError("boom")], ids=["returns", "raises"])
@pytest.mark.parametrize("prior", [None, "/prior/serial-seen"], ids=["unset", "set"])
def test_2148_after_a_leg_returns_or_raises_pytest_leg_serial_seen_is_what_it_was_before_the_leg_started(pytest_leg, monkeypatch, prior, outcome):
    for name, value in leg_env(VERI_PYTEST_WORKERS="1", PYTEST_PLUGINS="").items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(sys, "path", list(sys.path))
    if prior is None:
        monkeypatch.delenv("PYTEST_LEG_SERIAL_SEEN", raising=False)
    else:
        monkeypatch.setenv("PYTEST_LEG_SERIAL_SEEN", prior)

    def fake_main(args):
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(pytest, "main", fake_main)
    if isinstance(outcome, Exception):
        with pytest.raises(RuntimeError, match="boom"):
            pytest_leg.main(["some/dir"])
    else:
        assert pytest_leg.main(["some/dir"]) == 0

    assert os.environ.get("PYTEST_LEG_SERIAL_SEEN") == prior


def test_2184_at_start_a_leg_removes_a_veri_pytest_folder_in_its_tmpdir_whose_recorded_pid_no_longer_answers_kill_0_whatever_its_age(pytest_leg, run_cli, monkeypatch, tmp_path):
    import os
    import tempfile

    dead = next(pid for pid in range(99999, 1000, -1) if not _answers_kill_0(pid))
    stale = tmp_path / "veri-pytest-deadleg"
    stale.mkdir()
    (stale / "pid").write_text("%d\n" % dead)
    (stale / "leftover").write_text("x")
    os.utime(stale, (1, 1))
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    present = []

    def spy(args):
        present.append(stale.exists())
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}
    assert run_cli(pytest_leg, [], env=env)[0] == 0
    assert present and present[0] is False


def _answers_kill_0(pid):
    import os

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def test_2184_at_start_a_leg_keeps_a_veri_pytest_folder_in_its_tmpdir_whose_recorded_pid_answers_kill_0_whatever_its_age(pytest_leg, run_cli, monkeypatch, tmp_path):
    import os
    import tempfile

    kept = tmp_path / "veri-pytest-liveleg"
    kept.mkdir()
    (kept / "pid").write_text("%d\n" % os.getpid())
    (kept / "leftover").write_text("x")
    os.utime(kept, (1, 1))
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    present = []

    def spy(args):
        present.append((kept / "leftover").exists())
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}
    assert run_cli(pytest_leg, [], env=env)[0] == 0
    assert present and present[0] is True
    assert (kept / "leftover").exists()


def test_2184_at_start_a_leg_keeps_a_veri_pytest_folder_in_its_tmpdir_with_no_recorded_pid_and_one_whose_record_is_not_a_pid(pytest_leg, run_cli, monkeypatch, tmp_path):
    import tempfile

    unrecorded = tmp_path / "veri-pytest-norecord"
    unrecorded.mkdir()
    (unrecorded / "leftover").write_text("x")
    garbled = tmp_path / "veri-pytest-garbled"
    garbled.mkdir()
    (garbled / "pid").write_text("not-a-pid\n")
    (garbled / "leftover").write_text("x")
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    present = []

    def spy(args):
        present.append([(unrecorded / "leftover").exists(), (garbled / "leftover").exists()])
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}
    assert run_cli(pytest_leg, [], env=env)[0] == 0
    assert present and present[0] == [True, True]
    assert (unrecorded / "leftover").exists()
    assert (garbled / "leftover").exists()


def test_2184_at_start_a_leg_keeps_a_dead_pid_folder_not_named_veri_pytest_in_its_tmpdir_and_a_veri_pytest_one_outside_it(pytest_leg, run_cli, monkeypatch, tmp_path):
    import tempfile

    dead = next(pid for pid in range(99999, 1000, -1) if not _answers_kill_0(pid))
    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    other = tmpdir / "other-deadleg"
    outside = elsewhere / "veri-pytest-deadleg"
    for folder in (other, outside):
        folder.mkdir()
        (folder / "pid").write_text("%d\n" % dead)
        (folder / "leftover").write_text("x")
    monkeypatch.setattr(tempfile, "tempdir", str(tmpdir))
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    present = []

    def spy(args):
        present.append([(other / "leftover").exists(), (outside / "leftover").exists()])
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}
    assert run_cli(pytest_leg, [], env=env)[0] == 0
    assert present and present[0] == [True, True]
    assert (other / "leftover").exists()
    assert (outside / "leftover").exists()


def _mirror_of(prefix, folder):
    return prefix / str(folder).lstrip("/")


def _leg_over_scratch_cache(pytest_leg, run_cli, monkeypatch, tmp_path, during, before=lambda prefix, tmpdir: None):
    import tempfile

    tmpdir = tmp_path / "tmp"
    tmpdir.mkdir()
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(tmpdir))
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))
    before(prefix, tmpdir)

    def spy(args):
        base = next(arg for arg in args if arg.startswith("--basetemp="))[len("--basetemp="):]
        during(prefix, os.path.dirname(base))
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "1"}
    code, _, err = run_cli(pytest_leg, [], env=env)
    assert (code, err) == (0, "")
    return tmpdir, prefix


def test_after_a_run_the_bytecode_cache_holds_no_directory_tree_for_a_source_that_lived_under_the_runs_own_scratch_directory_and_leaves_another_tree_alone(pytest_leg, run_cli, monkeypatch, tmp_path):
    seen = {}

    def during(prefix, run):
        own = _mirror_of(prefix, run) / "base" / "test_case0"
        own.mkdir(parents=True, exist_ok=True)
        (own / "scratch_module.cpython-312.pyc").write_bytes(b"x")
        neighbour = _mirror_of(prefix, os.path.dirname(run)) / "veri-pytest-neighbour" / "base"
        neighbour.mkdir(parents=True, exist_ok=True)
        (neighbour / "scratch_module.cpython-312.pyc").write_bytes(b"x")
        seen.update(own=_mirror_of(prefix, run), neighbour=neighbour)

    _leg_over_scratch_cache(pytest_leg, run_cli, monkeypatch, tmp_path, during)

    assert not seen["own"].exists()
    assert (seen["neighbour"] / "scratch_module.cpython-312.pyc").exists()


def test_a_run_leaves_a_tree_reached_through_a_symlink_inside_the_bytecode_prefix_alone_when_it_resolves_outside_the_prefix(pytest_leg, run_cli, monkeypatch, tmp_path):
    outside = tmp_path / "outside"
    kept = []

    def during(prefix, run):
        top = str(run).lstrip("/").split("/")[0]
        if not (prefix / top).exists():
            os.symlink(outside, prefix / top)
        behind = outside / str(run).lstrip("/").partition("/")[2]
        behind.mkdir(parents=True, exist_ok=True)
        (behind / "keep.pyc").write_bytes(b"x")
        kept.append(behind / "keep.pyc")

    _leg_over_scratch_cache(pytest_leg, run_cli, monkeypatch, tmp_path, during)

    assert kept and all(path.exists() for path in kept)


def test_the_sweep_of_a_dead_run_removes_its_bytecode_cache_tree_too_and_keeps_a_live_runs_and_one_with_no_run_folder(pytest_leg, run_cli, monkeypatch, tmp_path):
    dead = next(pid for pid in range(99999, 1000, -1) if not _answers_kill_0(pid))
    trees = {}

    def before(prefix, tmpdir):
        for name, pid in (("veri-pytest-deadleg", dead), ("veri-pytest-liveleg", os.getpid()), ("veri-pytest-orphan", None)):
            folder = tmpdir / name
            if pid is not None:
                folder.mkdir()
                (folder / "pid").write_text("%d\n" % pid)
            trees[name] = _mirror_of(prefix, folder) / "base"
            trees[name].mkdir(parents=True)
            (trees[name] / "scratch_module.cpython-312.pyc").write_bytes(b"x")

    present = []

    def during(prefix, run):
        present.append({name: tree.exists() for name, tree in trees.items()})

    _leg_over_scratch_cache(pytest_leg, run_cli, monkeypatch, tmp_path, during, before)

    assert present[0] == {"veri-pytest-deadleg": False, "veri-pytest-liveleg": True, "veri-pytest-orphan": True}


def test_after_a_run_its_scratch_directory_is_gone_with_every_case_directory_and_file_in_it(pytest_leg, run_cli, monkeypatch, tmp_path):
    runs = []

    def during(prefix, run):
        for number in range(40):
            nested = os.path.join(run, "base", "test_case%d_x" % number, "repo", "objects")
            os.makedirs(nested, exist_ok=True)
            with open(os.path.join(nested, "file"), "w") as f:
                f.write("x")
        with open(os.path.join(run, "base", "loose-file"), "w") as f:
            f.write("x")
        runs.append(run)

    _leg_over_scratch_cache(pytest_leg, run_cli, monkeypatch, tmp_path, during)

    assert runs and not any(os.path.exists(run) for run in runs)


def test_after_a_run_a_symlink_a_case_left_in_its_scratch_directory_is_removed_and_what_it_points_at_is_not(pytest_leg, run_cli, monkeypatch, tmp_path):
    outside = tmp_path / "outside"
    (outside / "inner").mkdir(parents=True)
    (outside / "inner" / "keep").write_text("x")
    runs = []

    def during(prefix, run):
        if not runs:
            os.symlink(outside, os.path.join(run, "base", "link-to-a-directory"))
            os.symlink(outside / "inner" / "keep", os.path.join(run, "base", "link-to-a-file"))
        runs.append(run)

    _leg_over_scratch_cache(pytest_leg, run_cli, monkeypatch, tmp_path, during)

    assert not os.path.exists(runs[0])
    assert (outside / "inner" / "keep").read_text() == "x"


def in_process_leg(pytest_leg, monkeypatch, spy):
    for name, value in leg_env(VERI_PYTEST_WORKERS="1", PYTEST_PLUGINS="").items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("PYTEST_LEG_FULL_LOCK_HOLDER", raising=False)
    monkeypatch.delenv("PYTEST_LEG_LOCK_WAIT_MARKER", raising=False)
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(pytest, "main", spy)


@pytest.mark.timeout(10)
def test_2195_a_subset_run_starts_its_suites_at_once_while_a_full_run_holds_the_lock_and_writes_no_waiting_message(pytest_leg, monkeypatch, capsys):
    import fcntl

    started = []
    in_process_leg(pytest_leg, monkeypatch, lambda args: started.append(args) or pytest.ExitCode.OK)
    os.makedirs(os.path.dirname(importlib.import_module("veri.full_run_lock").path()), exist_ok=True)
    with open(importlib.import_module("veri.full_run_lock").path(), "w") as held:
        held.write("pid 1\ttree /elsewhere\n")
        held.flush()
        fcntl.flock(held, fcntl.LOCK_EX)
        code = pytest_leg.main(["--subset", "some/test_file.py"])

    assert (code, len(started) >= 1, "waiting" in capsys.readouterr().err) == (0, True, False)
    assert all("--subset" not in args and "some/test_file.py" in args for args in started)


def test_2195_after_a_full_run_releases_the_lock_the_lock_file_names_no_pid(pytest_leg, monkeypatch):
    seen = []

    def spy(args):
        seen.append(open(importlib.import_module("veri.full_run_lock").path()).read())
        return pytest.ExitCode.OK

    in_process_leg(pytest_leg, monkeypatch, spy)

    assert pytest_leg.main(["some/dir"]) == 0
    assert seen and all(("pid %d" % os.getpid()) in held for held in seen)
    assert "pid" not in open(importlib.import_module("veri.full_run_lock").path()).read()


def test_2386_on_macos_with_no_worker_count_the_budget_is_the_physical_core_count_less_the_live_legs_workers_and_at_least_1(pytest_leg, monkeypatch, tmp_path, fake_processes):
    fake_processes.answers({"sysctl -n hw.physicalcpu": (0, "8\n", "")}, exact=True)
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.delenv("VERI_PYTEST_WORKERS", raising=False)
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    alone = pytest_leg.worker_count(None)
    (legs / str(os.getpid())).write_text("6\n")
    beside_six = pytest_leg.worker_count(None)
    assert (alone, beside_six) == (8, 2)


def test_2386_off_macos_with_no_worker_count_the_budget_is_the_cpu_affinity_count_less_the_live_legs_workers_never_the_physical_core_count(pytest_leg, monkeypatch, tmp_path, fake_processes):
    fake_processes.answers({"sysctl": (0, "4\n", "")})
    monkeypatch.setattr(os, "cpu_count", lambda: 12)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 12, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(12)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("VERI_PYTEST_WORKERS", raising=False)
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    alone = pytest_leg.worker_count(None)
    (legs / str(os.getpid())).write_text("5\n")
    beside_five = pytest_leg.worker_count(None)
    assert (alone, beside_five) == (12, 7)


def test_2386_on_macos_a_set_worker_count_is_used_as_given_even_above_the_physical_core_count(pytest_leg, monkeypatch, tmp_path, fake_processes):
    fake_processes.answers({"sysctl": (0, "8\n", "")})
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    assert pytest_leg.worker_count("12") == 12


def test_2386_on_macos_with_no_sysctl_on_the_path_the_budget_falls_back_to_the_cpu_count_instead_of_crashing(pytest_leg, monkeypatch, tmp_path, fake_processes):
    fake_processes.answers({"sysctl": FileNotFoundError(2, "No such file or directory", "sysctl")})
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.delenv("VERI_PYTEST_WORKERS", raising=False)
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    assert pytest_leg.worker_count(None) == 16


def test_2397_on_a_mac_whose_sysctl_runs_and_fails_with_empty_stdout_the_worker_count_falls_back_to_the_affinity_count(pytest_leg, monkeypatch, tmp_path, fake_processes):
    legs = tmp_path / "legs"
    legs.mkdir()
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(8)), raising=False)
    monkeypatch.setattr(os, "cpu_count", lambda: 8)
    fake_processes.answers({"sysctl": (1, "", "sysctl: failed")})
    assert pytest_leg.worker_count(None) == 8


def test_2397_on_a_mac_whose_sysctl_exits_0_with_non_numeric_stdout_the_worker_count_falls_back_to_the_affinity_count(pytest_leg, monkeypatch, tmp_path, fake_processes):
    legs = tmp_path / "legs"
    legs.mkdir()
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(8)), raising=False)
    monkeypatch.setattr(os, "cpu_count", lambda: 8)
    fake_processes.answers({"sysctl": (0, "not a number\n", "")})
    assert pytest_leg.worker_count(None) == 8


def launched_with_lock_raising(pytest_leg, monkeypatch, capfd, prefix=None):
    """Runs the leg the way `make test` does, through `launch`, with taking the full-run lock raising OSError."""
    raised = []

    def unlockable():
        raised.append(OSError(13, "Permission denied", "/legs-full.lock"))
        raise raised[-1]

    monkeypatch.setattr(pytest_leg.full_run_lock, "acquire", unlockable)
    monkeypatch.setattr(sys, "pycache_prefix", prefix)
    for name, value in leg_env().items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(sys, "path", list(sys.path))  # main puts veri's directories first on sys.path
    code = pytest_leg.launch([])
    out, err = capfd.readouterr()
    return code, out, err, raised


def test_3985_an_oserror_taking_the_full_run_lock_makes_the_leg_exit_2_with_one_refusal_line_naming_it_and_no_traceback(pytest_leg, monkeypatch, capfd):
    import entry

    code, out, err, raised = launched_with_lock_raising(pytest_leg, monkeypatch, capfd)
    assert (code, out) == (2, "")
    assert err == entry.refusal(pytest_leg.main, raised[0])
    assert "Traceback" not in err and err.count("\n") == 1


def test_3985_a_leg_launched_as_make_test_runs_it_whose_passes_ran_and_had_a_failing_case_still_exits_1(pytest_leg, monkeypatch, capfd):
    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.TESTS_FAILED)
    monkeypatch.setattr(sys, "pycache_prefix", None)
    for name, value in leg_env(VERI_PYTEST_WORKERS="1", VERI_TEST_LOCK="0").items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(sys, "path", list(sys.path))  # main puts veri's directories first on sys.path
    assert pytest_leg.launch(["-q"]) == 1


def test_3985_the_bytecode_cache_record_still_runs_after_a_leg_exits_2_on_an_escaped_oserror(pytest_leg, monkeypatch, capfd, tmp_path):
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    recorded = []
    monkeypatch.setattr(pytest_leg, "record_bytecode_cache", lambda where, run: recorded.append(where))
    code = launched_with_lock_raising(pytest_leg, monkeypatch, capfd, prefix=str(prefix))[0]
    assert (code, recorded) == (2, [str(prefix)])


def launched_over_a_cache(pytest_leg, monkeypatch, capfd, tmp_path, status, check=None, record=None):
    """launch over a bytecode cache under tmp_path, pytest answering <status>, check/record replaced when given:
    (code, stderr, how many times pytest ran)."""
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    ran = []
    monkeypatch.setattr(pytest, "main", lambda args: ran.append(args) or status)
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))
    if check:
        monkeypatch.setattr(pytest_leg, "check_bytecode_cache", check)
    if record:
        monkeypatch.setattr(pytest_leg, "record_bytecode_cache", record)
    for name, value in leg_env(VERI_PYTEST_WORKERS="1", VERI_TEST_LOCK="0").items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(sys, "path", list(sys.path))  # main puts veri's directories first on sys.path
    code = pytest_leg.launch(["-q"])
    return code, capfd.readouterr().err, len(ran)


def unreadable_cache(*_):
    raise PermissionError(13, "Permission denied", "veri-manifest.json")


def test_3985_a_bytecode_cache_check_that_raises_makes_the_leg_exit_2_with_one_line_before_any_pass(pytest_leg, monkeypatch, capfd, tmp_path):
    code, err, passes = launched_over_a_cache(pytest_leg, monkeypatch, capfd, tmp_path, pytest.ExitCode.OK, check=unreadable_cache)
    assert (code, err.count("\n"), "PermissionError" in err, "Traceback" in err, passes) == (2, 1, True, False, 0)


def test_3985_a_bytecode_cache_record_that_raises_after_green_passes_makes_the_leg_exit_2_with_one_line(pytest_leg, monkeypatch, capfd, tmp_path):
    code, err, passes = launched_over_a_cache(pytest_leg, monkeypatch, capfd, tmp_path, pytest.ExitCode.OK, record=unreadable_cache)
    assert (code, err.count("\n"), "PermissionError" in err, "Traceback" in err) == (2, 1, True, False)


def test_3985_a_bytecode_cache_record_that_raises_after_a_failing_case_keeps_the_legs_exit_1_and_says_so_in_one_line(pytest_leg, monkeypatch, capfd, tmp_path):
    code, err, passes = launched_over_a_cache(pytest_leg, monkeypatch, capfd, tmp_path, pytest.ExitCode.TESTS_FAILED, record=unreadable_cache)
    assert (code, err.count("\n"), "PermissionError" in err, "Traceback" in err) == (1, 1, True, False)


def busy(*_args, **_kwargs):
    raise OSError(16, "Resource busy")


TEARDOWN_SITES = {
    "the run directory's removal": lambda pytest_leg, monkeypatch: monkeypatch.setattr(pytest_leg, "clear_case_directories", busy),
    "the full-run lock's release": lambda pytest_leg, monkeypatch: monkeypatch.setattr(pytest_leg.full_run_lock.Lock, "release", busy),
    "the leg registry's unregister": lambda pytest_leg, monkeypatch: monkeypatch.setattr(pytest_leg, "unregister", busy),
}


@pytest.mark.parametrize("status, code", [(pytest.ExitCode.TESTS_FAILED, 1), (pytest.ExitCode.OK, 2)], ids=["red", "green"])
@pytest.mark.parametrize("site", sorted(TEARDOWN_SITES))
def test_3985_a_teardown_that_raises_after_the_passes_is_one_line_and_keeps_a_red_legs_1_and_turns_a_green_ones_0_into_2(
        pytest_leg, monkeypatch, capfd, tmp_path, site, status, code):
    monkeypatch.setattr(pytest, "main", lambda args: status)
    monkeypatch.setattr(sys, "pycache_prefix", None)
    monkeypatch.setattr(sys, "path", list(sys.path))  # main puts veri's directories first on sys.path
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: {0, 1}, raising=False)
    monkeypatch.delenv("VERI_PYTEST_WORKERS", raising=False)
    monkeypatch.delenv("VERI_TEST_LOCK", raising=False)
    monkeypatch.delenv("PYTEST_LEG_FULL_LOCK_HOLDER", raising=False)
    for name, value in leg_env().items():
        monkeypatch.setenv(name, value)
    TEARDOWN_SITES[site](pytest_leg, monkeypatch)

    got = pytest_leg.launch(["-q"])
    err = capfd.readouterr().err

    assert (got, err.count("\n"), "OSError: [Errno 16] Resource busy" in err, "Traceback" in err) == (code, 1, True, False)
