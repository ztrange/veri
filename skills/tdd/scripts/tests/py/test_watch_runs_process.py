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


def start_conductor(tmp_path, issue):
    """A live process whose command line is run-conductor.sh <issue>; terminate() ends it."""
    script = tmp_path / "bin" / "run-conductor.sh"
    script.parent.mkdir(exist_ok=True)
    script.write_text("#!/bin/sh\nsleep 60 &\np=$!\ntrap 'kill $p; exit 0' TERM\nwait $p\n")
    script.chmod(0o755)
    proc = subprocess.Popen([str(script), str(issue)])
    time.sleep(0.3)
    return proc


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
        watcher = subprocess.Popen([str(SHIM), "--max-wait", "10"], cwd=repo, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(1)
        second.terminate()
        second.wait()
        (repo / ".tdd" / "wt" / "103" / ".tdd" / "conductor.pid").write_text("%d\n" % reused.pid)
        out, err = watcher.communicate(timeout=20)
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
    shutil.copy(SHIM, scripts / "watch-runs.sh")
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

        def watch(*args):
            return subprocess.run([str(scripts / "watch-runs.sh"), *args], cwd=repo, stdin=subprocess.DEVNULL,
                                  capture_output=True, text=True, timeout=30,
                                  env={**os.environ, "PYTHONPATH": str(SCRIPTS / "veri")})

        full = watch("--target", "2", "--max-wait", "3")
        second.terminate()
        second.wait()
        below = watch("--target", "2", "--max-wait", "3")
    finally:
        first.terminate()
        first.wait()
        second.terminate()
        second.wait()
        reused.kill()
        reused.wait()
    assert (full.returncode, full.stdout.strip()) == (3, "timeout"), full.stderr
    assert (below.returncode, below.stdout.strip()) == (0, "slot-free 1/2 next 777"), below.stderr
    assert calls.read_text().split("\n")[:-1] == ["--not-running"]
