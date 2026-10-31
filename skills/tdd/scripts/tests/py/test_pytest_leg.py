"""In-process cases for veri/pytest_leg.py, the launcher that makes the pytest leg's refusals and then runs pytest."""
import importlib
import os
import sys

import pytest


@pytest.fixture
def pytest_leg():
    return importlib.import_module("veri.pytest_leg")


def leg_env(**extra):
    """The env a case hands the launcher to pass its three importable checks, plus the case's own variables."""
    return {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", **extra}


def without_selection(args):
    return importlib.import_module("veri.pytest_leg").split_marks(args)[0]


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


@pytest.mark.process("a launcher child that receives SIGINT or SIGTERM during its pytest run")
def test_a_launcher_run_interrupted_by_sigint_or_sigterm_leaves_no_base_directory_behind(tmp_path):
    import os
    import signal
    import subprocess

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    child = (
        "import os, sys\n"
        "sys.path[:0] = [%r, %r]\n"
        "import pytest\n"
        "from veri import pytest_leg\n"
        "def spy(args):\n"
        "    base = [a.split('=', 1)[1] for a in args if a.startswith('--basetemp=')][0]\n"
        "    open(sys.argv[1], 'w').write(base)\n"
        "    os.kill(os.getpid(), int(sys.argv[2]))\n"
        "    return pytest.ExitCode.OK\n"
        "pytest.main = spy\n"
        "sys.exit(pytest_leg.main([]))\n"
    ) % (scripts, os.path.join(scripts, "veri"))
    env = dict(os.environ, VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1")
    left = {}
    for sig in (signal.SIGINT, signal.SIGTERM):
        record = tmp_path / ("base-%d" % sig)
        subprocess.run([sys.executable, "-c", child, str(record), str(int(sig))], env=env, capture_output=True, timeout=30)
        base = record.read_text()
        left[sig.name] = os.path.exists(base)
    assert left == {"SIGINT": False, "SIGTERM": False}


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


@pytest.mark.process("a launcher child that receives SIGHUP or SIGTERM during its pytest run")
def test_2184_a_launcher_run_sent_sighup_during_its_pytest_run_leaves_no_veri_pytest_folder_and_exits_as_on_sigterm(tmp_path):
    import os
    import signal
    import subprocess

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    child = (
        "import os, sys\n"
        "sys.path[:0] = [%r, %r]\n"
        "import pytest\n"
        "from veri import pytest_leg\n"
        "def spy(args):\n"
        "    os.kill(os.getpid(), int(sys.argv[1]))\n"
        "    return pytest.ExitCode.OK\n"
        "pytest.main = spy\n"
        "sys.exit(pytest_leg.main([]))\n"
    ) % (scripts, os.path.join(scripts, "veri"))
    outcome = {}
    for sig in (signal.SIGTERM, signal.SIGHUP):
        scratch = tmp_path / sig.name
        scratch.mkdir()
        env = dict(os.environ, VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1",
                   VERI_PYTEST_XDIST_IMPORTABLE="1", VERI_PYTEST_WORKERS="1", TMPDIR=str(scratch))
        done = subprocess.run([sys.executable, "-c", child, str(int(sig))], env=env, capture_output=True, timeout=30)
        outcome[sig.name] = (sorted(os.listdir(scratch)), done.returncode)
    assert (outcome["SIGTERM"], outcome["SIGHUP"]) == (([], 143), ([], 129))


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


@pytest.mark.process("the launcher run as a child over a planted tests tree holding a small case that starts git")
def test_a_small_case_that_starts_git_fails_under_the_launcher_with_its_failure_naming_git_and_no_unit_guard_shim_on_path(tmp_path):
    import os
    import subprocess

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "test_starts_git.py").write_text(
        "import subprocess\n"
        "\n"
        "def test_runs_git():\n"
        "    subprocess.run(['git', '--version'], capture_output=True)\n"
    )
    path = os.environ["PATH"]
    done = subprocess.run(
        [sys.executable, "-c", "import runpy, sys; sys.argv[0] = sys.argv.pop(1); runpy.run_path(sys.argv[0], run_name='__main__')",
         os.path.join(scripts, "veri", "pytest_leg.py"), "-q", "-p", "no:cacheprovider", str(planted)],
        cwd=tmp_path, env=dict(os.environ, VERI_PYTEST_WORKERS="1", PATH=path, PYTHONPATH=os.path.join(scripts, "veri")), capture_output=True, text=True, timeout=60,
    )
    assert done.returncode == 1
    assert "git" in (done.stdout + done.stderr).split("test_runs_git", 1)[-1]


@pytest.mark.process("the launcher run as a child over a planted tests tree holding small cases that start python3")
def test_a_small_case_that_starts_python3_on_a_script_outside_veri_fails_naming_python3_while_one_on_a_veri_module_is_not_refused(tmp_path):
    import os
    import subprocess

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    veri = os.path.join(scripts, "veri")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "python3").symlink_to(sys.executable)
    outside = tmp_path / "outside.py"
    outside.write_text("")
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "test_starts_python3.py").write_text(
        "import subprocess\n"
        "\n"
        "def test_runs_python3_outside_veri():\n"
        "    subprocess.run(['python3', %r], capture_output=True)\n"
        "\n"
        "def test_runs_python3_on_a_veri_module():\n"
        "    subprocess.run(['python3', %r], capture_output=True)\n"
        % (str(outside), os.path.join(veri, "small_case_guard.py"))
    )
    path = os.pathsep.join([str(bin_dir), os.environ["PATH"]])
    done = subprocess.run(
        [sys.executable, "-c", "import runpy, sys; sys.argv[0] = sys.argv.pop(1); runpy.run_path(sys.argv[0], run_name='__main__')",
         os.path.join(veri, "pytest_leg.py"), "-q", "-p", "no:cacheprovider", str(planted)],
        cwd=tmp_path, env=dict(os.environ, VERI_PYTEST_WORKERS="1", PATH=path, PYTHONPATH=veri), capture_output=True, text=True, timeout=60,
    )
    out = done.stdout + done.stderr
    assert "1 failed, 1 passed" in out
    assert "python3" in out.split("test_runs_python3_outside_veri", 1)[-1]
    assert "FAILED test_starts_python3.py::test_runs_python3_on_a_veri_module" not in out


