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


@pytest.mark.process("a stub python3 on PATH that the launcher asks for its version")
def test_3191_a_path_python3_below_the_floor_beside_a_healthy_interpreter_exits_2_naming_it_and_its_version_before_pytest_runs(pytest_leg, run_cli, monkeypatch, tmp_path):
    stub = tmp_path / "bin" / "python3"
    stub.parent.mkdir()
    stub.write_text("#!/bin/sh\necho 'Python 3.9.6'\n")
    stub.chmod(0o755)
    calls = []
    monkeypatch.setattr(pytest, "main", lambda args: calls.append(list(args)) or pytest.ExitCode.OK)
    code, out, err = run_cli(pytest_leg, ["-q"], env=leg_env(PATH=str(stub.parent), VERI_PYTEST_WORKERS="1"))
    assert (code, out, calls) == (2, "", [])
    assert str(stub) in err and "3.9.6" in err


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
        "sys.path.insert(0, sys.path[0] + '/tests/leg')\nimport pytest_leg\n"
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
        "sys.path.insert(0, sys.path[0] + '/tests/leg')\nimport pytest_leg\n"
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
         os.path.join(scripts, "tests", "leg", "pytest_leg.py"), "-q", "-p", "no:cacheprovider", str(planted)],
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
        % (str(outside), os.path.join(veri, "leg_tmpdir.py"))
    )
    path = os.pathsep.join([str(bin_dir), os.environ["PATH"]])
    done = subprocess.run(
        [sys.executable, "-c", "import runpy, sys; sys.argv[0] = sys.argv.pop(1); runpy.run_path(sys.argv[0], run_name='__main__')",
         os.path.join(scripts, "tests", "leg", "pytest_leg.py"), "-q", "-p", "no:cacheprovider", str(planted)],
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
         os.path.join(scripts, "tests", "leg", "pytest_leg.py"), "-q", "-p", "no:cacheprovider", str(planted)],
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
         os.path.join(scripts, "tests", "leg", "pytest_leg.py"), "-q", "-p", "no:cacheprovider", str(planted)],
        cwd=tmp_path, env=dict(os.environ, VERI_PYTEST_WORKERS="1", PYTHONPATH=veri), capture_output=True, text=True, timeout=60,
    )
    out = done.stdout + done.stderr
    assert "2 passed" in out and "failed" not in out
    assert (tmp_path / "ran-gh").exists() and (tmp_path / "ran-curl").exists()


@pytest.mark.process("a real sh child started with a hand-built env whose PATH holds a stand-in gh outside the run's basetemp")
def test_a_child_process_given_a_hand_built_env_whose_path_holds_a_gh_outside_the_basetemp_gets_the_refusal_not_that_gh_issue_2819(tmp_path):
    import pathlib
    import shutil
    import subprocess
    import tempfile

    outside = tempfile.mkdtemp(prefix="exp-gh-", dir="/tmp")
    try:
        stand_in = pathlib.Path(outside) / "gh"
        stand_in.write_text("#!/bin/sh\ntouch %s\n" % (tmp_path / "ran-gh"))
        stand_in.chmod(0o755)

        ran = subprocess.run(["/bin/sh", "-c", "gh issue view 1"], cwd=tmp_path, capture_output=True, text=True,
                             env={"PATH": outside + ":/usr/bin:/bin"})
    finally:
        shutil.rmtree(outside)

    assert not (tmp_path / "ran-gh").exists(), "the child ran the stand-in gh: %r" % ran.stderr
    assert ran.returncode != 0


