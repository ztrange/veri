"""In-process cases for tests/leg/pytest_leg.py, the launcher that makes the pytest leg's refusals and then runs pytest."""
import importlib
import os
import sys
import time

import pytest


@pytest.fixture
def pytest_leg():
    return importlib.import_module("pytest_leg")


def leg_env(**extra):
    """The env a case hands the launcher to pass its three importable checks, plus the case's own variables."""
    return {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", **extra}


def without_selection(args):
    return importlib.import_module("pytest_leg").split_marks(args)[0]


SELF_STARTED = "Wed Nov 18 08:00:00 2026"
PARENT_STARTED = "Wed Nov 18 07:00:00 2026"


@pytest.fixture
def started(fake_processes):
    """Answers `ps -o lstart= -p <pid>` with this process's and its parent's start times, plus `more` ({pid: text});
    any other process, a ps for a pid not in the table included, exits 1 with no output, as ps does for an unknown pid.
    Returns the setter, so a case adds pids (and other answers, `extra`) after the fixture installed the defaults."""
    def answer(more=None, extra=None):
        table = {os.getpid(): SELF_STARTED, os.getppid(): PARENT_STARTED, **(more or {})}
        answers = {"ps -o lstart= -p %d" % pid: (0, text + "\n", "") for pid, text in table.items()}
        return fake_processes.answers({**answers, **(extra or {})}, default=(1, "", ""), exact=True)
    answer()
    return answer


def registered(path, count, started_text=None):
    """Writes a registry entry as a live leg does: its worker count, then its pid's start time."""
    pid = int(path.name)
    started_text = started_text or {os.getpid(): SELF_STARTED, os.getppid(): PARENT_STARTED}[pid]
    path.write_text("%d\n%s\n" % (count, started_text))


def measured(n):
    """Writes a ceiling record of <n> where the hermetic fixture points VERI_TEST_CEILING_FILE, so the leg's budget is
    <n> and it prints no fallback line."""
    with open(os.environ["VERI_TEST_CEILING_FILE"], "w") as f:
        f.write("%d\n2026-11-18\n" % n)


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


def test_with_no_worker_count_the_launcher_hands_pytest_one_worker_per_available_core_and_2_on_a_single_core_4419(pytest_leg, run_cli, monkeypatch, tmp_path):
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
    assert single[:2] == ["-n", "2"]
    assert unset_serial == empty_serial == single_serial == ["-q", "some/dir"]


def test_2100_with_no_worker_count_a_leg_starting_beside_registered_legs_takes_only_the_cores_they_leave_free_and_at_least_2_4419(pytest_leg, run_cli, monkeypatch, tmp_path, started):
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
    for counts in ((14,), (8, 6)):
        legs = tmp_path / ("legs-%d" % len(counts))
        legs.mkdir()
        for pid, count in zip(live, counts, strict=False):
            registered(legs / str(pid), count)
        env = leg_env(VERI_PYTEST_LEGS=str(legs))
        assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    beside_one, _, beside_two, _ = [without_selection(c) for c in calls]
    assert beside_one == beside_two == ["-n", "2", "--dist", "worksteal", "-q", "some/dir"]


def test_2100_with_neither_worker_count_nor_legs_directory_set_legs_under_two_different_tmpdirs_share_one_registry_under_the_user_home_so_the_second_takes_2_beside_the_first_s_16(pytest_leg, run_cli, monkeypatch, tmp_path):
    import os
    import tempfile

    calls = []
    cores = [16]
    nested = []

    def spy(args):
        calls.append([a for a in args if not a.startswith("--basetemp=")])
        if not nested:
            nested.append(True)
            cores[0] = 18
            monkeypatch.setenv("TMPDIR", str(tmp_path / "tmp-b"))
            monkeypatch.setattr(tempfile, "tempdir", None)
            assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(os, "cpu_count", lambda: cores[0])
    monkeypatch.setattr(os, "process_cpu_count", lambda: cores[0], raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(cores[0])), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    (tmp_path / "tmp-a").mkdir()
    (tmp_path / "tmp-b").mkdir()
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("TMPDIR", str(tmp_path / "tmp-a"))
    monkeypatch.setattr(tempfile, "tempdir", None)
    monkeypatch.delenv("VERI_PYTEST_LEGS")
    env = leg_env()
    assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    assert without_selection(calls[1])[:2] == ["-n", "2"]


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


def test_2100_a_registry_entry_whose_pid_is_alive_but_owned_by_another_user_still_holds_its_share_so_a_leg_beside_only_such_a_16_worker_entry_on_18_cores_takes_2(pytest_leg, run_cli, monkeypatch, tmp_path, started):
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
    monkeypatch.setattr(os, "cpu_count", lambda: 18)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 18, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(18)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    legs = tmp_path / "legs"
    legs.mkdir()
    registered(legs / str(foreign), 16, "Tue Nov 17 06:00:00 2026")
    started({foreign: "Tue Nov 17 06:00:00 2026"})
    env = leg_env(VERI_PYTEST_LEGS=str(legs))
    assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    assert calls[0][:2] == ["-n", "2"]


def test_2100_a_set_worker_count_is_used_as_given_even_beside_a_live_16_worker_entry_on_16_cores(pytest_leg, run_cli, monkeypatch, tmp_path, started):
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
    registered(legs / str(os.getpid()), 16)
    env = leg_env(VERI_PYTEST_LEGS=str(legs), VERI_PYTEST_WORKERS="3")
    assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    parallel = without_selection(calls[0])
    assert parallel[parallel.index("-n") + 1] == "3" if "-n" in parallel else "-n3" in parallel or "--numprocesses=3" in parallel


def test_2100_two_legs_whose_registrations_interleave_at_the_read_together_register_at_most_16_workers_on_16_cores_the_second_getting_only_what_the_first_left(pytest_leg, monkeypatch, tmp_path, started):
    import os
    import threading

    legs = tmp_path / "legs"
    handed = {}
    reads = []
    cores = [16]

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
            cores[0] = 18
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
    monkeypatch.setattr(os, "cpu_count", lambda: cores[0])
    monkeypatch.setattr(os, "process_cpu_count", lambda: cores[0], raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(cores[0])), raising=False)
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
    assert (handed.get("MainThread"), handed.get("second")) == (16, 2)