@pytest.mark.process("the launcher run as a child over a planted tests tree holding cases that reach the network and start gh and curl")
def test_a_case_that_connects_to_a_non_loopback_address_or_starts_gh_or_curl_fails_naming_it_with_no_offline_shim_on_path_while_a_loopback_connection_works(tmp_path):
    import os
    import subprocess

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    veri = os.path.join(scripts, "veri")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("gh", "curl"):
        stub = bin_dir / name
        stub.write_text("#!/bin/sh\ntouch %s\n" % (tmp_path / ("ran-" + name)))
        stub.chmod(0o755)
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "test_reaches_out.py").write_text(
        "import socket\n"
        "import subprocess\n"
        "\n"
        "def test_reaches_a_remote_address():\n"
        "    try:\n"
        "        socket.create_connection(('192.0.2.1', 80), timeout=0.2)\n"
        "    except OSError:\n"
        "        pass\n"
        "\n"
        "def test_starts_gh():\n"
        "    subprocess.run(['gh', 'issue', 'list'])\n"
        "\n"
        "def test_starts_curl():\n"
        "    subprocess.run(['curl', 'http://example.invalid'])\n"
        "\n"
        "def test_reaches_loopback():\n"
        "    server = socket.socket()\n"
        "    server.bind(('127.0.0.1', 0))\n"
        "    server.listen(1)\n"
        "    socket.create_connection(server.getsockname(), timeout=2).close()\n"
        "    server.close()\n"
    )
    path = os.pathsep.join([str(bin_dir), os.environ["PATH"]])
    done = subprocess.run(
        [sys.executable, "-c", "import runpy, sys; sys.argv[0] = sys.argv.pop(1); runpy.run_path(sys.argv[0], run_name='__main__')",
         os.path.join(veri, "pytest_leg.py"), "-q", "-p", "no:cacheprovider", str(planted)],
        cwd=tmp_path, env=dict(os.environ, VERI_PYTEST_WORKERS="1", PATH=path, PYTHONPATH=veri), capture_output=True, text=True, timeout=60,
    )
    out = done.stdout + done.stderr
    assert "3 failed, 1 passed" in out
    assert "192.0.2.1" in out.split("test_reaches_a_remote_address", 1)[-1]
    assert "gh" in out.split("test_starts_gh", 1)[-1]
    assert "curl" in out.split("test_starts_curl", 1)[-1]
    assert not (tmp_path / "ran-gh").exists() and not (tmp_path / "ran-curl").exists()


@pytest.mark.process("the launcher run as a child over a planted tests tree whose cases start a gh and a curl they planted under their own basetemp")
def test_a_gh_or_curl_stub_a_case_plants_under_the_run_s_basetemp_starts_and_passes_the_network_guard(tmp_path):
    import os
    import subprocess

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    veri = os.path.join(scripts, "veri")
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "test_starts_its_own_stubs.py").write_text(
        "import os\n"
        "import subprocess\n"
        "\n"
        "def stub(directory, name):\n"
        "    directory.mkdir(exist_ok=True)\n"
        "    path = directory / name\n"
        "    path.write_text('#!/bin/sh\\ntouch ' + os.path.join(%r, 'ran-' + name) + '\\n')\n"
        "    path.chmod(0o755)\n"
        "\n"
        "def test_starts_a_gh_found_on_its_own_path(tmp_path):\n"
        "    stub(tmp_path / 'bin', 'gh')\n"
        "    subprocess.run(['gh', 'issue', 'list'], env=dict(os.environ, PATH=str(tmp_path / 'bin') + os.pathsep + os.environ['PATH']), check=True)\n"
        "\n"
        "def test_starts_a_curl_by_its_full_path(tmp_path):\n"
        "    stub(tmp_path / 'bin', 'curl')\n"
        "    subprocess.run([str(tmp_path / 'bin' / 'curl'), 'http://example.invalid'], check=True)\n"
        % str(tmp_path)
    )
    done = subprocess.run(
        [sys.executable, "-c", "import runpy, sys; sys.argv[0] = sys.argv.pop(1); runpy.run_path(sys.argv[0], run_name='__main__')",
         os.path.join(veri, "pytest_leg.py"), "-q", "-p", "no:cacheprovider", str(planted)],
        cwd=tmp_path, env=dict(os.environ, VERI_PYTEST_WORKERS="1", PYTHONPATH=veri), capture_output=True, text=True, timeout=60,
    )
    out = done.stdout + done.stderr
    assert "2 passed" in out and "failed" not in out
    assert (tmp_path / "ran-gh").exists() and (tmp_path / "ran-curl").exists()


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


