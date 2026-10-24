"""merge-lock.sh through the real /bin/sh shim."""
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("merge-lock.sh run as the /bin/sh shim it is")
def test_merge_lock_sh_with_no_argument_prints_a_usage_line_naming_take_release_and_holder_and_exits_2():
    done = subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh")], stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert (done.returncode, all(verb in done.stderr for verb in ("take", "release", "holder"))) == (2, True)


@pytest.mark.process("two merge-lock.sh take shims racing for one lock in a scratch repository")
def test_two_takers_racing_for_a_free_lock_end_with_one_holding_it_and_the_other_waiting_until_the_winners_release(
        tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)
    env = {**os.environ, "VERI_MERGE_LOCK_POLL": "0.05"}
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    pids = {"a": str(os.getpid()), "b": str(sleeper.pid)}

    def shim(*args, wait=True):
        cmd = ["/bin/sh", str(SCRIPTS / "merge-lock.sh"), *args]
        kw = dict(cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                  stderr=subprocess.PIPE, text=True)
        return subprocess.run(cmd, **kw) if wait else subprocess.Popen(cmd, **kw)

    takers = {k: shim("take", "--pid", pid, wait=False) for k, pid in pids.items()}
    try:
        deadline = time.monotonic() + 10
        while all(t.poll() is None for t in takers.values()) and time.monotonic() < deadline:
            time.sleep(0.02)
        time.sleep(0.5)
        winner = next((k for k, t in takers.items() if t.returncode == 0), "a")
        loser = "b" if winner == "a" else "a"
        waiting = takers[loser].poll() is None
        released = shim("release", "--pid", pids[winner])
        try:
            takers[loser].wait(timeout=10)
        except subprocess.TimeoutExpired:
            takers[loser].kill()
        held = shim("holder")
        assert (takers[winner].returncode, waiting, released.returncode, takers[loser].returncode,
                pids[loser] in held.stdout.split()) == (0, True, 0, 0, True)
    finally:
        for t in takers.values():
            if t.poll() is None:
                t.kill()
            t.communicate()
        sleeper.kill()
        sleeper.wait()


@pytest.mark.process("a merge-lock.sh take shim waiting on a stale lock in a scratch repository, then release --force")
def test_take_on_a_stale_lock_reports_the_stale_holder_on_stderr_and_waits_with_the_lock_in_place_until_release_force(
        tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"], check=True)
    env = {**os.environ, "VERI_MERGE_LOCK_POLL": "0.05"}
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    dead = str(child.pid)
    lock = repo / ".tdd" / "merge.lock"

    def shim(*args, **kw):
        return subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), *args], cwd=repo, env=env,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, **kw)

    shim("take", "--pid", dead)
    errfile = tmp_path / "take.err"
    with open(errfile, "w") as err:
        taker = subprocess.Popen(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "take", "--pid", str(os.getpid())],
                                 cwd=repo, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=err)
    try:
        deadline = time.monotonic() + 10
        while not errfile.read_text() and taker.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        time.sleep(0.3)
        reported = errfile.read_text()
        waiting = taker.poll() is None
        kept = lock.is_dir()
        forced = shim("release", "--force")
        try:
            taker.wait(timeout=10)
        except subprocess.TimeoutExpired:
            taker.kill()
        held = shim("holder")
        assert (dead in reported.split(), "stale" in reported.lower(), waiting, kept, forced.returncode,
                taker.returncode, str(os.getpid()) in held.stdout.split()) == (True, True, True, True, 0, 0, True)
    finally:
        if taker.poll() is None:
            taker.kill()
        taker.communicate()


@pytest.mark.process("merge-lock.sh take and holder as two separate shims in a scratch repository")
def test_take_with_pid_of_a_long_lived_process_keeps_the_lock_live_for_a_holder_run_in_a_later_shell(tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])

    def shim(*args):
        return subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), *args], cwd=tmp_path,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True)

    try:
        taken = shim("take", "--pid", str(sleeper.pid))
        held = shim("holder")
        assert (taken.returncode, held.returncode, str(sleeper.pid) in held.stdout.split()) == (0, 0, True)
    finally:
        sleeper.kill()
        sleeper.wait()
