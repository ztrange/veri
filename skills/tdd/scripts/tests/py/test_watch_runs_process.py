"""Process cases for watch-runs.sh: the shim started for real over a scratch repo of conductor pid files."""
import json
import os
import shutil
import subprocess
import time

import pytest

from conftest import SCRIPTS

SHIM = SCRIPTS / "watch-runs.sh"


def make_run(repo, issue, pid):
    run = repo / ".tdd" / "wt" / str(issue) / ".tdd"
    run.mkdir(parents=True)
    (run / ("issue-%s.md" % issue)).write_text("# Plan for #%s — title\n" % issue)
    (run / "events.jsonl").write_text(json.dumps({"event": "launch", "ts": 1, "step": 1, "issue": str(issue)}) + "\n")
    (run / "conductor.pid").write_text("%d\n" % pid)


class Conductor:
    """A claude child of a run_conductor.py <issue> process: pid is the claude's, terminate() ends both."""

    def __init__(self, proc, pid):
        self.proc = proc
        self.pid = pid

    def terminate(self):
        self.proc.terminate()

    def wait(self):
        return self.proc.wait()


def start_conductor(tmp_path, issue):
    """A live claude whose parent's command line is run_conductor.py <issue>."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    claude = bin_dir / "claude"
    claude.write_text("#!/bin/sh\nsleep 60 &\np=$!\ntrap 'kill $p; exit 0' TERM\nwait $p\n")
    claude.chmod(0o755)
    script = bin_dir / "run_conductor.py"
    script.write_text("#!/bin/sh\n\"$(dirname \"$0\")/claude\" &\np=$!\necho $p > \"$2\"\n"
                      "trap 'kill $p; wait $p; exit 0' TERM\nwait $p\n")
    script.chmod(0o755)
    pid_file = tmp_path / ("claude-%s.pid" % issue)
    proc = subprocess.Popen([str(script), str(issue), str(pid_file)])
    deadline = time.monotonic() + 10
    while not (pid_file.exists() and pid_file.read_text().strip()):
        if time.monotonic() >= deadline:
            proc.terminate()
            proc.wait()
            pytest.fail("the stub never wrote its pid file: %s" % pid_file)
        time.sleep(0.02)
    return Conductor(proc, int(pid_file.read_text()))


def watch_hook(tmp_path):
    """Env for a watcher that touches a marker file as it first goes to wait, i.e. once its snapshot of live conductors is taken."""
    hook = tmp_path / "hook"
    hook.mkdir(exist_ok=True)
    marker = tmp_path / "watcher-snapshotted"
    (hook / "sitecustomize.py").write_text(
        "import os, time\n"
        "_sleep = time.sleep\n"
        "def sleep(seconds):\n"
        "    if os.environ.get('WATCH_MARKER'):\n"
        "        open(os.environ['WATCH_MARKER'], 'w').close()\n"
        "    _sleep(seconds)\n"
        "time.sleep = sleep\n")
    env = {**os.environ, "WATCH_MARKER": str(marker),
           "PYTHONPATH": os.pathsep.join(filter(None, [str(hook), os.environ.get("PYTHONPATH")]))}
    return env, marker


def wait_for_snapshot(watcher, marker, bound=10):
    deadline = time.monotonic() + bound
    while not marker.exists():
        if time.monotonic() >= deadline:
            watcher.kill()
            watcher.wait()
            pytest.fail("the watcher never took its snapshot of the live conductors: %s" % marker)
        time.sleep(0.02)


@pytest.mark.process("watch-runs.sh as a real process over real conductor pid files")
@pytest.mark.serial("waits on a subprocess timeout of its own, which expires when every core is busy")
def test_it_exits_only_when_the_second_of_two_running_conductors_exits_printing_that_issue_1930(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    gone = subprocess.Popen(["sleep", "60"])
    gone.kill()
    gone.wait()
    watcher = subprocess.Popen(["true"])
    watcher.wait()
    first = start_conductor(tmp_path, 101)
    second = start_conductor(tmp_path, 103)
    reused = subprocess.Popen(["sleep", "60"])
    try:
        make_run(repo, 101, first.pid)
        make_run(repo, 102, gone.pid)
        make_run(repo, 103, second.pid)
        env, marker = watch_hook(tmp_path)
        watcher = subprocess.Popen([str(SHIM), "--max-wait", "15"], cwd=repo, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        wait_for_snapshot(watcher, marker)
        second.terminate()
        second.wait()
        (repo / ".tdd" / "wt" / "103" / ".tdd" / "conductor.pid").write_text("%d\n" % reused.pid)
        out, err = watcher.communicate(timeout=15)
    finally:
        if watcher.poll() is None:
            watcher.kill()
            watcher.wait()
        first.terminate()
        first.wait()
        second.terminate()
        second.wait()
        reused.kill()
        reused.wait()
    assert (watcher.returncode, out.strip()) == (0, "exited 103 stale"), err


@pytest.mark.process("watch-runs.sh as a real process over real conductor pid files and a stub solvable-issues.sh")
def test_target_slot_is_free_only_below_target_asking_for_not_running_issues_1930(tmp_path):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    shutil.copy(SCRIPTS / "veri" / "watch_runs.py", scripts / "veri" / "watch_runs.py")
    shutil.copy(SCRIPTS / "veri" / "pycache_prefix.py", scripts / "veri" / "pycache_prefix.py")
    shutil.copy(SHIM, scripts / "watch-runs.sh")
    (scripts / "lib").symlink_to(SCRIPTS / "lib")
    calls = tmp_path / "calls"
    stub = scripts / "solvable-issues.sh"
    stub.write_text('#!/bin/sh\necho "$*" >> "%s"\necho "777 next one"\necho "888 next two"\n' % calls)
    stub.chmod(0o755)
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    first = start_conductor(tmp_path, 101)
    second = start_conductor(tmp_path, 102)
    reused = subprocess.Popen(["sleep", "60"])
    try:
        make_run(repo, 101, first.pid)
        make_run(repo, 102, second.pid)
        make_run(repo, 103, reused.pid)

        def watch(*args, timeout=30):
            return subprocess.run([str(scripts / "watch-runs.sh"), *args], cwd=repo, stdin=subprocess.DEVNULL,
                                  capture_output=True, text=True, timeout=timeout,
                                  env={**os.environ, "PYTHONPATH": str(SCRIPTS / "veri")})

        full = watch("--target", "2", "--max-wait", "3")
        second.terminate()
        second.wait()
        below = watch("--target", "2", "--max-wait", "20", timeout=25)
    finally:
        first.terminate()
        first.wait()
        second.terminate()
        second.wait()
        reused.kill()
        reused.wait()
    assert (full.returncode, full.stdout.strip()) == (3, "timeout"), full.stderr
    assert below.stdout.strip() != "timeout", "the watcher timed out before observing the exit: %s" % below.stderr
    assert (below.returncode, below.stdout.strip()) == (0, "slot-free 1/2 next 777"), below.stderr
    assert calls.read_text().split("\n")[:-1] == ["--not-running"]


@pytest.mark.process("watch-runs.sh as a real process over a live conductor whose run directory has no events or pid file, and a stub solvable-issues.sh")
def test_target_slot_is_taken_by_a_live_conductor_that_has_not_written_a_launch_event_2388(tmp_path):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    shutil.copy(SCRIPTS / "veri" / "watch_runs.py", scripts / "veri" / "watch_runs.py")
    shutil.copy(SCRIPTS / "veri" / "pycache_prefix.py", scripts / "veri" / "pycache_prefix.py")
    shutil.copy(SHIM, scripts / "watch-runs.sh")
    (scripts / "lib").symlink_to(SCRIPTS / "lib")
    stub = scripts / "solvable-issues.sh"
    stub.write_text('#!/bin/sh\necho "777 next one"\n')
    stub.chmod(0o755)
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    starting = start_conductor(tmp_path, 101)
    try:
        run = repo / ".tdd" / "wt" / "101" / ".tdd"
        run.mkdir(parents=True)
        (run / "baseline-fast.pid").write_text("1\n")
        out = subprocess.run([str(scripts / "watch-runs.sh"), "--target", "1", "--max-wait", "2"], cwd=repo,
                             stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30,
                             env={**os.environ, "PYTHONPATH": str(SCRIPTS / "veri")})
    finally:
        starting.terminate()
        starting.wait()
    assert (out.returncode, out.stdout.strip()) == (3, "timeout"), out.stderr


@pytest.mark.process("watch-runs.sh as a real process over a live conductor whose run directory has no events or pid file, run from a subdirectory of the repo")
def test_target_counts_a_starting_run_when_run_from_a_subdirectory_2388(tmp_path):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    shutil.copy(SCRIPTS / "veri" / "watch_runs.py", scripts / "veri" / "watch_runs.py")
    shutil.copy(SCRIPTS / "veri" / "pycache_prefix.py", scripts / "veri" / "pycache_prefix.py")
    shutil.copy(SHIM, scripts / "watch-runs.sh")
    (scripts / "lib").symlink_to(SCRIPTS / "lib")
    stub = scripts / "solvable-issues.sh"
    stub.write_text('#!/bin/sh\necho "777 next one"\n')
    stub.chmod(0o755)
    repo = tmp_path / "repo"
    (repo / "sub").mkdir(parents=True)
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    starting = start_conductor(tmp_path, 101)
    try:
        run = repo / ".tdd" / "wt" / "101" / ".tdd"
        run.mkdir(parents=True)
        (run / "baseline-fast.pid").write_text("1\n")
        out = subprocess.run([str(scripts / "watch-runs.sh"), "--target", "1", "--max-wait", "2"], cwd=repo / "sub",
                             stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30,
                             env={**os.environ, "PYTHONPATH": str(SCRIPTS / "veri")})
    finally:
        starting.terminate()
        starting.wait()
    assert (out.returncode, out.stdout.strip()) == (3, "timeout"), out.stderr


@pytest.mark.process("watch-runs.sh as a real process over a running conductor, a live pre-conductor baseline run, and a stub solvable-issues.sh")
def test_target_counts_a_run_live_in_its_pre_conductor_baseline_2388(tmp_path):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    shutil.copy(SCRIPTS / "veri" / "watch_runs.py", scripts / "veri" / "watch_runs.py")
    shutil.copy(SCRIPTS / "veri" / "pycache_prefix.py", scripts / "veri" / "pycache_prefix.py")
    shutil.copy(SHIM, scripts / "watch-runs.sh")
    (scripts / "lib").symlink_to(SCRIPTS / "lib")
    stub = scripts / "solvable-issues.sh"
    stub.write_text('#!/bin/sh\necho "777 next one"\n')
    stub.chmod(0o755)
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    running = start_conductor(tmp_path, 101)
    baseline = start_conductor(tmp_path, 102)
    try:
        make_run(repo, 101, running.pid)
        run = repo / ".tdd" / "wt" / "102" / ".tdd"
        run.mkdir(parents=True)
        for name in ("baseline-fast", "baseline-full"):
            (run / (name + ".pid")).write_text("1\n")
            (run / (name + ".exit")).write_text("0\n")
        out = subprocess.run([str(scripts / "watch-runs.sh"), "--target", "2", "--max-wait", "2"], cwd=repo,
                             stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30,
                             env={**os.environ, "PYTHONPATH": str(SCRIPTS / "veri")})
    finally:
        running.terminate()
        running.wait()
        baseline.terminate()
        baseline.wait()
    assert (out.returncode, out.stdout.strip()) == (3, "timeout"), out.stderr


@pytest.mark.process("watch-runs.sh as a real process over a real conductor whose leaf spawns and reaps children")
def test_it_prints_exactly_one_exit_line_when_a_conductor_whose_leaf_reaps_children_exits_2249(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    claude = bin_dir / "claude"
    claude.write_text("#!/bin/sh\ntrap 'exit 0' TERM\nwhile :; do sleep 0.05 & wait $!; done\n")
    claude.chmod(0o755)
    launcher = bin_dir / "run_conductor.py"
    launcher.write_text("#!/bin/sh\n\"$(dirname \"$0\")/claude\" &\np=$!\necho $p > \"$1\"\n"
                        "trap 'kill $p; wait $p; exit 0' TERM\nwait $p\n")
    launcher.chmod(0o755)
    pid_file = tmp_path / "claude.pid"
    proc = subprocess.Popen([str(launcher), str(pid_file)])
    watcher = None
    try:
        deadline = time.monotonic() + 30
        while not (pid_file.exists() and pid_file.read_text().strip()):
            if time.monotonic() >= deadline:
                pytest.fail("the stub never wrote its pid file: %s" % pid_file)
            time.sleep(0.05)
        make_run(repo, 201, int(pid_file.read_text()))
        env, marker = watch_hook(tmp_path)
        watcher = subprocess.Popen([str(SHIM), "--max-wait", "20"], cwd=repo, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        wait_for_snapshot(watcher, marker)
        proc.terminate()
        proc.wait()
        out, err = watcher.communicate(timeout=25)
    finally:
        if watcher is not None and watcher.poll() is None:
            watcher.kill()
            watcher.wait()
        if proc.poll() is None:
            proc.terminate()
            proc.wait()
    assert out.strip().splitlines() != ["timeout"], "the watcher timed out before observing the exit: %s" % err
    assert (watcher.returncode, out.strip().splitlines()) == (0, ["exited 201 stale"]), err