PLANTED_CONFTEST = """\
import os


def pytest_configure(config):
    config.addinivalue_line("markers", "serial(reason): planted")


def pytest_sessionstart(session):
    if not hasattr(session.config, "workerinput"):
        with open(os.environ["PLANTED_LOG"], "a") as log:
            log.write("session\\n")
"""

PLANTED_RAN = """\
import os

import pytest


def ran(name):
    with open(os.environ["PLANTED_LOG"]) as log:
        sessions = log.read().split().count("session")
    with open(os.environ["PLANTED_LOG"], "a") as log:
        log.write("%s session=%d worker=%s\\n" % (name, sessions, "xdist" if os.environ.get("PYTEST_XDIST_WORKER") else "none"))
"""


def run_the_real_leg_over(run_cli, tmp_path, cases, selection=()):
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "conftest.py").write_text(PLANTED_CONFTEST)
    (planted / "test_planted.py").write_text(PLANTED_RAN + cases)
    log = tmp_path / "ran.log"
    env = leg_env(VERI_PYTEST_WORKERS="2", PLANTED_LOG=str(log))
    try:
        code, out, err = run_cli(importlib.import_module("veri.pytest_leg"), ["-q", "-p", "no:cacheprovider", *selection, str(planted)], env=env)
    finally:
        sys.modules.pop("test_planted", None)  # an in-process session imports it; the next planted tree's would mismatch
    return code, log.read_text().splitlines(), out + err


@pytest.mark.process("the real leg's parallel pass starts two xdist worker processes over a planted tree")
def test_the_real_leg_runs_the_unmarked_case_on_xdist_workers_in_the_first_session_and_the_serial_case_alone_in_a_second_2092(run_cli, tmp_path):
    code, log, output = run_the_real_leg_over(run_cli, tmp_path, (
        "\n\ndef test_unmarked():\n    ran('unmarked')\n"
        "\n\n@pytest.mark.serial('planted')\ndef test_serial():\n    ran('serial')\n"
    ))

    assert (code, log) == (0, ["session", "unmarked session=1 worker=xdist", "session", "serial session=2 worker=none"]), output


@pytest.mark.process("the real leg's parallel pass starts two xdist worker processes over a planted tree")
def test_the_real_leg_over_a_tree_with_no_serial_marked_case_starts_one_session_only_2092(run_cli, tmp_path):
    code, log, output = run_the_real_leg_over(run_cli, tmp_path, "\n\ndef test_unmarked():\n    ran('unmarked')\n")

    assert (code, log) == (0, ["session", "unmarked session=1 worker=xdist"]), output


@pytest.mark.process("the real leg's parallel pass starts two xdist worker processes over a planted tree")
@pytest.mark.parametrize("selection", [["-m", "not serial"], ["-k", "test_unmarked"]])
def test_a_caller_selection_that_filters_the_serial_case_out_never_runs_it_yet_the_leg_starts_a_second_session_that_runs_nothing_and_exits_0_2092(run_cli, tmp_path, selection):
    code, log, output = run_the_real_leg_over(run_cli, tmp_path, (
        "\n\ndef test_unmarked():\n    ran('unmarked')\n"
        "\n\n@pytest.mark.serial('planted')\ndef test_serial():\n    ran('serial')\n"
    ), selection)

    assert (code, log) == (0, ["session", "unmarked session=1 worker=xdist", "session"]), output


INTERNALERROR_CONFTEST = """\
failed = []


def pytest_runtest_logreport(report):
    if failed:
        raise RuntimeError("controller broke after a failure")
    if report.failed:
        failed.append(report.nodeid)
"""