def test_2100_with_no_worker_count_a_leg_registers_its_worker_count_in_the_legs_registry_while_pytest_runs_and_removes_it_after_whatever_the_status(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    import os

    legs = tmp_path / "legs"
    during, handed = [], []
    statuses = iter([pytest.ExitCode.TESTS_FAILED, pytest.ExitCode.TESTS_FAILED, pytest.ExitCode.OK, pytest.ExitCode.OK])

    def spy(args):
        during.append(sorted(p.read_text().split("\n")[0] for p in legs.iterdir()) if legs.is_dir() else None)
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


def test_4261_main_leaves_sys_path_as_it_found_it_once_it_returns(pytest_leg, monkeypatch):
    in_process_leg(pytest_leg, monkeypatch, lambda args: pytest.ExitCode.OK)
    before = list(sys.path)

    assert pytest_leg.main(["some/dir"]) == 0

    assert sys.path == before


def test_4261_main_leaves_sys_path_as_it_found_it_once_it_raises(pytest_leg, monkeypatch):
    def spy(args):
        raise RuntimeError("the pass broke")

    in_process_leg(pytest_leg, monkeypatch, spy)
    before = list(sys.path)

    with pytest.raises(RuntimeError, match="the pass broke"):
        pytest_leg.main(["some/dir"])

    assert sys.path == before


def test_2386_on_macos_with_no_worker_count_the_budget_is_the_physical_core_count_less_the_live_legs_workers_and_at_least_1(pytest_leg, monkeypatch, tmp_path, started):
    started(extra={"sysctl -n hw.physicalcpu": (0, "8\n", "")})
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
    registered(legs / str(os.getpid()), 6)
    beside_six = pytest_leg.worker_count(None)
    assert (alone, beside_six) == (8, 2)


def test_2386_off_macos_with_no_worker_count_the_budget_is_the_cpu_affinity_count_less_the_live_legs_workers_never_the_physical_core_count(pytest_leg, monkeypatch, tmp_path, started):
    started(extra={"sysctl -n hw.physicalcpu": (0, "4\n", "")})
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
    registered(legs / str(os.getpid()), 5)
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
    measured(2)
    TEARDOWN_SITES[site](pytest_leg, monkeypatch)

    got = pytest_leg.launch(["-q"])
    err = capfd.readouterr().err

    assert (got, err.count("\n"), "OSError: [Errno 16] Resource busy" in err, "Traceback" in err) == (code, 1, True, False)


def test_4310_a_leg_with_no_worker_count_that_finds_the_registered_workers_at_the_cores_starts_pytest_only_after_a_registered_leg_is_gone(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    blocker = legs / str(os.getppid())
    registered(blocker, 16)
    started_with_blocker = []

    def spy(args):
        started_with_blocker.append(blocker.exists())
        return pytest.ExitCode.OK

    def death_during_the_poll_sleep(seconds):
        blocker.unlink(missing_ok=True)

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(pytest_leg.time, "sleep", death_during_the_poll_sleep)
    env = leg_env(VERI_PYTEST_LEGS=str(legs))
    assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    assert started_with_blocker == [False, False]


def test_4310_a_leg_waiting_for_a_free_core_writes_one_stderr_line_however_many_polls_naming_the_cores_in_use_and_the_holding_pids(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    measured(16)
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    holder = os.getppid()
    blocker = legs / str(holder)
    registered(blocker, 16)
    polls = []

    def death_on_the_third_poll(seconds):
        polls.append(seconds)
        if len(polls) == 3:
            blocker.unlink()

    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", death_on_the_third_poll)
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))

    assert (code, len(polls), [(str(holder) in line, "16" in line) for line in err.splitlines()]) == (0, 3, [(True, True)])


def test_4310_a_leg_waiting_for_a_free_core_holds_the_lock_wait_marker_so_lock_waiting_reports_it_and_the_marker_is_gone_once_pytest_starts(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    import supervise
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    blocker = legs / str(os.getppid())
    registered(blocker, 16)
    marker = tmp_path / "marker"
    waiting_while_polling = []
    marker_at_start = []

    def death_during_the_poll_sleep(seconds):
        waiting_while_polling.append(supervise.lock_waiting(str(marker)))
        blocker.unlink(missing_ok=True)

    def spy(args):
        marker_at_start.append(marker.exists())
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(pytest_leg.time, "sleep", death_during_the_poll_sleep)
    env = leg_env(VERI_PYTEST_LEGS=str(legs), PYTEST_LEG_LOCK_WAIT_MARKER=str(marker))
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0]

    assert (code, waiting_while_polling, marker_at_start[:1], marker.exists()) == (0, [True], [False], False)


def test_4310_a_leg_whose_wait_ends_as_4_of_16_cores_free_hands_pytest_4_workers_and_registers_4_while_pytest_runs(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    registered(legs / "1", 12, "Thu Nov 12 05:00:00 2026")
    started({1: "Thu Nov 12 05:00:00 2026"})
    leaving = legs / str(os.getppid())
    registered(leaving, 4)
    started = []

    def spy(args):
        if not started:
            started.append((args[args.index("-n") + 1] if "-n" in args else "1", (legs / str(os.getpid())).read_text().split("\n")[0]))
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    monkeypatch.setattr(pytest_leg.time, "sleep", lambda seconds: leaving.unlink(missing_ok=True))
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))[0]

    assert (code, started) == (0, [("4", "4")])


def test_4310_a_leg_that_waited_7_seconds_for_a_free_core_writes_one_core_wait_event_carrying_seconds_7(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    import json
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    legs = tmp_path / "legs"
    legs.mkdir()
    blocker = legs / str(os.getppid())
    registered(blocker, 16)
    clock = [1000.0]

    def seven_seconds_then_death(seconds):
        clock[0] += 7
        blocker.unlink(missing_ok=True)

    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(pytest_leg.time, "sleep", seven_seconds_then_death)
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)), cwd=str(tree))[0]
    journal = tree / ".tdd" / "events.jsonl"
    lines = [json.loads(line) for line in journal.read_text().splitlines()] if journal.exists() else []

    assert (code, [line.get("seconds") for line in lines if line["event"] == "core-wait"]) == (0, ["7"])


def test_4310_a_leg_that_finds_a_core_free_starts_without_writing_a_core_wait_event(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    legs = tmp_path / "legs"
    legs.mkdir()
    registered(legs / str(os.getppid()), 14)
    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)), cwd=str(tree))[0]
    journal = tree / ".tdd" / "events.jsonl"

    assert (code, "core-wait" in (journal.read_text() if journal.exists() else "")) == (0, False)


def test_4310_a_full_run_that_must_wait_for_a_free_core_already_holds_the_full_run_lock_when_its_wait_begins(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    monkeypatch.delenv("PYTEST_LEG_FULL_LOCK_HOLDER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    blocker = legs / str(os.getppid())
    registered(blocker, 16)
    lock = tmp_path / "legs-full.lock"
    held_at_wait = []

    def poll(seconds):
        held_at_wait.append(lock.exists() and lock.read_text().startswith("pid %d\t" % os.getpid()))
        blocker.unlink(missing_ok=True)

    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", poll)
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), VERI_TEST_LOCK="1"))[0]

    assert (code, held_at_wait) == (0, [True])


