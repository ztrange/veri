"""The real leg over a planted suite whose xdist workers hang after their cases ran (#4254): the leg ends itself."""
import os
import signal
import subprocess
import sys
import time

import pytest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEG = os.path.join(SCRIPTS, "tests", "leg", "pytest_leg.py")
BOUND = 45  # the test-side bound on a leg that never ends, well under the case's own timeout (90 s)
IDLE = 8  # the idle window: long enough under CI start-up load for both workers to reach their hang

# A worker that ran its one case and then never reports workerfinished: its sessionfinish blocks, as the hung legs'
# workers did after their cases ran, and it ignores TERM when asked to, so only a KILL ends it.
HANGING_CONFTEST = (
    "import os, signal, time\n"
    "def pytest_sessionfinish(session):\n"
    "    if os.environ.get('PYTEST_XDIST_WORKER'):\n"
    "        if os.environ.get('PLANTED_IGNORE_TERM'):\n"
    "            signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
    "        with open(os.path.join(os.environ['PLANTED_PIDS'], str(os.getpid())), 'w'):\n"
    "            pass\n"
    "        while True:\n"
    "            time.sleep(1)\n"
)


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def run_hanging_leg(tmp_path, idle=IDLE, signal_when_hung=None, **extra):
    """(exit code, stderr, worker pids, those alive when the leg exited, seconds from the signal to the exit)."""
    planted = tmp_path / "planted"
    planted.mkdir()
    pids = tmp_path / "worker-pids"
    pids.mkdir()
    (planted / "conftest.py").write_text(HANGING_CONFTEST)
    (planted / "test_one.py").write_text("def test_one():\n    pass\n\ndef test_two():\n    pass\n")
    # A one-second grace, not the production 5 s: every case here ends workers that hang
    env = dict(os.environ, VERI_PYTEST_WORKERS="2", VERI_PYTEST_IDLE=str(idle), VERI_PYTEST_TERM_GRACE="1",
               PLANTED_PIDS=str(pids), PYTHONPATH=os.path.join(SCRIPTS, "veri"), **extra)
    # Files, not pipes: the workers inherit the leg's stderr, and a pipe would wait for them, not for the leg, to end.
    with open(tmp_path / "out", "w") as out, open(tmp_path / "err", "w") as err:
        leg = subprocess.Popen(
            [sys.executable, "-c", "import runpy, sys; sys.argv[0] = sys.argv.pop(1); runpy.run_path(sys.argv[0], run_name='__main__')",
             LEG, "--subset", "-q", "-p", "no:cacheprovider", str(planted)],
            cwd=tmp_path, env=env, stdout=out, stderr=err, start_new_session=True)
    signalled = None
    try:
        if signal_when_hung:
            deadline = time.monotonic() + BOUND
            while len(os.listdir(pids)) < 2 and leg.poll() is None and time.monotonic() < deadline:
                time.sleep(0.1)
            signalled = time.monotonic()
            leg.send_signal(signal_when_hung)
        leg.wait(timeout=BOUND)
    except subprocess.TimeoutExpired:
        if leg.pid > 1:
            os.killpg(leg.pid, signal.SIGKILL)  # the session this case started: the leg and its workers
        leg.wait()
        pytest.fail("the leg was still running %d s after its cases ran, its workers idle" % BOUND)
    workers = [int(name) for name in os.listdir(pids)]
    alive_at_exit = [pid for pid in workers if alive(pid)]
    if alive_at_exit and leg.pid > 1:
        os.killpg(leg.pid, signal.SIGKILL)  # leave nothing running past the case
    took = time.monotonic() - signalled if signalled else None
    return leg.returncode, (tmp_path / "err").read_text(), workers, alive_at_exit, took


@pytest.mark.process("the real leg over a planted suite whose two xdist workers hang after their cases ran")
@pytest.mark.parametrize("ignore_term", ["", "1"], ids=["workers-end-on-term", "workers-ignore-term"])
def test_4254_a_leg_whose_workers_hang_after_their_cases_ran_ends_them_and_exits_2_naming_the_idle_time_and_the_last_case(tmp_path, ignore_term):
    code, err, workers, alive_at_exit, _ = run_hanging_leg(tmp_path, PLANTED_IGNORE_TERM=ignore_term)

    lines = [line for line in err.splitlines() if line.startswith("pytest leg idle for ")]
    assert (code, len(lines), len(workers)) == (2, 1, 2), err
    assert "with no case running (last case seen: " in lines[0] and "test_one.py::test_" in lines[0]
    assert lines[0].endswith(" ended") and all(str(pid) in lines[0] for pid in workers)
    assert alive_at_exit == []  # ended by the leg, before it exited, not by execnet noticing its leg gone


@pytest.mark.process("the real leg over a planted suite whose two xdist workers hang after their cases ran")
def test_4254_before_it_ends_its_hung_workers_an_idle_leg_writes_its_own_stacks_and_each_worker_s_to_stderr(tmp_path):
    # A window twice the others': a worker that has not reached its hang when the leg dumps shows no frame there.
    code, err, workers, alive_at_exit, _ = run_hanging_leg(tmp_path, idle=2 * IDLE)

    hung_frames = [line for line in err.splitlines() if "conftest.py" in line and "pytest_sessionfinish" in line]
    assert (code, len(hung_frames)) == (2, 2), err  # one per worker, where each hung
    assert "idle_watch.py" in err.split("pytest leg idle for ")[0]  # the leg's own watch thread, among its stacks


@pytest.mark.process("the real leg over a planted suite whose two xdist workers hang, sent TERM or HUP")
@pytest.mark.parametrize("sig", [signal.SIGTERM, signal.SIGHUP], ids=["TERM", "HUP"])
def test_4254_a_leg_sent_term_or_hup_while_its_workers_hang_ends_them_and_exits_128_plus_the_signal_without_xdist_s_teardown(tmp_path, sig):
    code, err, workers, alive_at_exit, took = run_hanging_leg(tmp_path, idle=600, signal_when_hung=sig)

    assert (code, len(workers), alive_at_exit) == (128 + sig, 2, []), err
    # xdist's teardown waits up to its EXIT_TIMEOUT (10 s) on workers that do not answer; ending them here takes no wait
    assert took < 4, err


@pytest.mark.process("the real leg over a planted suite whose two xdist workers hang and ignore TERM, sent TERM")
def test_4254_a_leg_sent_term_kills_by_pid_a_hung_worker_that_ignores_term_after_the_grace(tmp_path):
    code, err, workers, alive_at_exit, took = run_hanging_leg(tmp_path, idle=600, signal_when_hung=signal.SIGTERM,
                                                             PLANTED_IGNORE_TERM="1")

    assert (code, len(workers), alive_at_exit) == (143, 2, []), err
