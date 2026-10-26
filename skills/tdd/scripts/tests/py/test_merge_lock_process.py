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


@pytest.mark.process("a merge-lock.sh take shim blocked reading a holder record that its release removes, in a scratch repository")
def test_2381_take_waiting_on_a_held_lock_whose_release_removes_it_mid_read_exits_0_holding_the_lock(tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)
    lock = tmp_path / ".tdd" / "merge.lock"
    lock.mkdir(parents=True)
    record = lock / "holder"
    os.mkfifo(record)
    env = {**os.environ, "VERI_MERGE_LOCK_POLL": "0.05"}
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    taker = subprocess.Popen(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "take", "--pid", str(sleeper.pid)],
                             cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 20
        writer = None
        while writer is None and taker.poll() is None and time.monotonic() < deadline:
            try:
                writer = os.open(record, os.O_WRONLY | os.O_NONBLOCK)
            except OSError:
                time.sleep(0.02)
        if writer is not None:
            subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "release", "--force"],
                           cwd=tmp_path, env=env, stdin=subprocess.DEVNULL, capture_output=True, check=True)
            os.close(writer)
        try:
            taker.wait(timeout=10)
        except subprocess.TimeoutExpired:
            taker.kill()
        held = subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "holder"], cwd=tmp_path, env=env,
                              stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, text=True)
        assert (taker.returncode, str(sleeper.pid) in held.stdout.split()) == (0, True)
    finally:
        if taker.poll() is None:
            taker.kill()
        taker.communicate()
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


@pytest.mark.process("merge-lock.sh gate running a real command that exits 1 against a held lock in a scratch repository")
def test_2245_gate_running_a_command_that_exits_1_exits_1_and_releases_the_lock_so_a_second_take_gets_it_at_once(
        tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)
    env = {**os.environ, "VERI_MERGE_LOCK_POLL": "0.05"}
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])

    def shim(*args, **kw):
        return subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), *args], cwd=tmp_path, env=env,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, **kw)

    try:
        taken = shim("take", "--pid", str(os.getpid()))
        gated = shim("gate", "--pid", str(os.getpid()), "--", sys.executable, "-c", "raise SystemExit(1)")
        held = shim("holder")
        second = shim("take", "--pid", str(sleeper.pid), timeout=5)
        assert (taken.returncode, gated.returncode, held.returncode, second.returncode) == (0, 1, 3, 0)
    finally:
        sleeper.kill()
        sleeper.wait()


@pytest.mark.process("merge-lock.sh gate running real commands that exit 0 and 3, and malformed gate calls, in scratch repositories")
def test_2245_gate_keeps_the_lock_held_when_the_command_exits_0_or_3_and_refuses_a_call_missing_pid_or_command_with_2(
        tmp_path):
    held_repo, bare_repo = tmp_path / "held", tmp_path / "bare"
    for repo in (held_repo, bare_repo):
        repo.mkdir()
        subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"], check=True)
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])

    def shim(repo, *args):
        return subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), *args], cwd=repo,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)

    try:
        pid = str(sleeper.pid)
        assert shim(held_repo, "take", "--pid", pid).returncode == 0
        results = []
        for code in (0, 3):
            gated = shim(held_repo, "gate", "--pid", pid, "--", sys.executable, "-c", f"raise SystemExit({code})")
            held = shim(held_repo, "holder")
            results.append((gated.returncode, held.returncode, pid in held.stdout.split()))
        no_pid = shim(bare_repo, "gate", "--", sys.executable, "-c", "raise SystemExit(0)")
        no_cmd = shim(bare_repo, "gate", "--pid", pid)
        no_cmd_after_dashes = shim(bare_repo, "gate", "--pid", pid, "--")
        assert results == [(0, 0, True), (3, 0, True)]
        assert (no_pid.returncode, no_cmd.returncode, no_cmd_after_dashes.returncode) == (2, 2, 2)
        assert not (bare_repo / ".tdd" / "merge.lock").exists()
    finally:
        sleeper.kill()
        sleeper.wait()


@pytest.mark.process("merge-lock.sh gate --keep running a real command that exits 1 against a held lock in a scratch repository")
def test_2245_gate_keep_running_a_command_that_exits_1_exits_1_keeps_the_lock_for_its_pid_and_names_release_force_on_stderr(
        tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)
    pid = str(os.getpid())

    def shim(*args):
        return subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), *args], cwd=tmp_path,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)

    taken = shim("take", "--pid", pid)
    gated = shim("gate", "--keep", "--pid", pid, "--", sys.executable, "-c", "raise SystemExit(1)")
    held = shim("holder")
    assert (taken.returncode, gated.returncode, held.returncode, pid in held.stdout.split(),
            "release --force" in gated.stderr) == (0, 1, 0, True, True)


@pytest.mark.process("merge-lock.sh gate --pid of a non-holder running a real command that exits 1 against a lock held by another live pid")
def test_2245_gate_with_a_pid_that_does_not_hold_the_lock_running_a_command_that_exits_1_exits_nonzero_and_leaves_the_lock_held_by_its_holder(
        tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])

    def shim(*args):
        return subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), *args], cwd=tmp_path,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)

    try:
        holder = str(sleeper.pid)
        taken = shim("take", "--pid", holder)
        gated = shim("gate", "--pid", str(os.getpid()), "--", sys.executable, "-c", "raise SystemExit(1)")
        held = shim("holder")
        assert (taken.returncode, gated.returncode != 0, held.returncode, holder in held.stdout.split()) == (
            0, True, 0, True)
    finally:
        sleeper.kill()
        sleeper.wait()


@pytest.mark.process("merge-lock.sh gate called with --pid only after the -- against a held lock in a scratch repository")
def test_2245_gate_with_pid_only_after_the_double_dash_exits_2_naming_usage_runs_nothing_and_leaves_the_lock_held(
        tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)
    pid = str(os.getpid())
    marker = tmp_path / "ran"

    def shim(*args):
        return subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), *args], cwd=tmp_path,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)

    taken = shim("take", "--pid", pid)
    gated = shim("gate", "--", sys.executable, "-c", f"open({str(marker)!r}, 'w'); raise SystemExit(1)",
                 "--pid", pid)
    held = shim("holder")
    assert (taken.returncode, gated.returncode, "usage" in gated.stderr.lower(), marker.exists(),
            held.returncode, pid in held.stdout.split()) == (0, 2, True, False, 0, True)


@pytest.mark.process("merge-lock.sh gate called with --pid and no command in a scratch repository")
def test_2374_gate_with_pid_and_no_command_exits_2_with_the_gate_usage_line_and_no_traceback_and_creates_no_tdd(
        tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)

    gated = subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "gate", "--pid", "1"], cwd=tmp_path,
                           stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)

    assert (gated.returncode, "usage: merge-lock.sh gate" in gated.stderr, "Traceback" in gated.stderr,
            (tmp_path / ".tdd").exists()) == (2, True, False, False)


@pytest.mark.process("merge-lock.sh gate called with --pid and a -- followed by no command in a scratch repository")
def test_2374_gate_with_pid_and_a_double_dash_but_no_command_exits_2_with_the_gate_usage_line_and_no_traceback_and_creates_no_tdd(
        tmp_path):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)

    gated = subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "gate", "--pid", "1", "--"], cwd=tmp_path,
                           stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)

    assert (gated.returncode, "usage: merge-lock.sh gate" in gated.stderr, "Traceback" in gated.stderr,
            (tmp_path / ".tdd").exists()) == (2, True, False, False)