def test_4310_a_leg_with_veri_pytest_workers_set_reads_neither_the_core_count_nor_the_registry_beside_a_full_registry(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    reads = []

    def read(name, value):
        def reader(*args):
            reads.append(name)
            return value
        return reader

    monkeypatch.setattr(os, "cpu_count", read("cpu_count", 16))
    monkeypatch.setattr(os, "process_cpu_count", read("process_cpu_count", 16), raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", read("sched_getaffinity", set(range(16))), raising=False)
    # The leg reads the registry both through its own registered_legs and through leg_registry.registered_workers,
    # which looks registered_legs up in leg_registry, so the spy sits on both names.
    for module in (pytest_leg, importlib.import_module("leg_registry")):
        monkeypatch.setattr(module, "registered_legs", read("registered_legs", [(str(os.getppid()), 16)]))
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    registered(legs / str(os.getppid()), 16)
    handed = []
    monkeypatch.setattr(pytest, "main", lambda args: handed.append(args[args.index("-n") + 1] if "-n" in args else "1") or pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", lambda seconds: reads.append("waited"))
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), VERI_PYTEST_WORKERS="3"))[0]

    assert (code, reads, handed[:1]) == (0, [], ["3"])


def on_16_cores(monkeypatch):
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)


class NeverFreed(Exception):
    """Raised by a poll a case caps, so a leg that would wait forever fails the case instead of hanging it."""


def polls(seen, limit=3, also=lambda: None):
    def sleep(seconds):
        seen.append(seconds)
        also()
        if len(seen) >= limit:
            raise NeverFreed("still waiting after %d polls" % len(seen))
    return sleep


def handed_workers(handed):
    def spy(args):
        handed.append(args[args.index("-n") + 1] if "-n" in args else "1")
        return pytest.ExitCode.OK
    return spy


def test_4310_a_registry_entry_whose_pid_now_runs_under_another_start_time_holds_no_share_and_is_removed_while_a_live_legs_entry_keeps_its_share(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_16_cores(monkeypatch)
    legs = tmp_path / "legs"
    legs.mkdir()
    registered(legs / "1", 16, "Mon Jan  5 00:00:00 2015")
    registered(legs / str(os.getppid()), 10)
    started({1: "Thu Nov 12 05:00:00 2026"})
    waited, handed = [], []
    monkeypatch.setattr(pytest, "main", handed_workers(handed))
    monkeypatch.setattr(pytest_leg.time, "sleep", polls(waited))
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))[0]

    assert (code, waited, handed[:1], sorted(p.name for p in legs.iterdir())) == (0, [], ["6"], [str(os.getppid())])


def test_4310_an_entry_with_no_start_time_an_older_legs_holds_no_share_even_for_a_live_pid_and_stays_while_that_pid_lives(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_16_cores(monkeypatch)
    legs = tmp_path / "legs"
    legs.mkdir()
    older = legs / str(os.getppid())
    older.write_text("16\n")
    waited, handed = [], []
    monkeypatch.setattr(pytest, "main", handed_workers(handed))
    monkeypatch.setattr(pytest_leg.time, "sleep", polls(waited))
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))[0]

    assert (code, waited, handed[:1], older.read_text()) == (0, [], ["16"], "16\n")


def test_4310_a_malformed_unreadable_or_non_pid_entry_holds_no_share_and_none_crashes_the_leg_or_is_removed(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_16_cores(monkeypatch)
    legs = tmp_path / "legs"
    legs.mkdir()
    (legs / str(os.getppid())).write_text("sixteen\n%s\n" % PARENT_STARTED)
    (legs / "notapid").write_text("16\n")
    (legs / "1").mkdir()
    waited, handed = [], []
    monkeypatch.setattr(pytest, "main", handed_workers(handed))
    monkeypatch.setattr(pytest_leg.time, "sleep", polls(waited))
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))[0]

    assert (code, waited, handed[:1], sorted(p.name for p in legs.iterdir())) == (0, [], ["16"], sorted(["1", "notapid", str(os.getppid())]))


@pytest.mark.parametrize("reads, share", [
    (["", "Mon Jan  5 00:00:00 2015"], "16"),
    (["Mon Jan  5 00:00:00 2015", ""], "16"),
    (["Mon Jan  5 00:00:00 2015", PARENT_STARTED], "6"),
], ids=["first-read-fails", "second-read-fails", "second-read-matches-the-record"])
def test_4310_a_live_pids_entry_is_removed_only_when_two_pinned_start_time_reads_both_succeed_and_differ_from_its_record_else_it_stays(pytest_leg, run_cli, monkeypatch, tmp_path, started, reads, share):
    on_16_cores(monkeypatch)
    legs = tmp_path / "legs"
    legs.mkdir()
    live = legs / str(os.getppid())
    registered(live, 10)
    answers = iter(reads)
    real_field = pytest_leg.pid_file.ps_field
    monkeypatch.setattr(pytest_leg.pid_file, "ps_field", lambda field, pid: (
        next(answers, "") if (field, int(pid)) == ("lstart", os.getppid()) else real_field(field, pid)))
    waited, handed = [], []
    monkeypatch.setattr(pytest, "main", handed_workers(handed))
    monkeypatch.setattr(pytest_leg.time, "sleep", polls(waited))
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))[0]

    assert (code, waited, handed[:1], live.read_text()) == (0, [], [share], "10\n%s\n" % PARENT_STARTED)


def test_4310_an_entry_whose_pid_is_gone_holds_no_share_and_is_removed(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_16_cores(monkeypatch)
    gone = 2**22 + 12345
    real_kill = os.kill

    def kill(pid, sig):
        if pid == gone:
            raise ProcessLookupError(pid)
        return real_kill(pid, sig)

    monkeypatch.setattr(os, "kill", kill)
    legs = tmp_path / "legs"
    legs.mkdir()
    registered(legs / str(gone), 16, "Mon Jan  5 00:00:00 2015")
    waited, handed = [], []
    monkeypatch.setattr(pytest, "main", handed_workers(handed))
    monkeypatch.setattr(pytest_leg.time, "sleep", polls(waited))
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))[0]

    assert (code, waited, handed[:1], sorted(p.name for p in legs.iterdir())) == (0, [], ["16"], [])