@pytest.mark.process("the real leg's parallel pass starts two xdist worker processes over a planted tree")
def test_2741_a_leg_whose_xdist_run_ends_in_an_internalerror_after_a_case_failed_names_that_case_says_the_leg_was_cut_short_and_exits_non_zero(run_cli, tmp_path):
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "conftest.py").write_text(INTERNALERROR_CONFTEST)
    (planted / "test_planted.py").write_text("def test_fails():\n    assert False\n")
    env = leg_env(VERI_PYTEST_WORKERS="2")
    try:
        code, out, err = run_cli(importlib.import_module("veri.pytest_leg"), ["-q", "-p", "no:cacheprovider", str(planted)], env=env)
    finally:
        sys.modules.pop("test_planted", None)
        sys.modules.pop("conftest", None)

    assert (code != 0, "test_planted.py::test_fails" in out + err, "cut short" in err) == (True, True, True), out + err


@pytest.mark.process("the real leg's parallel pass starts two xdist worker processes over a planted tree")
def test_2741_a_leg_cut_short_by_an_internalerror_names_only_the_cases_that_failed_not_a_passing_one(run_cli, tmp_path):
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "conftest.py").write_text(INTERNALERROR_CONFTEST)
    (planted / "test_planted.py").write_text("def test_fails():\n    assert False\n\n\ndef test_passes_quietly():\n    pass\n")
    env = leg_env(VERI_PYTEST_WORKERS="2")
    try:
        code, out, err = run_cli(importlib.import_module("veri.pytest_leg"), ["-q", "-p", "no:cacheprovider", str(planted)], env=env)
    finally:
        sys.modules.pop("test_planted", None)
        sys.modules.pop("conftest", None)

    listed = [line for line in (out + err).splitlines() if "test_planted.py::" in line]
    assert (code != 0, any("test_fails" in line for line in listed), any("test_passes_quietly" in line for line in listed)) == (True, True, False), out + err


@pytest.mark.process("the real leg's parallel pass starts two xdist worker processes over a planted tree")
def test_2741_a_leg_whose_xdist_run_ends_in_an_internalerror_says_on_stderr_that_it_was_cut_short(run_cli, tmp_path):
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "conftest.py").write_text(INTERNALERROR_CONFTEST)
    (planted / "test_planted.py").write_text("def test_fails():\n    assert False\n")
    env = leg_env(VERI_PYTEST_WORKERS="2")
    try:
        code, out, err = run_cli(importlib.import_module("veri.pytest_leg"), ["-q", "-p", "no:cacheprovider", str(planted)], env=env)
    finally:
        sys.modules.pop("test_planted", None)
        sys.modules.pop("conftest", None)

    assert "cut short" in err, out + err


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