@pytest.mark.process("a real sh child started with a hand-built env whose PATH holds a stand-in curl outside the run's basetemp")
def test_a_child_process_given_a_hand_built_env_whose_path_holds_a_curl_outside_the_basetemp_gets_the_refusal_not_that_curl_issue_2819(tmp_path):
    import pathlib
    import shutil
    import subprocess
    import tempfile

    outside = tempfile.mkdtemp(prefix="exp-curl-", dir="/tmp")
    try:
        stand_in = pathlib.Path(outside) / "curl"
        stand_in.write_text("#!/bin/sh\ntouch %s\n" % (tmp_path / "ran-curl"))
        stand_in.chmod(0o755)

        ran = subprocess.run(["/bin/sh", "-c", "curl http://example.invalid/"], cwd=tmp_path, capture_output=True, text=True,
                             env={"PATH": outside + ":/usr/bin:/bin"})
    finally:
        shutil.rmtree(outside)

    assert not (tmp_path / "ran-curl").exists(), "the child ran the stand-in curl: %r" % ran.stderr
    assert ran.returncode != 0


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
        code, out, err = run_cli(importlib.import_module("pytest_leg"), ["-q", "-p", "no:cacheprovider", *selection, str(planted)], env=env)
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
        code, out, err = run_cli(importlib.import_module("pytest_leg"), ["-q", "-p", "no:cacheprovider", str(planted)], env=env)
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
        code, out, err = run_cli(importlib.import_module("pytest_leg"), ["-q", "-p", "no:cacheprovider", str(planted)], env=env)
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
        code, out, err = run_cli(importlib.import_module("pytest_leg"), ["-q", "-p", "no:cacheprovider", str(planted)], env=env)
    finally:
        sys.modules.pop("test_planted", None)
        sys.modules.pop("conftest", None)

    assert "cut short" in err, out + err


@pytest.mark.process("the launcher run as a child over a planted tests tree whose case reports its own tmp_path")
def test_2051_a_case_s_tmp_path_under_the_launcher_is_the_private_tmp_path_directory_of_mode_0700_under_the_run_s_basetemp_not_a_numbered_one(tmp_path):
    import os
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
         os.path.join(scripts, "tests", "leg", "pytest_leg.py"), "-q", "-p", "no:cacheprovider", str(planted)],
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
sys.path.insert(0, sys.path[0] + "/tests/leg")
import pytest_leg
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
    with open(os.environ["VERI_TEST_CEILING_FILE"], "w") as f:
        f.write("8\n")  # a measured budget, so the only stderr line is the lock wait's, not the core fallback's
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
sys.path.insert(0, sys.path[0] + "/tests/leg")
import pytest_leg
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
sys.path.insert(0, sys.path[0] + "/tests/leg")
import pytest_leg
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
    env.update(HOME=str(home), VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1", VERI_PYTEST_XDIST_IMPORTABLE="1",
               VERI_PYTEST_WORKERS="1")  # the holder registers no core, so the nested leg finds one free on any machine
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
    with open(os.environ["VERI_TEST_CEILING_FILE"], "w") as f:
        f.write("8\n")  # a measured budget, so B's first stderr byte is a wait, not the core fallback's line
    env = dict(os.environ, HOME=str(home), VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1", VERI_PYTEST_XDIST_IMPORTABLE="1")

    def launch(name, extra):
        err = open(tmp_path / (name + ".err"), "w")
        return subprocess.Popen([sys.executable, "-c", child, name, str(marks), str(release)],
                                cwd=tmp_path / ("tree" + name), env=dict(env, **extra), stdout=subprocess.DEVNULL, stderr=err)

    def until(done):
        deadline = time.monotonic() + 15
        while not done() and time.monotonic() < deadline:
            time.sleep(0.05)

    first = launch("A", {"VERI_PYTEST_WORKERS": "1"})  # the holder registers no core, so B finds one free on any machine
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
    with open(os.environ["VERI_TEST_CEILING_FILE"], "w") as f:
        f.write("8\n")  # a measured budget, so B's first stderr byte is a wait, not the core fallback's line
    env = dict(os.environ, HOME=str(home), VERI_PYTEST_IMPORTABLE="1", VERI_PYTEST_TIMEOUT_IMPORTABLE="1", VERI_PYTEST_XDIST_IMPORTABLE="1")

    def launch(name):
        err = open(tmp_path / (name + ".err"), "w")
        # the holder registers no core, so B finds one free on any machine
        extra = {"VERI_PYTEST_WORKERS": "1"} if name == "A" else {}
        return subprocess.Popen([sys.executable, "-c", fast_child, name, str(marks), str(release)],
                                cwd=tmp_path / ("tree" + name), env=dict(env, **extra), stdout=subprocess.DEVNULL, stderr=err)

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
sys.path.insert(0, sys.path[0] + "/tests/leg")
import pytest_leg
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