def test_4310_an_entry_whose_kill_0_fails_otherwise_or_overflows_holds_no_share_and_is_kept(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    import errno

    on_16_cores(monkeypatch)
    failing, huge = 2**22 + 777, 10**25
    real_kill = os.kill

    def kill(pid, sig):
        if pid == failing:
            raise OSError(errno.EINVAL, "invalid")
        if pid == huge:
            raise OverflowError(pid)
        return real_kill(pid, sig)

    monkeypatch.setattr(os, "kill", kill)
    legs = tmp_path / "legs"
    legs.mkdir()
    registered(legs / str(failing), 16, "Mon Jan  5 00:00:00 2015")
    registered(legs / str(huge), 16, "Mon Jan  5 00:00:00 2015")
    waited, handed = [], []
    monkeypatch.setattr(pytest, "main", handed_workers(handed))
    monkeypatch.setattr(pytest_leg.time, "sleep", polls(waited))
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))[0]

    assert (code, waited, handed[:1], sorted(p.name for p in legs.iterdir())) == (0, [], ["16"], sorted([str(failing), str(huge)]))


def test_4310_a_leg_registers_its_worker_count_on_line_1_and_its_own_start_time_on_line_2(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_16_cores(monkeypatch)
    legs = tmp_path / "legs"
    during = []
    monkeypatch.setattr(pytest, "main", lambda args: during.append((legs / str(os.getpid())).read_text()) or pytest.ExitCode.OK)
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))[0]

    assert (code, during[:1]) == (0, ["16\n%s\n" % SELF_STARTED])


def test_4310_a_core_wait_whose_marker_another_leg_removed_meanwhile_still_starts_pytest_and_exits_0(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_16_cores(monkeypatch)
    legs = tmp_path / "legs"
    legs.mkdir()
    blocker = legs / str(os.getppid())
    registered(blocker, 16)
    marker = tmp_path / "marker"
    waited, handed = [], []

    def the_other_leg_finishes():
        marker.unlink(missing_ok=True)
        blocker.unlink(missing_ok=True)

    monkeypatch.setattr(pytest, "main", handed_workers(handed))
    monkeypatch.setattr(pytest_leg.time, "sleep", polls(waited, also=the_other_leg_finishes))
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), PYTEST_LEG_LOCK_WAIT_MARKER=str(marker)))

    assert (code, len(waited), handed[:1], "Error" in err) == (0, 1, ["16"], False)


def test_4310_a_core_wait_whose_marker_cannot_be_written_waits_unmarked_saying_so_once_and_exits_0(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_16_cores(monkeypatch)
    legs = tmp_path / "legs"
    legs.mkdir()
    blocker = legs / str(os.getppid())
    registered(blocker, 16)
    marker = tmp_path / "no-such-directory" / "marker"
    waited, handed = [], []

    def freed_on_the_second_poll():
        if len(waited) == 2:
            blocker.unlink()

    monkeypatch.setattr(pytest, "main", handed_workers(handed))
    monkeypatch.setattr(pytest_leg.time, "sleep", polls(waited, also=freed_on_the_second_poll))
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), PYTEST_LEG_LOCK_WAIT_MARKER=str(marker)))
    unmarked = [line for line in err.splitlines() if line.startswith("cannot mark the core wait")]

    assert (code, len(waited), handed[:1], len(unmarked), str(marker) in "".join(unmarked)) == (0, 2, ["16"], 1, True)


def test_4310_a_leg_ended_by_term_while_it_waits_for_a_core_has_removed_its_wait_marker_by_the_time_it_exits(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    import signal

    import idle_watch
    on_16_cores(monkeypatch)
    legs = tmp_path / "legs"
    legs.mkdir()
    registered(legs / str(os.getppid()), 16)
    marker = tmp_path / "marker"
    marked_at_exit = []

    def exit(code):
        marked_at_exit.append(marker.exists())
        raise SystemExit(code)

    class Watch(idle_watch.Watch):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, exit=exit, **kwargs)

    def term(seconds):
        assert marker.exists()
        signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)

    monkeypatch.setattr(idle_watch, "Watch", Watch)
    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", term)
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), PYTEST_LEG_LOCK_WAIT_MARKER=str(marker)))[0]

    assert (code, marked_at_exit) == (128 + signal.SIGTERM, [False])


def test_4311_a_case_waiting_for_a_core_under_the_fixtures_own_working_directory_appends_no_core_wait_event_to_the_real_trees_journal(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    from conftest import ROOT
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    blocker = legs / str(os.getppid())
    registered(blocker, 16)
    clock = [1000.0]

    def a_distinct_wait_then_death(seconds):
        clock[0] += 4311
        blocker.unlink(missing_ok=True)

    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(pytest_leg.time, "sleep", a_distinct_wait_then_death)
    journal = ROOT / ".tdd" / "events.jsonl"

    def distinct_waits():
        return [line for line in (journal.read_text().splitlines() if journal.exists() else []) if '"event": "core-wait"' in line and '"seconds": "4311"' in line]

    before = distinct_waits()
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))[0]

    assert (code, distinct_waits()) == (0, before)