@pytest.mark.process("the launcher run as a child over a planted tests tree whose case reports its own tmp_path")
def test_2051_a_case_s_tmp_path_under_the_launcher_is_the_private_tmp_path_directory_of_mode_0700_under_the_run_s_basetemp_not_a_numbered_one(tmp_path):
    import os
    import stat
    import subprocess

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    veri = os.path.join(scripts, "veri")
    planted = tmp_path / "planted"
    planted.mkdir()
    report = tmp_path / "report"
    (planted / "test_reports_its_tmp_path.py").write_text(
        "import os\n"
        "import stat\n"
        "\n"
        "def test_probe(tmp_path):\n"
        "    open(%r, 'w').write('\\n'.join([tmp_path.name, tmp_path.parent.parent.name, oct(stat.S_IMODE(os.stat(tmp_path).st_mode))]))\n"
        % str(report)
    )
    done = subprocess.run(
        [sys.executable, "-c", "import runpy, sys; sys.argv[0] = sys.argv.pop(1); runpy.run_path(sys.argv[0], run_name='__main__')",
         os.path.join(veri, "pytest_leg.py"), "-q", "-p", "no:cacheprovider", str(planted)],
        cwd=tmp_path, env=dict(os.environ, VERI_PYTEST_WORKERS="1", PYTHONPATH=veri), capture_output=True, text=True, timeout=60,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    name, parent, mode = report.read_text().split("\n")
    assert parent.startswith("veri-pytest-")
    assert mode == "0o700"
    assert name.startswith("test_probe_") and len(name) > len("test_probe_")


LOCK_CHILD = """\
import os, sys
sys.path[:0] = [%r, %r]
import pytest
from veri import pytest_leg
name, marks, release = sys.argv[1:4]
def spy(args):
    open(os.path.join(marks, name + "-started"), "a").close()
    while name == "A" and not os.path.exists(release):
        pass
    return pytest.ExitCode.OK
pytest.main = spy
sys.exit(pytest_leg.main([]))
"""


@pytest.mark.process("two launcher children run as full runs from different working trees, sharing one home")
@pytest.mark.timeout(60)
def test_2195_a_second_full_run_waits_for_the_first_saying_once_who_holds_the_lock_then_runs_and_exits_as_its_suites_decide(tmp_path):
    import subprocess
    import time

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    child = LOCK_CHILD % (scripts, os.path.join(scripts, "veri"))
    home, marks, release = tmp_path / "home", tmp_path / "marks", tmp_path / "release"
    for directory in (home, marks, tmp_path / "treeA", tmp_path / "treeB"):
        directory.mkdir()
    env = dict(os.environ, HOME=str(home), VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1", VERI_PYTEST_XDIST_IMPORTABLE="1")

    def launch(name):
        err = open(tmp_path / (name + ".err"), "w")
        return subprocess.Popen([sys.executable, "-c", child, name, str(marks), str(release)],
                                cwd=tmp_path / ("tree" + name), env=env, stdout=subprocess.DEVNULL, stderr=err)

    def until(done):
        deadline = time.monotonic() + 15
        while not done() and time.monotonic() < deadline:
            time.sleep(0.05)

    first = launch("A")
    until(lambda: (marks / "A-started").exists())
    second = launch("B")
    until(lambda: (marks / "B-started").exists() or (tmp_path / "B.err").stat().st_size > 0)
    second_started_while_first_held = (marks / "B-started").exists()
    release.touch()
    codes = (first.wait(timeout=30), second.wait(timeout=30))
    waiting = (tmp_path / "B.err").read_text()
    assert (second_started_while_first_held, codes) == (False, (0, 0))
    assert len(waiting.splitlines()) == 1
    assert str(first.pid) in waiting and os.path.realpath(tmp_path / "treeA") in waiting
    assert (marks / "B-started").exists()


EXIT_CHILD = """\
import os, sys, time
sys.path[:0] = [%r, %r]
import pytest
from veri import pytest_leg
name, marks, release, status = sys.argv[1:5]
def spy(args):
    open(os.path.join(marks, name + "-started"), "a").close()
    while name == "A" and not os.path.exists(release):
        time.sleep(0.01)
    return pytest.ExitCode[status] if name == "A" else pytest.ExitCode.OK
pytest.main = spy
sys.exit(pytest_leg.main([]))
"""


@pytest.mark.process("two launcher children run as full runs sharing one home, the first ended each way the lock must survive")
@pytest.mark.parametrize("ending", ["exits_ok", "exits_red", "SIGTERM", "SIGINT", "SIGHUP"])
@pytest.mark.timeout(60)
def test_2195_a_waiting_full_run_starts_its_suites_after_the_holder_exits_normally_exits_red_or_is_ended_by_a_signal(tmp_path, ending):
    import signal
    import subprocess
    import time

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    child = EXIT_CHILD % (scripts, os.path.join(scripts, "veri"))
    home, marks, release = tmp_path / "home", tmp_path / "marks", tmp_path / "release"
    for directory in (home, marks, tmp_path / "treeA", tmp_path / "treeB"):
        directory.mkdir()
    env = dict(os.environ, HOME=str(home), VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1", VERI_PYTEST_XDIST_IMPORTABLE="1")

    def launch(name, status):
        err = open(tmp_path / (name + ".err"), "w")
        return subprocess.Popen([sys.executable, "-c", child, name, str(marks), str(release), status],
                                cwd=tmp_path / ("tree" + name), env=env, stdout=subprocess.DEVNULL, stderr=err)

    def until(done):
        deadline = time.monotonic() + 15
        while not done() and time.monotonic() < deadline:
            time.sleep(0.05)

    first = launch("A", "TESTS_FAILED" if ending == "exits_red" else "OK")
    until(lambda: (marks / "A-started").exists())
    second = launch("B", "OK")
    until(lambda: (marks / "B-started").exists() or (tmp_path / "B.err").stat().st_size > 0)
    if ending.startswith("exits"):
        release.touch()
    else:
        first.send_signal(getattr(signal, ending))
    first.wait(timeout=30)
    until(lambda: (marks / "B-started").exists())
    started_after_holder_ended = (marks / "B-started").exists()
    if not started_after_holder_ended:
        second.kill()
    assert (started_after_holder_ended, second.wait(timeout=30)) == (True, 0)


NESTED_CHILD = """\
import os, subprocess, sys
sys.path[:0] = [%r, %r]
import pytest
from veri import pytest_leg
name, marks = sys.argv[1:3]
def spy(args):
    open(os.path.join(marks, name + "-started"), "a").close()
    if name == "outer":
        env = {k: v for k, v in os.environ.items() if not k.startswith("VERI_")}
        nested = subprocess.Popen([sys.executable, sys.argv[0], "nested", marks], env=env)
        try:
            code = nested.wait(timeout=20)
        except subprocess.TimeoutExpired:
            nested.kill()
            code = "waited"
        open(os.path.join(marks, "nested-exit"), "w").write(str(code))
    return pytest.ExitCode.OK
pytest.main = spy
sys.exit(pytest_leg.main([]))
"""


@pytest.mark.process("a launcher child run as a full run starts a second full run nested under it, its environment stripped of VERI_*")
@pytest.mark.timeout(60)
def test_2195_a_full_run_started_under_the_full_run_holding_the_lock_skips_the_lock_and_runs_its_suites_at_once(tmp_path):
    import subprocess

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    child = tmp_path / "child.py"
    child.write_text(NESTED_CHILD % (scripts, os.path.join(scripts, "veri")))
    home, marks = tmp_path / "home", tmp_path / "marks"
    for directory in (home, marks):
        directory.mkdir()
    env = {k: v for k, v in os.environ.items() if k != "VERI_PYTEST_LEGS"}
    env.update(HOME=str(home), VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1", VERI_PYTEST_XDIST_IMPORTABLE="1")
    outer = subprocess.run([sys.executable, str(child), "outer", str(marks)], cwd=tmp_path, env=env,
                           stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=45)

    assert (outer.returncode, (marks / "nested-exit").read_text()) == (0, "0"), outer.stderr
    assert (marks / "nested-started").exists()
    assert "waiting for the full run" not in outer.stderr


@pytest.mark.process("two launcher children run as full runs sharing one home, the second with VERI_TEST_LOCK=0 while the first holds the lock")
@pytest.mark.timeout(60)
def test_2195_a_full_run_started_with_veri_test_lock_0_starts_its_suites_at_once_beside_a_live_holder_and_writes_no_waiting_message(tmp_path):
    import subprocess
    import time

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    child = LOCK_CHILD % (scripts, os.path.join(scripts, "veri"))
    home, marks, release = tmp_path / "home", tmp_path / "marks", tmp_path / "release"
    for directory in (home, marks, tmp_path / "treeA", tmp_path / "treeB"):
        directory.mkdir()
    env = dict(os.environ, HOME=str(home), VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1", VERI_PYTEST_XDIST_IMPORTABLE="1")

    def launch(name, extra):
        err = open(tmp_path / (name + ".err"), "w")
        return subprocess.Popen([sys.executable, "-c", child, name, str(marks), str(release)],
                                cwd=tmp_path / ("tree" + name), env=dict(env, **extra), stdout=subprocess.DEVNULL, stderr=err)

    def until(done):
        deadline = time.monotonic() + 15
        while not done() and time.monotonic() < deadline:
            time.sleep(0.05)

    first = launch("A", {})
    until(lambda: (marks / "A-started").exists())
    second = launch("B", {"VERI_TEST_LOCK": "0"})
    until(lambda: (marks / "B-started").exists() or (tmp_path / "B.err").stat().st_size > 0)
    started_while_first_held = (marks / "B-started").exists()
    release.touch()
    codes = (first.wait(timeout=30), second.wait(timeout=30))
    assert (started_while_first_held, codes) == (True, (0, 0))
    assert "waiting" not in (tmp_path / "B.err").read_text()


@pytest.mark.process("two launcher children run as full runs sharing one home, the first SIGKILLed while it holds the lock")
@pytest.mark.timeout(60)
def test_2195_a_full_run_started_after_the_holder_was_sigkilled_takes_the_lock_over_without_waiting_and_runs_its_suites(tmp_path):
    import signal
    import subprocess
    import time

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    child = LOCK_CHILD % (scripts, os.path.join(scripts, "veri"))
    home, marks, release = tmp_path / "home", tmp_path / "marks", tmp_path / "release"
    for directory in (home, marks, tmp_path / "treeA", tmp_path / "treeB"):
        directory.mkdir()
    env = dict(os.environ, HOME=str(home), VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1", VERI_PYTEST_XDIST_IMPORTABLE="1")

    def launch(name):
        err = open(tmp_path / (name + ".err"), "w")
        return subprocess.Popen([sys.executable, "-c", child, name, str(marks), str(release)],
                                cwd=tmp_path / ("tree" + name), env=env, stdout=subprocess.DEVNULL, stderr=err)

    def until(done):
        deadline = time.monotonic() + 15
        while not done() and time.monotonic() < deadline:
            time.sleep(0.05)

    first = launch("A")
    until(lambda: (marks / "A-started").exists())
    first.send_signal(signal.SIGKILL)
    first.wait(timeout=30)
    second = launch("B")
    until(lambda: (marks / "B-started").exists())
    started = (marks / "B-started").exists()
    if not started:
        second.kill()
    code = second.wait(timeout=30)
    assert (started, code) == (True, 0)
    assert "waiting" not in (tmp_path / "B.err").read_text()


@pytest.mark.process("two launcher children, the first a full run holding the lock and the second a fast-tier run, sharing one home")
@pytest.mark.timeout(60)
def test_2195_a_fast_tier_run_starts_its_suites_at_once_beside_a_live_full_run_holder_and_writes_no_waiting_message(tmp_path):
    import subprocess
    import time

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    child = LOCK_CHILD % (scripts, os.path.join(scripts, "veri"))
    fast_child = child.replace("pytest_leg.main([])", "pytest_leg.main(['-m', 'not process and not tree_audit'] if name == 'B' else [])")
    home, marks, release = tmp_path / "home", tmp_path / "marks", tmp_path / "release"
    for directory in (home, marks, tmp_path / "treeA", tmp_path / "treeB"):
        directory.mkdir()
    env = dict(os.environ, HOME=str(home), VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1", VERI_PYTEST_XDIST_IMPORTABLE="1")

    def launch(name):
        err = open(tmp_path / (name + ".err"), "w")
        return subprocess.Popen([sys.executable, "-c", fast_child, name, str(marks), str(release)],
                                cwd=tmp_path / ("tree" + name), env=env, stdout=subprocess.DEVNULL, stderr=err)

    def until(done):
        deadline = time.monotonic() + 15
        while not done() and time.monotonic() < deadline:
            time.sleep(0.05)

    first = launch("A")
    until(lambda: (marks / "A-started").exists())
    second = launch("B")
    until(lambda: (marks / "B-started").exists() or (tmp_path / "B.err").stat().st_size > 0)
    started_while_first_held = (marks / "B-started").exists()
    release.touch()
    codes = (first.wait(timeout=30), second.wait(timeout=30))
    assert (started_while_first_held, codes) == (True, (0, 0))
    assert "waiting" not in (tmp_path / "B.err").read_text()


WAIT_CHILD = """\
import os, sys, time
sys.path[:0] = [%r, %r]
import pytest
from veri import pytest_leg
name, marks, release, planted = sys.argv[1:5]
def spy(args):
    open(os.path.join(marks, name + "-started"), "a").close()
    while not os.path.exists(release):
        time.sleep(0.01)
    return pytest.ExitCode.OK
if name == "A":
    pytest.main = spy
sys.exit(pytest_leg.main(["--timeout=1", "-q", "-p", "no:cacheprovider", planted] if name == "B" else []))
"""


@pytest.mark.process("two launcher children run as full runs sharing one home, the second a real pytest session with a 1 s case limit, waiting on the first")
@pytest.mark.timeout(60)
def test_2195_a_waiting_full_run_with_a_1_s_case_limit_passes_once_a_holder_that_held_the_lock_over_1_s_releases_it(tmp_path):
    import subprocess
    import time

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    child = WAIT_CHILD % (scripts, os.path.join(scripts, "veri"))
    home, marks, release, planted = tmp_path / "home", tmp_path / "marks", tmp_path / "release", tmp_path / "planted"
    for directory in (home, marks, planted, tmp_path / "treeA", tmp_path / "treeB"):
        directory.mkdir()
    (planted / "test_planted.py").write_text(
        "import os, time\n"
        "def test_starts_only_after_the_holder_released():\n"
        "    assert os.path.exists(%r)\n"
        "    time.sleep(0.5)\n" % str(release))
    env = dict(os.environ, HOME=str(home), VERI_PYTEST_WORKERS="1", VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1", VERI_PYTEST_XDIST_IMPORTABLE="1")

    def launch(name):
        out = open(tmp_path / (name + ".out"), "w")
        return subprocess.Popen([sys.executable, "-c", child, name, str(marks), str(release), str(planted)],
                                cwd=tmp_path / ("tree" + name), env=env, stdout=out, stderr=subprocess.STDOUT)

    def until(done):
        deadline = time.monotonic() + 15
        while not done() and time.monotonic() < deadline:
            time.sleep(0.05)

    first = launch("A")
    until(lambda: (marks / "A-started").exists())
    second = launch("B")
    until(lambda: "waiting for the full run holding the lock" in (tmp_path / "B.out").read_text())
    time.sleep(1.5)
    release.touch()
    codes = (first.wait(timeout=30), second.wait(timeout=30))
    output = (tmp_path / "B.out").read_text()
    assert (codes, "waiting for the full run holding the lock" in output, "1 passed" in output) == ((0, 0), True, True), output


@pytest.mark.process("two launcher children run as full runs sharing one home, the first holding the lock forever, the second waiting under a bound")
@pytest.mark.timeout(120)
def test_2195_a_full_run_waiting_on_a_holder_that_never_releases_the_lock_fails_within_its_bound_instead_of_hanging(tmp_path):
    import subprocess
    import time

    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    child = LOCK_CHILD % (scripts, os.path.join(scripts, "veri"))
    home, marks, release = tmp_path / "home", tmp_path / "marks", tmp_path / "release"
    for directory in (home, marks, tmp_path / "treeA", tmp_path / "treeB"):
        directory.mkdir()
    env = dict(os.environ, HOME=str(home), VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1", VERI_PYTEST_XDIST_IMPORTABLE="1")

    def launch(name):
        err = open(tmp_path / (name + ".err"), "w")
        return subprocess.Popen([sys.executable, "-c", child, name, str(marks), str(release)],
                                cwd=tmp_path / ("tree" + name), env=env, stdout=subprocess.DEVNULL, stderr=err)

    def until(done):
        deadline = time.monotonic() + 15
        while not done() and time.monotonic() < deadline:
            time.sleep(0.05)

    first = launch("A")
    second = None
    try:
        until(lambda: (marks / "A-started").exists())
        second = launch("B")
        until(lambda: "waiting" in (tmp_path / "B.err").read_text())
        try:
            second.wait(timeout=5)
        except subprocess.TimeoutExpired:
            second.kill()
        code = second.wait(timeout=30)
    finally:
        release.touch()
        for process in (first, second):
            if process is not None and process.poll() is None:
                process.kill()
        first.wait(timeout=30)
    assert (code != 0, (marks / "B-started").exists()) == (True, False)


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
    os.makedirs(os.path.dirname(pytest_leg.full_lock_path()), exist_ok=True)
    with open(pytest_leg.full_lock_path(), "w") as held:
        held.write("pid 1\ttree /elsewhere\n")
        held.flush()
        fcntl.flock(held, fcntl.LOCK_EX)
        code = pytest_leg.main(["--subset", "some/test_file.py"])

    assert (code, len(started) >= 1, "waiting" in capsys.readouterr().err) == (0, True, False)
    assert all("--subset" not in args and "some/test_file.py" in args for args in started)


def test_2195_after_a_full_run_releases_the_lock_the_lock_file_names_no_pid(pytest_leg, monkeypatch):
    seen = []

    def spy(args):
        seen.append(open(pytest_leg.full_lock_path()).read())
        return pytest.ExitCode.OK

    in_process_leg(pytest_leg, monkeypatch, spy)

    assert pytest_leg.main(["some/dir"]) == 0
    assert seen and all(("pid %d" % os.getpid()) in held for held in seen)
    assert "pid" not in open(pytest_leg.full_lock_path()).read()


def test_2386_on_macos_with_no_worker_count_the_budget_is_the_physical_core_count_less_the_live_legs_workers_and_at_least_1(pytest_leg, monkeypatch, tmp_path):
    import subprocess

    def sysctl_answer(argv, *args, **kwargs):
        assert list(argv) == ["sysctl", "-n", "hw.physicalcpu"]
        return subprocess.CompletedProcess(argv, 0, stdout="8\n", stderr="")

    monkeypatch.setattr(subprocess, "run", sysctl_answer)
    monkeypatch.setattr(subprocess, "check_output", lambda argv, *a, **k: sysctl_answer(argv).stdout)
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


def test_2386_off_macos_with_no_worker_count_the_budget_is_the_cpu_affinity_count_less_the_live_legs_workers_never_the_physical_core_count(pytest_leg, monkeypatch, tmp_path):
    import subprocess

    def sysctl_answer(argv, *args, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout="4\n", stderr="")

    monkeypatch.setattr(subprocess, "run", sysctl_answer)
    monkeypatch.setattr(subprocess, "check_output", lambda argv, *a, **k: sysctl_answer(argv).stdout)
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


def test_2386_on_macos_a_set_worker_count_is_used_as_given_even_above_the_physical_core_count(pytest_leg, monkeypatch, tmp_path):
    import subprocess

    def sysctl_answer(argv, *args, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout="8\n", stderr="")

    monkeypatch.setattr(subprocess, "run", sysctl_answer)
    monkeypatch.setattr(subprocess, "check_output", lambda argv, *a, **k: sysctl_answer(argv).stdout)
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    monkeypatch.setattr(os, "process_cpu_count", lambda: 16, raising=False)
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(16)), raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    legs = tmp_path / "legs"
    legs.mkdir()
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    assert pytest_leg.worker_count("12") == 12


def test_2386_on_macos_with_no_sysctl_on_the_path_the_budget_falls_back_to_the_cpu_count_instead_of_crashing(pytest_leg, monkeypatch, tmp_path):
    import subprocess

    def no_sysctl(argv, *args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory", "sysctl")

    monkeypatch.setattr(subprocess, "run", no_sysctl)
    monkeypatch.setattr(subprocess, "check_output", no_sysctl)
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


def test_2397_on_a_mac_whose_sysctl_runs_and_fails_with_empty_stdout_the_worker_count_falls_back_to_the_affinity_count(pytest_leg, monkeypatch, tmp_path):
    import subprocess

    legs = tmp_path / "legs"
    legs.mkdir()
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(8)), raising=False)
    monkeypatch.setattr(os, "cpu_count", lambda: 8)
    monkeypatch.setattr(pytest_leg.subprocess, "run", lambda argv, **kw: subprocess.CompletedProcess(argv, 1, stdout="", stderr="sysctl: failed"))
    assert pytest_leg.worker_count(None) == 8


def test_2397_on_a_mac_whose_sysctl_exits_0_with_non_numeric_stdout_the_worker_count_falls_back_to_the_affinity_count(pytest_leg, monkeypatch, tmp_path):
    import subprocess

    legs = tmp_path / "legs"
    legs.mkdir()
    monkeypatch.setenv("VERI_PYTEST_LEGS", str(legs))
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(os, "sched_getaffinity", lambda pid: set(range(8)), raising=False)
    monkeypatch.setattr(os, "cpu_count", lambda: 8)
    monkeypatch.setattr(pytest_leg.subprocess, "run", lambda argv, **kw: subprocess.CompletedProcess(argv, 0, stdout="not a number\n", stderr=""))
    assert pytest_leg.worker_count(None) == 8
