"""Cases for supervise.sh that start a real process."""
import fcntl
import json
import os
import subprocess
import sys
import time

import pytest

from conftest import SCRIPTS, supervised


@pytest.mark.process("supervise.sh run for real, supervising a real leaf that echoes its arguments and exits 1")
def test_supervise_sh_forwards_its_arguments_to_the_leaf_and_the_leafs_exit_code_as_its_own(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "supervise.sh"), "develop-red", "sh", "-c", 'echo "$1"; exit 1', "sh", "forwarded"],
                         cwd=tmp_path, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "0",
                              "VERI_POLL": "0.05", "PYTHONDONTWRITEBYTECODE": "1"})

    assert (ran.returncode, ran.stdout) == (1, "forwarded\n"), ran.stderr


@pytest.mark.process("supervise.sh and git run for real, from a subdirectory of a throwaway repo")
def test_supervise_sh_run_from_a_subdirectory_writes_its_run_state_under_the_repo_root_1895(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    sub = tmp_path / "skills"
    sub.mkdir()

    ran = subprocess.run([str(SCRIPTS / "supervise.sh"), "develop-red", "sh", "-c", "exit 0"],
                         cwd=sub, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "0",
                              "VERI_POLL": "0.05", "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 0, ran.stderr
    assert (sorted(p.name for p in (tmp_path / ".tdd").glob("develop-red.*")), (sub / ".tdd").exists()) == (
        ["develop-red.exit", "develop-red.log", "develop-red.pid", "develop-red.rc"], False)


BROKEN_LOCK_WAIT = """\
import sys, time
sys.path[:0] = [%r, %r]
import pytest
from veri import pytest_leg
pytest.main = lambda args: pytest.ExitCode.OK
pytest_leg.acquire_full_lock = lambda: time.sleep(3600)
sys.exit(pytest_leg.main([]))
"""


@pytest.mark.process("supervise.sh runs a real verify leaf whose full run sits in a lock wait that never returns")
@pytest.mark.timeout(60)
def test_2377_a_verify_leaf_whose_mutation_breaks_the_full_suite_lock_wait_is_killed_stuck_within_its_bound(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    script = work / "full_run.py"
    script.write_text(BROKEN_LOCK_WAIT % (str(SCRIPTS), str(SCRIPTS / "veri")))

    ran = subprocess.run([str(SCRIPTS / "supervise.sh"), "verify-rebase", sys.executable, str(script)],
                         cwd=work, capture_output=True, text=True, timeout=30,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "0",
                              "VERI_POLL": "0.05", "VERI_TIMEOUT": "2", "VERI_HEARTBEAT": "600",
                              "HOME": str(tmp_path), "VERI_PYTEST_LEGS": str(tmp_path / "legs"),
                              "VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1",
                              "VERI_PYTEST_XDIST_IMPORTABLE": "1", "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 2, ran.stderr


SHORT_FULL_RUN = """\
import sys
sys.path[:0] = [%r, %r]
import pytest
from veri import pytest_leg
pytest.main = lambda args: pytest.ExitCode.OK
sys.exit(pytest_leg.main([]))
"""


CLOCK = """\
#!/bin/sh
n=$(cat "$1/ticks" 2>/dev/null || echo 0)
set -- "$1" "$1/../legs-full.lock.wait-"*
if [ -e "$2" ]; then n=$((n + 1)); echo $n > "$1/ticks.tmp" && mv "$1/ticks.tmp" "$1/ticks"; fi
echo $n
"""

DATE = """\
#!/bin/sh
cat "%s/ticks" 2>/dev/null || echo 0
"""


NEW_SESSION = """\
import os, subprocess, sys
child = subprocess.Popen([sys.executable, %r], start_new_session=True)
open(%r, "w").write(str(child.pid))
sys.exit(child.wait())
"""


def run_queued_leaf_past_window(tmp_path, limits, own_session=False):
    work = tmp_path / "work"
    work.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    script = work / "full_run.py"
    script.write_text(SHORT_FULL_RUN % (str(SCRIPTS), str(SCRIPTS / "veri")))
    pidfile = tmp_path / "full_run.pid"
    if own_session:
        tool = work / "tool_shell.py"
        tool.write_text(NEW_SESSION % (str(script), str(pidfile)))
        script = tool
    state = tmp_path / "state"
    state.mkdir()
    shims = tmp_path / "shims"
    shims.mkdir()
    for name, body in (("clock", CLOCK), ("date", DATE % state)):
        (shims / name).write_text(body)
        (shims / name).chmod(0o755)
    held = open(str(tmp_path / "legs") + "-full.lock", "a+")
    fcntl.flock(held, fcntl.LOCK_EX)
    window = int(limits["VERI_TIMEOUT"]) if limits["VERI_HEARTBEAT"] == "600" else int(limits["VERI_HEARTBEAT"])
    ticks = state / "ticks"
    with supervised([str(SCRIPTS / "supervise.sh"), "verify-rebase", sys.executable, str(script)],
                    cwd=work, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                    env={"PATH": str(shims) + ":" + os.path.dirname(sys.executable) + ":/usr/bin:/bin",
                         "VERI_STUCK_RETRIES": "0", "VERI_POLL": "0.05", **limits,
                         "VERI_AWAKE_CLOCK": "%s %s" % (shims / "clock", state),
                         "HOME": str(tmp_path), "VERI_PYTEST_LEGS": str(tmp_path / "legs"),
                         "VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1",
                         "VERI_PYTEST_XDIST_IMPORTABLE": "1", "PYTHONDONTWRITEBYTECODE": "1"}) as ran:
        try:
            while ran.poll() is None and not (ticks.exists() and int(ticks.read_text() or 0) > window):
                time.sleep(0.02)
        finally:
            fcntl.flock(held, fcntl.LOCK_UN)
            held.close()
        try:
            out, err = ran.communicate(timeout=30)
        finally:
            if own_session:
                try:
                    os.kill(int(pidfile.read_text()), 9)
                except (OSError, ValueError):
                    pass
        return ran.returncode, err


@pytest.mark.process("supervise.sh runs a real leaf whose full run queues behind a lock the test holds until the injected clock passes VERI_TIMEOUT")
@pytest.mark.timeout(60)
def test_2380_a_leaf_queued_on_the_full_suite_lock_past_the_hard_timeout_is_not_killed_stuck(tmp_path):
    code, err = run_queued_leaf_past_window(tmp_path, {"VERI_TIMEOUT": "2", "VERI_HEARTBEAT": "600"})

    assert code == 0, err


@pytest.mark.process("supervise.sh runs a real leaf whose full run queues silently behind a lock the test holds until the injected clock passes VERI_HEARTBEAT")
@pytest.mark.timeout(60)
def test_2380_a_leaf_queued_on_the_full_suite_lock_past_the_silence_window_is_not_killed_for_silence(tmp_path):
    code, err = run_queued_leaf_past_window(tmp_path, {"VERI_TIMEOUT": "600", "VERI_HEARTBEAT": "2"})

    assert code == 0, err


@pytest.mark.process("supervise.sh runs a real leaf whose full run, in a session of its own as a Bash tool command is, queues behind a lock the test holds until the injected clock passes VERI_TIMEOUT")
@pytest.mark.timeout(60)
def test_2380_a_leaf_whose_full_run_queues_on_the_lock_from_its_own_process_group_past_the_hard_timeout_is_not_killed_stuck(tmp_path):
    code, err = run_queued_leaf_past_window(tmp_path, {"VERI_TIMEOUT": "2", "VERI_HEARTBEAT": "600"}, own_session=True)

    assert code == 0, err


HANG_CLOCK = """\
#!/bin/sh
n=$(cat "$1/ticks" 2>/dev/null || echo 0)
if [ -e "$1/../acquired" ]; then n=$((n + 1)); echo $n > "$1/ticks.tmp" && mv "$1/ticks.tmp" "$1/ticks"; fi
echo $n
"""


HANG_AFTER_LOCK = """\
import sys, time
sys.path[:0] = [%r, %r]
import pytest
from veri import pytest_leg
pytest.main = lambda args: (open(%r, "w").close(), time.sleep(3600))
sys.exit(pytest_leg.main([]))
"""


def run_hang_after_lock(tmp_path, startup_delay):
    work = tmp_path / "work"
    work.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    script = work / "full_run.py"
    acquired = tmp_path / "acquired"
    script.write_text(HANG_AFTER_LOCK % (str(SCRIPTS), str(SCRIPTS / "veri"), str(acquired)))
    state = tmp_path / "state"
    state.mkdir()
    clock = tmp_path / "clock"
    clock.write_text(HANG_CLOCK)
    clock.chmod(0o755)
    held = open(str(tmp_path / "legs") + "-full.lock", "a+")
    fcntl.flock(held, fcntl.LOCK_EX)
    with supervised([str(SCRIPTS / "supervise.sh"), "verify-rebase", sys.executable, str(script)],
                           cwd=work, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                           env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "0",
                                "VERI_POLL": "0.05", "VERI_TIMEOUT": "4", "VERI_HEARTBEAT": "600",
                                "VERI_AWAKE_CLOCK": "%s %s" % (clock, state),
                                "HOME": str(tmp_path), "VERI_PYTEST_LEGS": str(tmp_path / "legs"),
                                "VERI_PYTEST_IMPORTABLE": "1", "VERI_PYTEST_TIMEOUT_IMPORTABLE": "1",
                                "VERI_PYTEST_XDIST_IMPORTABLE": "1", "PYTHONDONTWRITEBYTECODE": "1"}) as ran:
        try:
            while ran.poll() is None and not list(tmp_path.glob("legs-full.lock.wait-*")):
                time.sleep(0.02)
            time.sleep(startup_delay)
        finally:
            fcntl.flock(held, fcntl.LOCK_UN)
            held.close()
        out, err = ran.communicate(timeout=30)

    return ran.returncode, acquired.exists(), err


@pytest.mark.process("supervise.sh runs a real leaf that waits on a lock the test releases, then hangs holding it")
@pytest.mark.timeout(60)
def test_2380_a_leaf_that_hangs_after_acquiring_the_full_suite_lock_is_still_killed_stuck(tmp_path):
    code, acquired, err = run_hang_after_lock(tmp_path, 0)

    assert (code, acquired) == (2, True), err


@pytest.mark.process("supervise.sh runs a real leaf that waits past VERI_TIMEOUT on a lock the test releases, then hangs holding it")
@pytest.mark.timeout(60)
def test_2717_a_leaf_slow_to_reach_the_full_suite_lock_past_the_hard_timeout_is_still_killed_stuck(tmp_path):
    code, acquired, err = run_hang_after_lock(tmp_path, 5)

    assert (code, acquired) == (2, True), err


@pytest.mark.process("supervise.sh runs a real leaf whose whole process group the test SIGKILLs from outside")
@pytest.mark.timeout(60)
def test_2427_a_leaf_sigkilled_by_another_process_exits_2_with_cause_killed_external_and_is_not_retried(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    pidfile = tmp_path / "leaf.pid"
    leaf = None
    with supervised([str(SCRIPTS / "supervise.sh"), "develop-red", "sh", "-c",
                     'echo $$ > "$1"; exec sleep 60', "sh", str(pidfile)],
                    cwd=work, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                    env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "1",
                         "VERI_POLL": "0.05", "VERI_TIMEOUT": "3", "VERI_HEARTBEAT": "600",
                         "VERI_ISSUE": "2427", "VERI_STEP": "1", "PYTHONDONTWRITEBYTECODE": "1"}) as ran:
        while ran.poll() is None and leaf is None:
            text = pidfile.read_text().strip() if pidfile.exists() else ""
            leaf = int(text) if text.isdigit() else None
            time.sleep(0.02)
        if leaf is not None:
            os.killpg(os.getpgid(leaf), 9)
        out, err = ran.communicate(timeout=20)
    events = [json.loads(l) for l in (work / ".tdd" / "events.jsonl").read_text().splitlines()]
    exits = [e for e in events if e.get("event") == "exit"]

    assert (ran.returncode, [e for e in events if e.get("event") == "retry"] == [],
            [e.get("cause") for e in exits]) == (2, True, ["killed-external"]), err


@pytest.mark.process("supervise.sh runs a real leaf that outlives VERI_TIMEOUT, so supervise.sh itself SIGKILLs it")
@pytest.mark.timeout(60)
def test_2427_a_leaf_killed_by_the_supervisors_own_hard_timeout_stays_killed_stuck_and_is_retried_within_its_budget(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    ran = subprocess.run([str(SCRIPTS / "supervise.sh"), "develop-red", "sleep", "60"],
                         cwd=work, capture_output=True, text=True, timeout=30,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "1",
                              "VERI_POLL": "0.05", "VERI_TIMEOUT": "1", "VERI_HEARTBEAT": "600",
                              "VERI_ISSUE": "2427", "VERI_STEP": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    events = [json.loads(l) for l in (work / ".tdd" / "events.jsonl").read_text().splitlines()]
    retries = [e for e in events if e.get("event") == "retry"]
    exits = [e for e in events if e.get("event") == "exit"]

    assert (ran.returncode, len(retries), [e.get("cause") for e in exits]) == (
        2, 1, ["hard timeout 1s exceeded"]), ran.stderr


@pytest.mark.process("supervise.sh runs a real leaf that outlives the wait the shared helper gives it")
@pytest.mark.timeout(60)
def test_2644_a_supervisor_whose_leaf_outlives_the_cases_wait_is_gone_after_the_helper_exits(tmp_path):
    from conftest import run_supervised

    work = tmp_path / "work"
    work.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    started = []
    with pytest.raises(subprocess.TimeoutExpired):
        run_supervised([str(SCRIPTS / "supervise.sh"), "develop-red", "sleep", "300"], timeout=2, started=started,
                       cwd=work, text=True,
                       env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "0",
                            "VERI_POLL": "0.05", "VERI_TIMEOUT": "600", "VERI_HEARTBEAT": "600",
                            "VERI_ISSUE": "2644", "VERI_STEP": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    alive = True
    try:
        os.kill(started[0].pid, 0)
    except ProcessLookupError:
        alive = False
    finally:
        if alive:
            os.killpg(started[0].pid, 9)

    assert alive is False