@pytest.mark.parametrize("held, workers", [(0, "4"), (14, "2")])
def test_4311_a_leg_handed_cap_4_with_no_worker_count_takes_min_4_and_the_free_cores_and_registers_that_count_while_pytest_runs(pytest_leg, run_cli, monkeypatch, tmp_path, started, held, workers):
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    if held:
        registered(legs / str(os.getppid()), held)
    seen = []

    def spy(args):
        seen.append((args[args.index("-n") + 1] if "-n" in args else "1", (legs / str(os.getpid())).read_text().split("\n")[0], "--cap=4" in args))
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    code = run_cli(pytest_leg, ["--cap=4", "-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))[0]

    assert (code, seen[:1]) == (0, [(workers, workers, False)])


@pytest.mark.parametrize("cap", ["--cap=0", "--cap=", "--cap=four", "--cap=-1"])
def test_4311_a_cap_that_is_not_a_whole_number_of_at_least_1_exits_2_in_one_line_naming_it_before_pytest_runs(pytest_leg, run_cli, monkeypatch, cap):
    ran = []
    monkeypatch.setattr(pytest, "main", lambda args: ran.append(args) or pytest.ExitCode.OK)
    code, _, err = run_cli(pytest_leg, [cap, "-q", "some/dir"], env=leg_env())

    assert (code, ran, err.count("\n"), cap in err) == (2, [], 1, True)


def test_4311_a_cap_4_leg_finding_no_free_core_waits_with_one_stderr_line_the_wait_marker_and_one_core_wait_event_carrying_its_seconds(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    measured(16)
    import json

    import supervise
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    tree = tmp_path / "tree"
    (tree / ".git").mkdir(parents=True)
    legs = tmp_path / "legs"
    legs.mkdir()
    holder = os.getppid()
    blocker = legs / str(holder)
    registered(blocker, 16)
    marker = tmp_path / "marker"
    clock = [1000.0]
    polls = []

    def five_seconds_a_poll_then_death_on_the_second(seconds):
        polls.append(supervise.lock_waiting(str(marker)))
        clock[0] += 5
        if len(polls) == 2:
            blocker.unlink()

    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(pytest_leg.time, "sleep", five_seconds_a_poll_then_death_on_the_second)
    argv = ["--cap=4", "--timeout=30", "-m", "not process and not tree_audit", "some/dir"]
    env = leg_env(VERI_PYTEST_LEGS=str(legs), PYTEST_LEG_LOCK_WAIT_MARKER=str(marker))
    code, _, err = run_cli(pytest_leg, argv, env=env, cwd=str(tree))
    journal = tree / ".tdd" / "events.jsonl"
    waits = [line.get("seconds") for line in map(json.loads, journal.read_text().splitlines() if journal.exists() else []) if line["event"] == "core-wait"]

    assert (code, [str(holder) in line for line in err.splitlines()], polls, marker.exists(), waits) == (0, [True], [True, True], False, ["10"])


def on_cores(monkeypatch, n, platform="linux"):
    """Fakes a machine of <n> cores (affinity and cpu_count alike) on <platform>, outside any xdist worker."""
    monkeypatch.setattr(os, "cpu_count", lambda: n)
    monkeypatch.setattr(os, "process_cpu_count", lambda: n, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(n)), raising=False)
    monkeypatch.setattr(sys, "platform", platform)
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)


def workers_handed(calls):
    """The -n value of the first pytest pass the spy saw, "1" when it ran serially."""
    first = calls[0]
    return first[first.index("-n") + 1] if "-n" in first else "1"


def test_4419_a_full_leg_alone_beside_a_ceiling_record_of_6_on_16_cores_takes_6_and_says_nothing_about_make_ceiling(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 16)
    record = tmp_path / "ceiling"
    record.write_text("6\n2026-11-18\nabc123\n1.5\n2 100 0\n4 60 0\n6 50 0\n8 48 1\n")
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(args) or pytest.ExitCode.OK)
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_TEST_CEILING_FILE=str(record)))

    assert (code, workers_handed(calls), "make ceiling" in err) == (0, "6", False)


@pytest.mark.parametrize("idle", ["idle all 50\nidle fast 2\n", "idle all 50\nidle fast 12\n"], ids=["below", "above"])
def test_4456_a_full_leg_beside_a_record_holding_idle_lines_takes_its_line_1_and_says_nothing_about_make_ceiling(pytest_leg, run_cli, monkeypatch, tmp_path, started, idle):
    on_cores(monkeypatch, 16)
    record = tmp_path / "ceiling"
    record.write_text("6\n2026-11-18\nabc123\n1.5\n2 100 0\n4 60 0\n6 50 0\n8 48 1\n" + idle)
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(args) or pytest.ExitCode.OK)
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_TEST_CEILING_FILE=str(record)))

    assert (code, workers_handed(calls), "make ceiling" in err) == (0, "6", False)


@pytest.mark.parametrize("cap, record, workers", [
    ("4\n", 8, "4"), ("4\nhand-set on 2026-11-19\n", 8, "4"), ("12\n", 8, "8"), ("8\n", 8, "8"), (None, 8, "8"), ("4\n", None, "4"),
    ("2\n", 8, "2"),
], ids=["below", "line-1-only", "above", "equal", "no-cap", "below-the-core-fallback", "two-the-least-cap"])
def test_4457_a_full_leg_alone_takes_min_of_c0_and_the_cap_on_line_1_of_the_cap_file_and_leaves_the_file_as_it_was(pytest_leg, run_cli, monkeypatch, tmp_path, started, cap, record, workers):
    on_cores(monkeypatch, 16)
    if record:
        measured(record)
    path = os.environ["VERI_TEST_CAP_FILE"]
    if cap is not None:
        with open(path, "w") as f:
            f.write(cap)
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(args) or pytest.ExitCode.OK)
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env())
    left = open(path).read() if os.path.exists(path) else None

    assert (code, workers_handed(calls), left, "cap" in err) == (0, workers, cap, False), err


def test_4453_a_full_leg_alone_beside_one_unexpired_lane_entry_needing_4_under_a_ceiling_record_of_10_takes_4(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 16)
    measured(10)
    entries = tmp_path / "veri-test-budget"
    entries.mkdir()
    (entries / "main@0123456789abcdef").write_text("4\n%d\n" % (time.time() + 3600))
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(args) or pytest.ExitCode.OK)
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_TEST_BUDGET_DIR=str(entries)))

    assert (code, workers_handed(calls)) == (0, "4"), err


@pytest.mark.parametrize("line_1", ["", "six", "1", "0", "-4", "2.5", "\u0663", b"\xff\xfe", "a directory"])
def test_4457_a_cap_file_unreadable_or_whose_line_1_is_not_a_whole_number_of_at_least_2_sets_no_cap_and_is_one_stderr_line_naming_it(pytest_leg, run_cli, monkeypatch, tmp_path, started, line_1):
    on_cores(monkeypatch, 16)
    measured(8)
    path = os.environ["VERI_TEST_CAP_FILE"]
    if line_1 == "a directory":
        os.mkdir(path)
    elif isinstance(line_1, bytes):
        with open(path, "wb") as f:
            f.write(line_1 + b"\n")
    else:
        with open(path, "w") as f:
            f.write(line_1 + "\n")
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(args) or pytest.ExitCode.OK)
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env())

    assert (code, workers_handed(calls), len(err.splitlines()), path in err) == (0, "8", 1, True), err


def test_4419_the_hermetic_fixture_points_the_ceiling_record_into_the_cases_own_tmp_path(tmp_path):
    assert os.environ["VERI_TEST_CEILING_FILE"].startswith(str(tmp_path) + os.sep)


def test_4457_the_hermetic_fixture_points_the_cap_file_into_the_cases_own_tmp_path(tmp_path):
    assert os.environ["VERI_TEST_CAP_FILE"].startswith(str(tmp_path) + os.sep)


@pytest.mark.parametrize("line_1", [None, "", "six", "1", "0", "-4", "2.5", "٣", b"\xff\xfe"])
def test_4419_with_no_record_or_one_whose_line_1_is_not_a_whole_number_of_at_least_2_a_full_leg_takes_the_cores_and_says_so_in_one_line_naming_the_file_and_make_ceiling(pytest_leg, run_cli, monkeypatch, tmp_path, started, line_1):
    on_cores(monkeypatch, 16)
    record = tmp_path / "ceiling"
    if isinstance(line_1, bytes):
        record.write_bytes(line_1 + b"\n2026-11-18\n")
    elif line_1 is not None:
        record.write_text(line_1 + "\n2026-11-18\n")
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(args) or pytest.ExitCode.OK)
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_TEST_CEILING_FILE=str(record)))
    told = [line for line in err.splitlines() if "make ceiling" in line]

    assert (code, workers_handed(calls), len(told), str(record) in "".join(told)) == (0, "16", 1, True)


