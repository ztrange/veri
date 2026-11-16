"""run-finished.sh's entry point: the shim runs veri/run_finished.py and passes its exit code and output through,
and a running run, which needs a live conductor process. The module's logic is tested in-process, in
tests/py/unit/test_run_finished.py."""
import importlib
import json
import os
import subprocess
import time

import pytest

from conftest import SCRIPTS

FINISHED = str(SCRIPTS / "run-finished.sh")
LAUNCH = '{"ts":%s,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}'
DONE = '{"ts":1001,"event":"done","pr":"https://github.com/o/r/pull/7"}'
STEP = "- [x] first step ⟦criterion 1⟧\n"


def git_init(path):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    for key, value in (("user.name", "Test"), ("user.email", "test@example.com")):
        subprocess.run(["git", "-C", str(path), "config", key, value], check=True)


def make_run(tmp_path, events, steps=STEP):
    repo = tmp_path / "repo"
    git_init(repo)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "--allow-empty", "-m", "init"], check=True)
    run = repo / ".tdd" / "wt" / "4242"
    git_init(run)
    (run / ".tdd").mkdir(exist_ok=True)
    (run / ".tdd" / "events.jsonl").write_text("".join(e + "\n" for e in events))
    (run / ".tdd" / "issue-4242.md").write_text("# Plan for #4242 — a title\n\n" + steps)
    return repo


def fake_gh(tmp_path, script):
    bin = tmp_path / "bin"
    bin.mkdir(exist_ok=True)
    (bin / "gh").write_text("#!/bin/sh\n" + script)
    (bin / "gh").chmod(0o755)
    return {**os.environ, "PATH": "%s:%s" % (bin, os.environ["PATH"])}


def finish_with_gh(repo, tmp_path, script):
    env = fake_gh(tmp_path, script)
    ran = subprocess.run([FINISHED, "4242"], cwd=repo, capture_output=True, text=True, env=env)
    return ran.returncode, ran.stdout, ran.stderr


def finish(repo, tmp_path, body=None):
    if body is None:
        ran = subprocess.run([FINISHED, "4242"], cwd=repo, capture_output=True, text=True)
        return ran.returncode, ran.stdout, ran.stderr
    (tmp_path / "body").write_text(json.dumps({"body": body}))
    return finish_with_gh(repo, tmp_path, 'cat "%s"\n' % (tmp_path / "body"))


@pytest.mark.process("run-finished.sh on a running run")
def test_a_running_run_exits_1_and_prints_a_not_done_line_naming_the_running_state(tmp_path):
    repo = make_run(tmp_path, [(LAUNCH % int(time.time()))[:-1] + ',"issue":"4242"}'])
    claude = tmp_path / "claude"
    claude.write_text("#!/bin/sh\nsleep 30\n")
    claude.chmod(0o755)
    conductor = tmp_path / "run_conductor.py"
    conductor.write_text("#!/bin/sh\n\"$(dirname \"$0\")/claude\" &\necho $! > \"$2\"\nwait\n")
    conductor.chmod(0o755)
    claude_pid = tmp_path / "claude.pid"
    child = subprocess.Popen([str(conductor), "4242", str(claude_pid)])
    try:
        deadline = time.monotonic() + 10
        while not (claude_pid.exists() and claude_pid.read_text().strip()):
            if time.monotonic() >= deadline:
                pytest.fail("the stub never wrote its pid file: %s" % claude_pid)
            time.sleep(0.02)
        (repo / ".tdd" / "wt" / "4242" / ".tdd" / "conductor.pid").write_text(claude_pid.read_text())

        code, out, _ = finish(repo, tmp_path)
    finally:
        if claude_pid.exists() and claude_pid.read_text().strip():
            os.kill(int(claude_pid.read_text()), 9)
        child.kill()
        child.wait()

    assert code == 1
    assert out.startswith("not-done running")


def usage():
    return importlib.import_module("veri.run_finished").USAGE


@pytest.mark.process("run-finished.sh on a done run, with a fake gh answering the PR body")
def test_the_shim_passes_exit_0_through_for_a_finished_run(tmp_path):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE])

    assert finish(repo, tmp_path, "Closes #4242") == (0, "", "")


@pytest.mark.process("run-finished.sh on a done run with an unchecked step, with a fake gh")
def test_the_shim_passes_exit_1_and_the_modules_stdout_through_for_an_unfinished_run(tmp_path):
    repo = make_run(tmp_path, [LAUNCH % 1000, DONE], STEP + "- [ ] second step ⟦criterion 2⟧\n")

    assert finish(repo, tmp_path, "Closes #4242") == (1, "unchecked second step ⟦criterion 2⟧\n", "")


@pytest.mark.process("run-finished.sh run as a script")
def test_the_shim_passes_exit_2_and_the_modules_stderr_through_for_no_arguments(tmp_path):
    ran = subprocess.run([FINISHED], cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", usage())


@pytest.mark.process("run-finished.sh run as a script")
def test_help_prints_the_modules_usage_on_stdout_and_exits_0(tmp_path):
    ran = subprocess.run([FINISHED, "--help"], cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == (0, usage(), "")

