"""Process cases for watch-runs.sh: the shim started for real over a scratch repo of conductor pid files."""
import json
import subprocess
import time

import pytest

from conftest import SCRIPTS

SHIM = SCRIPTS / "watch-runs.sh"


def make_run(repo, issue, pid):
    run = repo / ".tdd" / "wt" / str(issue) / ".tdd"
    run.mkdir(parents=True)
    (run / ("issue-%s.md" % issue)).write_text("# Plan for #%s — title\n" % issue)
    (run / "events.jsonl").write_text(json.dumps({"event": "launch", "ts": 1, "step": 1}) + "\n")
    (run / "conductor.pid").write_text("%d\n" % pid)


@pytest.mark.process("watch-runs.sh as a real process over real conductor pid files")
def test_it_exits_only_when_the_second_of_two_running_conductors_exits_printing_that_issue_1930(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    gone = subprocess.Popen(["sleep", "60"])
    gone.kill()
    gone.wait()
    watcher = subprocess.Popen(["true"])
    watcher.wait()
    first = subprocess.Popen(["sleep", "60"])
    second = subprocess.Popen(["sleep", "60"])
    try:
        make_run(repo, 101, first.pid)
        make_run(repo, 102, gone.pid)
        make_run(repo, 103, second.pid)
        watcher = subprocess.Popen([str(SHIM)], cwd=repo, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(1)
        second.kill()
        second.wait()
        out, err = watcher.communicate(timeout=20)
    finally:
        if watcher.poll() is None:
            watcher.kill()
            watcher.wait()
        first.kill()
        first.wait()
        second.kill()
        second.wait()
    assert (watcher.returncode, out.strip()) == (0, "exited 103 stale"), err