def test_4419_a_ceiling_record_path_that_is_a_directory_falls_back_to_the_cores_saying_so_instead_of_crashing(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 16)
    record = tmp_path / "ceiling"
    record.mkdir()
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(args) or pytest.ExitCode.OK)
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_TEST_CEILING_FILE=str(record)))

    assert (code, workers_handed(calls), err.count("make ceiling")) == (0, "16", 1)


def test_4419_on_a_single_core_with_no_record_the_budget_is_never_below_2_so_a_full_leg_alone_takes_2(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 1)
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(args) or pytest.ExitCode.OK)
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env())[0]

    assert (code, workers_handed(calls)) == (0, "2")


def test_4419_with_no_record_on_macos_the_budget_is_the_physical_cores_not_the_logical_ones(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 16, platform="darwin")
    started(extra={"sysctl -n hw.physicalcpu": (0, "8\n", "")})
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(args) or pytest.ExitCode.OK)
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env())[0]

    assert (code, workers_handed(calls)) == (0, "8")


@pytest.mark.parametrize("cap", [[], ["--cap=4"], ["--subset"]], ids=["full", "unit", "subset"])
def test_4419_a_leg_finding_1_worker_of_t_free_waits_with_the_marker_and_one_line_and_starts_only_once_2_are_free(pytest_leg, run_cli, monkeypatch, tmp_path, started, cap):
    import supervise
    on_cores(monkeypatch, 16)
    measured(8)
    legs = tmp_path / "legs"
    legs.mkdir()
    blocker = legs / str(os.getppid())
    registered(blocker, 7)
    marker = tmp_path / "marker"
    polls, seen = [], []

    def the_holder_drops_to_6_on_the_second_poll(seconds):
        polls.append(supervise.lock_waiting(str(marker)))
        if len(polls) == 2:
            registered(blocker, 6)

    monkeypatch.setattr(pytest, "main", lambda args: seen.append((args, blocker.read_text().split("\n")[0])) or pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", the_holder_drops_to_6_on_the_second_poll)
    code, _, err = run_cli(pytest_leg, cap + ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), PYTEST_LEG_LOCK_WAIT_MARKER=str(marker)))

    assert (code, polls, workers_handed([seen[0][0]]), seen[0][1], len(err.splitlines()), marker.exists()) == (0, [True, True], "2", "6", 1, False)


@pytest.mark.parametrize("argv, held, workers", [
    (["--subset"], 0, "4"), (["--subset"], 4, "4"), (["--subset"], 5, "3"),
    (["--cap=4"], 0, "4"), (["--cap=4"], 5, "3"),
    ([], 0, "8"), ([], 2, "6"),
], ids=["subset-alone", "subset-beside-4", "subset-beside-5", "unit-alone", "unit-beside-5", "full-alone", "full-beside-2"])
def test_4419_a_unit_or_subset_leg_takes_min_4_and_the_free_workers_of_t_and_a_full_run_every_free_worker(pytest_leg, run_cli, monkeypatch, tmp_path, started, argv, held, workers):
    on_cores(monkeypatch, 16)
    measured(8)
    legs = tmp_path / "legs"
    legs.mkdir()
    if held:
        registered(legs / str(os.getppid()), held)
    seen = []
    monkeypatch.setattr(pytest, "main", lambda args: seen.append((args, (legs / str(os.getpid())).read_text().split("\n")[0])) or pytest.ExitCode.OK)
    code = run_cli(pytest_leg, argv + ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))[0]

    assert (code, workers_handed([seen[0][0]]), seen[0][1]) == (0, workers, workers)


@pytest.mark.parametrize("record, source", [(True, "the ceiling record"), (False, "the core fallback")], ids=["record", "fallback"])
def test_4419_the_wait_line_names_t_and_its_source_beside_the_workers_in_use_and_the_holding_pids(pytest_leg, run_cli, monkeypatch, tmp_path, started, record, source):
    on_cores(monkeypatch, 12)
    if record:
        measured(8)
    legs = tmp_path / "legs"
    legs.mkdir()
    holder = os.getppid()
    blocker = legs / str(holder)
    registered(blocker, 7 if record else 11)
    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", lambda seconds: blocker.unlink())
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))
    waits = [line for line in err.splitlines() if line.startswith("waiting")]
    t, in_use = ("8", "7") if record else ("12", "11")

    assert (code, len(waits), "T=%s" % t in waits[0], source in waits[0], " %s in use" % in_use in waits[0], str(holder) in waits[0]) == (
        0, 1, True, True, True, True), waits


@pytest.mark.parametrize("record, c0, source", [(True, "8", "the ceiling record"), (False, "12", "the core fallback")], ids=["record", "fallback"])
def test_4457_with_the_cap_below_c0_the_wait_line_names_the_cap_file_as_ts_source_beside_c0_and_c0s_source(pytest_leg, run_cli, monkeypatch, tmp_path, started, record, c0, source):
    on_cores(monkeypatch, 12)
    if record:
        measured(8)
    cap = os.environ["VERI_TEST_CAP_FILE"]
    with open(cap, "w") as f:
        f.write("4\n")
    legs = tmp_path / "legs"
    legs.mkdir()
    blocker = legs / str(os.getppid())
    registered(blocker, 3)
    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", lambda seconds: blocker.unlink())
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))
    waits = [line for line in err.splitlines() if line.startswith("waiting")]

    assert (code, len(waits), "T=4 " in waits[0], cap in waits[0], "C0=%s " % c0 in waits[0], source in waits[0]) == (
        0, 1, True, True, True, True), waits


