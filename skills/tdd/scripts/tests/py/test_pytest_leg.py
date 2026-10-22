"""In-process cases for veri/pytest_leg.py, the launcher that makes the pytest leg's refusals and then runs pytest."""
import importlib
import sys

import pytest


@pytest.fixture
def pytest_leg():
    return importlib.import_module("veri.pytest_leg")


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
        code, out, err = run_cli(pytest_leg, [], env={"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": value})
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
        env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": workers}
        assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    parallel, serial_pass, single, single_serial_pass = [without_selection(c) for c in calls]
    assert "-n" in parallel and parallel[parallel.index("-n") + 1] == "4" or "-n4" in parallel or "--numprocesses=4" in parallel
    assert serial_pass == single == single_serial_pass == ["-q", "some/dir"]


def test_with_no_worker_count_the_launcher_hands_pytest_one_worker_per_available_core_and_runs_serially_on_a_single_core(pytest_leg, run_cli, monkeypatch):
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
    for cores["n"], workers in ((6, None), (6, ""), (1, None)):
        env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1"}
        if workers is not None:
            env["VERI_PYTEST_WORKERS"] = workers
        assert run_cli(pytest_leg, ["-q", "some/dir"], env=env)[0] == 0
    unset, unset_serial, empty, empty_serial, single, single_serial = [without_selection(c) for c in calls]
    for parallel in (unset, empty):
        assert parallel[parallel.index("-n") + 1] == "6" if "-n" in parallel else "-n6" in parallel or "--numprocesses=6" in parallel
    assert unset_serial == empty_serial == single == single_serial == ["-q", "some/dir"]


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
    for workers in (None, "3"):
        env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "PYTEST_XDIST_WORKER": "gw0"}
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
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "4"}
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
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1",
           "VERI_PYTEST_WORKERS": "2", "PLANTED_LOG": str(log)}
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
    env = {"VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1", "VERI_PYTEST_XDIST_IMPORTABLE": "1", "VERI_PYTEST_WORKERS": "4"}

    assert run_cli(pytest_leg, ["some/dir"], env=env)[0] == code
    assert next(statuses, None) is None
