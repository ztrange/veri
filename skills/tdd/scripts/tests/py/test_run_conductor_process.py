"""Cases for run-conductor.sh that start a real process."""
import importlib
import os
import subprocess
import sys

import pytest

from conftest import SCRIPTS


@pytest.mark.process("run-conductor.sh run as a real shim over veri/run_conductor.py, refusing an empty issue before any fetch")
def test_run_conductor_sh_with_an_empty_issue_forwards_it_to_the_module_and_returns_2_with_the_usage_line_alone(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "run-conductor.sh"), ""], cwd=tmp_path, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_BASH_MAJOR": "5",
                              "PYTHONDONTWRITEBYTECODE": "1"})

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: run-conductor.sh <issue>\n")


@pytest.mark.process("a real stub process standing in for claude -p, started by run_conductor.conduct")
def test_conduct_records_the_pid_of_the_claude_process_it_starts_in_the_worktree_conductor_pid_before_that_process_runs_issue_2249(
        tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    stub = tmp_path / "stub-claude"
    stub.write_text('#!/bin/sh\ncat "%s/.tdd/wt/2249/.tdd/conductor.pid" > "%s/seen" 2>/dev/null\necho $$ > "%s/mine"\n'
                    % (tmp_path, tmp_path, tmp_path))
    stub.chmod(0o755)
    (tmp_path / ".tdd" / "wt" / "2249").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CLAUDE_BIN", str(stub))
    monkeypatch.setenv("PATH", os.path.dirname(sys.executable) + ":/usr/bin:/bin")
    sys.path[:0] = [str(SCRIPTS)]
    from veri import run_conductor

    run_conductor.conduct("", "2249", dict(os.environ))

    assert (tmp_path / "seen").read_text().splitlines()[0] == (tmp_path / "mine").read_text().strip() != ""


@pytest.mark.process("a real git worktree, staging everything beside the kept pinned scripts and then removed")
def test_2627_the_kept_copy_is_never_staged_and_goes_with_the_worktree(tmp_path, monkeypatch):
    run_conductor = importlib.import_module("veri.run_conductor")

    def git(cwd, *argv):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv], cwd=cwd, check=True,
                              capture_output=True, text=True).stdout
    main = tmp_path / "main"
    main.mkdir()
    git(main, "init", "-q")
    git(main, "commit", "-q", "--allow-empty", "-m", "base")
    worktree = main / ".tdd" / "wt" / "7"
    git(main, "worktree", "add", "-q", "-b", "tdd/7", str(worktree))
    monkeypatch.setattr(run_conductor, "run_worktree", lambda issue: str(worktree))
    snapshot = tmp_path / "snapshot"
    (snapshot / "scripts").mkdir(parents=True)
    (snapshot / "scripts" / "tick.sh").write_text("tick\n")

    kept = run_conductor.keep_pinned_scripts(str(snapshot), "7")
    git(worktree, "add", "-A")
    staged = git(worktree, "diff", "--cached", "--name-only")
    present = (worktree / ".tdd" / "pinned-scripts" / "tick.sh").exists()
    git(main, "worktree", "remove", str(worktree))

    assert (kept, staged, present, worktree.exists()) == (True, "", True, False)