def test_4419_an_exported_worker_count_is_used_as_given_beside_a_registry_holding_all_of_t_never_waiting_registering_or_reading_the_record(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 16)
    measured(8)
    legs = tmp_path / "legs"
    legs.mkdir()
    registered(legs / str(os.getppid()), 8)
    reads, sleeps, seen = [], [], []
    real_open = open

    def watching_open(path, *args, **kwargs):
        if str(path) == os.environ["VERI_TEST_CEILING_FILE"]:
            reads.append(path)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", watching_open)
    monkeypatch.setattr(pytest_leg.time, "sleep", lambda seconds: sleeps.append(seconds))
    monkeypatch.setattr(pytest, "main", lambda args: seen.append((args, sorted(os.listdir(legs)))) or pytest.ExitCode.OK)
    code, _, err = run_cli(pytest_leg, ["--subset", "-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), VERI_PYTEST_WORKERS="3"))

    assert (code, workers_handed([seen[0][0]]), seen[0][1], sleeps, reads, err) == (0, "3", [str(os.getppid())], [], [], "")


def test_4457_an_exported_worker_count_never_opens_the_cap_file_so_a_bad_one_says_nothing(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 16)
    measured(8)
    cap = os.environ["VERI_TEST_CAP_FILE"]
    with open(cap, "w") as f:
        f.write("six\n")
    reads, seen = [], []
    real_open = open

    def watching_open(path, *args, **kwargs):
        if str(path) == cap:
            reads.append(path)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", watching_open)
    monkeypatch.setattr(pytest, "main", lambda args: seen.append(args) or pytest.ExitCode.OK)
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_WORKERS="12"))

    assert (code, workers_handed(seen), reads, err) == (0, "12", [], "")


def test_4457_with_the_cap_equal_to_c0_the_wait_line_names_c0s_source_not_the_cap_file(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 12)
    measured(8)
    cap = os.environ["VERI_TEST_CAP_FILE"]
    with open(cap, "w") as f:
        f.write("8\n")
    legs = tmp_path / "legs"
    legs.mkdir()
    blocker = legs / str(os.getppid())
    registered(blocker, 7)
    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", lambda seconds: blocker.unlink())
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs)))
    waits = [line for line in err.splitlines() if line.startswith("waiting")]

    assert (code, len(waits), "T=8 (the ceiling record " in waits[0], cap in waits[0], "C0=" in waits[0]) == (
        0, 1, True, False, False), waits


def test_4455_a_leg_waiting_for_t_writes_a_waiter_entry_named_for_its_pid_holding_the_workers_it_waits_for_and_its_start_time_and_starts_with_the_same_workers(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 16)
    measured(8)
    legs = tmp_path / "legs"
    legs.mkdir()
    waiters = tmp_path / "waiters"
    blocker = legs / str(os.getppid())
    registered(blocker, 7)
    entries, seen = [], []

    def the_holder_drops_to_4_on_the_first_poll(seconds):
        entries.append({name: (waiters / name).read_text() for name in os.listdir(waiters)} if waiters.is_dir() else {})
        registered(blocker, 4)

    monkeypatch.setattr(pytest, "main", lambda args: seen.append(args) or pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", the_holder_drops_to_4_on_the_first_poll)
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), VERI_PYTEST_WAITERS=str(waiters)))[0]

    assert (code, entries, workers_handed(seen)) == (0, [{str(os.getpid()): "2\n%s\n" % SELF_STARTED}], "4")


def test_4455_a_legs_waiter_entry_is_gone_once_it_registers_and_starts_pytest(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 16)
    measured(8)
    legs = tmp_path / "legs"
    legs.mkdir()
    waiters = tmp_path / "waiters"
    blocker = legs / str(os.getppid())
    registered(blocker, 7)
    at_start = []

    monkeypatch.setattr(pytest, "main", lambda args: at_start.append(sorted(os.listdir(waiters))) or pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", lambda seconds: blocker.unlink())
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), VERI_PYTEST_WAITERS=str(waiters)))[0]

    assert (code, at_start[:1]) == (0, [[]])


def test_4455_a_leg_ended_by_term_while_it_waits_for_t_has_removed_its_waiter_entry_by_the_time_it_exits(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    import signal

    import idle_watch
    on_cores(monkeypatch, 16)
    measured(8)
    legs = tmp_path / "legs"
    legs.mkdir()
    registered(legs / str(os.getppid()), 8)
    waiters = tmp_path / "waiters"
    entry = waiters / str(os.getpid())
    waiting_at_exit = []

    def exit(code):
        waiting_at_exit.append(entry.exists())
        raise SystemExit(code)

    class Watch(idle_watch.Watch):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, exit=exit, **kwargs)

    def term(seconds):
        assert entry.exists()
        signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)

    monkeypatch.setattr(idle_watch, "Watch", Watch)
    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", term)
    code = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), VERI_PYTEST_WAITERS=str(waiters)))[0]

    assert (code, waiting_at_exit) == (128 + signal.SIGTERM, [False])


def test_4455_a_waiter_entry_the_leg_cannot_write_is_one_stderr_line_naming_it_and_the_wait_goes_on_to_start_pytest(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 16)
    measured(8)
    legs = tmp_path / "legs"
    legs.mkdir()
    blocker = legs / str(os.getppid())
    registered(blocker, 7)
    (tmp_path / "a-file").write_text("")
    waiters = tmp_path / "a-file" / "waiters"
    waited, handed = [], []

    def freed_on_the_second_poll():
        if len(waited) == 2:
            blocker.unlink()

    monkeypatch.setattr(pytest, "main", handed_workers(handed))
    monkeypatch.setattr(pytest_leg.time, "sleep", polls(waited, also=freed_on_the_second_poll))
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), VERI_PYTEST_WAITERS=str(waiters)))
    unlisted = [line for line in err.splitlines() if line.startswith("cannot register the wait")]

    assert (code, len(waited), handed[:1], len(unlisted), str(waiters) in "".join(unlisted)) == (0, 2, ["8"], 1, True), err


def test_4453_a_leg_waiting_under_a_t_narrowed_to_2_starts_with_4_once_its_lane_entry_widens_t_to_6_and_says_the_core_fallback_once(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 10)
    legs = tmp_path / "legs"
    legs.mkdir()
    registered(legs / str(os.getppid()), 2)
    entry = tmp_path / "veri-test-budget" / "main@0123456789abcdef"
    entry.parent.mkdir()
    entry.write_text("2\n%d\n" % (time.time() + 3600))
    polls = []

    def widened_while_it_waits(seconds):
        polls.append(seconds)
        if len(polls) > 3:
            raise RuntimeError("still waiting after T was widened")
        entry.write_text("6\n%d\n" % (time.time() + 3600))

    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(args) or pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", widened_while_it_waits)
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), VERI_TEST_BUDGET_DIR=str(entry.parent)))

    assert (code, workers_handed(calls), len(polls), err.count("`make ceiling`")) == (0, "4", 1, 1), err


def test_4453_a_lane_entry_narrowing_t_to_2_while_a_full_leg_runs_on_10_leaves_its_registry_entry_at_10_and_its_run_unended(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 16)
    measured(10)
    legs = tmp_path / "legs"
    entries = tmp_path / "veri-test-budget"
    entries.mkdir()
    seen = []

    def narrowed_mid_run(args):
        if not seen:
            (entries / "main@0123456789abcdef").write_text("2\n%d\n" % (time.time() + 3600))
            seen.append((args[args.index("-n") + 1], (legs / str(os.getpid())).read_text().split("\n")[0]))
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", narrowed_mid_run)
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), VERI_TEST_BUDGET_DIR=str(entries)))

    assert (code, seen) == (0, [("10", "10")]), err


def test_4453_a_leg_waiting_under_a_t_two_lane_entries_narrow_below_c_names_each_lane_and_need_beside_c_and_its_source(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 16)
    measured(10)
    legs = tmp_path / "legs"
    legs.mkdir()
    holder = legs / str(os.getppid())
    registered(holder, 4)
    entries = tmp_path / "veri-test-budget"
    entries.mkdir()
    (entries / "main@0123456789abcdef").write_text("2\n%d\n" % (time.time() + 3600))
    (entries / "mu@0123456789abcdef").write_text("2\n%d\n" % (time.time() + 3600))
    monkeypatch.setattr(pytest, "main", lambda args: pytest.ExitCode.OK)
    monkeypatch.setattr(pytest_leg.time, "sleep", lambda seconds: holder.unlink(missing_ok=True))
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_LEGS=str(legs), VERI_TEST_BUDGET_DIR=str(entries)))

    assert (code, ["T=4 (the lane entries main=2, mu=2, below C=10 from the ceiling record %s)" % os.environ["VERI_TEST_CEILING_FILE"] in line
                   for line in err.splitlines()]) == (0, [True]), err


def test_4453_with_veri_pytest_workers_3_exported_the_leg_takes_3_beside_a_lane_entry_needing_2_and_leaves_an_expired_one_in_place(pytest_leg, run_cli, monkeypatch, tmp_path, started):
    on_cores(monkeypatch, 16)
    measured(10)
    entries = tmp_path / "veri-test-budget"
    entries.mkdir()
    (entries / "main@0123456789abcdef").write_text("2\n%d\n" % (time.time() + 3600))
    (entries / "mu@0123456789abcdef").write_text("4\n%d\n" % (time.time() - 1))
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(args) or pytest.ExitCode.OK)
    code, _, err = run_cli(pytest_leg, ["-q", "some/dir"], env=leg_env(VERI_PYTEST_WORKERS="3", VERI_TEST_BUDGET_DIR=str(entries)))

    assert (code, workers_handed(calls), sorted(os.listdir(entries))) == (0, "3", ["main@0123456789abcdef", "mu@0123456789abcdef"]), err


def test_4453_a_lone_lane_entry_needing_0_under_a_ceiling_record_of_10_narrows_t_to_its_floor_of_2(pytest_leg, monkeypatch, tmp_path):
    on_cores(monkeypatch, 16)
    measured(10)
    entries = tmp_path / "veri-test-budget"
    entries.mkdir()
    (entries / "main@0123456789abcdef").write_text("0\n%d\n" % (time.time() + 3600))
    monkeypatch.setenv("VERI_TEST_BUDGET_DIR", str(entries))

    assert pytest_leg.budget(say=False)[0] == 2


def test_4855_with_keep_run_dir_unset_leaving_run_directory_removes_it_and_a_file_planted_under_its_base(pytest_leg, monkeypatch, tmp_path):
    import tempfile
    monkeypatch.delenv("VERI_PYTEST_KEEP_RUN_DIR", raising=False)
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(sys, "pycache_prefix", None)

    with pytest_leg.run_directory() as run:
        planted = os.path.join(run, "base", "case0", "left.txt")
        os.makedirs(os.path.dirname(planted))
        with open(planted, "w") as f:
            f.write("x")

    assert (run.startswith(str(tmp_path)), os.path.exists(planted), os.path.exists(run)) == (True, False, False)


def test_4855_with_keep_run_dir_1_leaving_run_directory_leaves_it_and_a_file_planted_under_its_base(pytest_leg, monkeypatch, tmp_path):
    import tempfile
    monkeypatch.setenv("VERI_PYTEST_KEEP_RUN_DIR", "1")
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(sys, "pycache_prefix", None)

    with pytest_leg.run_directory() as run:
        planted = os.path.join(run, "base", "case0", "left.txt")
        os.makedirs(os.path.dirname(planted))
        with open(planted, "w") as f:
            f.write("x")

    assert (run.startswith(str(tmp_path)), os.path.exists(planted), os.path.exists(run)) == (True, True, True)


def test_4855_with_keep_run_dir_set_to_anything_but_1_leaving_run_directory_still_removes_it(pytest_leg, monkeypatch, tmp_path):
    import tempfile
    monkeypatch.setenv("VERI_PYTEST_KEEP_RUN_DIR", "yes")
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(sys, "pycache_prefix", None)

    with pytest_leg.run_directory() as run:
        planted = os.path.join(run, "base", "case0", "left.txt")
        os.makedirs(os.path.dirname(planted))
        with open(planted, "w") as f:
            f.write("x")

    assert (run.startswith(str(tmp_path)), os.path.exists(planted), os.path.exists(run)) == (True, False, False)


def test_4855_with_keep_run_dir_1_leaving_run_directory_still_removes_its_bytecode_mirror(pytest_leg, monkeypatch, tmp_path):
    import tempfile
    prefix = tmp_path / "pycache"
    prefix.mkdir()
    (tmp_path / "runs").mkdir()
    monkeypatch.setenv("VERI_PYTEST_KEEP_RUN_DIR", "1")
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path / "runs"))
    monkeypatch.setattr(sys, "pycache_prefix", str(prefix))

    with pytest_leg.run_directory() as run:
        mirror = os.path.join(str(prefix), run.lstrip(os.sep))
        os.makedirs(mirror)

    assert os.path.exists(mirror) is False


def test_4855_with_keep_run_dir_1_the_leg_leaves_its_run_directory_in_place_after_main_returns(pytest_leg, run_cli, monkeypatch, tmp_path):
    import tempfile

    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    monkeypatch.setattr(sys, "pycache_prefix", None)
    planted = []

    def spy(args):
        base = next(arg for arg in args if arg.startswith("--basetemp="))[len("--basetemp="):]
        path = os.path.join(base, "case0", "left.txt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("x")
        planted.append(path)
        return pytest.ExitCode.OK

    monkeypatch.setattr(pytest, "main", spy)
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1",
           "VERI_PYTEST_WORKERS": "1", "VERI_PYTEST_KEEP_RUN_DIR": "1"}
    code = run_cli(pytest_leg, [], env=env)[0]

    run = os.path.dirname(os.path.dirname(os.path.dirname(planted[0])))
    assert (code, run.startswith(str(tmp_path)), os.path.exists(planted[0]), os.path.isdir(run)) == (0, True, True, True)
