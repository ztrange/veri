"""Process cases for stack-fix.sh, the shim over veri/stack_fix.py: a real git clone of a local bare origin whose default
branch is `trunk` and whose CLAUDE.md names the stack branch `stack`, a one-test-file command and a fast tier, a stack
whose second issue turns a case red, a fix worktree under the clone's `.tdd/` holding a hand fix, and a stub gh
answering the stack's runs and taking the comments."""
import json
import os
import subprocess

import pytest

from repo_builder import git
from stub_script import write_stub

SHIM = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "stack-fix.sh"))
GH = """here="$(dirname "$0")"
echo "$*" >> "$here/calls"
case "$*" in
  *actions/runs?branch=stack*) cat "$here/runs" ;;
  *pulls?state=open*) echo '[]' ;;
  *"-X POST"*comments*) echo '{}' ;;
  *) exit 1 ;;
esac
"""
CASE = "t/test_a.py::test_x"
RUNNER = 'f="${1%%::*}"; [ -f "$f" ] || exit 4; if grep -q red src/flag; then echo "FAILED $1 - red"; exit 1; fi\n'


def red_stack(tmp_path, fast="true"):
    """A clone whose stack holds two commits on trunk: #11 adds the case and a green flag, #12 turns the flag red, and
    whose fast tier is <fast>; the clone and the red sha."""
    origin, seed, work = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "trunk", str(origin)], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "init", "-q", "-b", "trunk", str(seed)], cwd=str(tmp_path), check=True)
    (seed / "CLAUDE.md").write_text('veri: stack branch: stack\nveri: one test file: sh run.sh "$1"\n'
                                    'veri: fast tests: %s\n' % fast)
    (seed / "run.sh").write_text(RUNNER)
    (seed / ".gitignore").write_text(".tdd/\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "docs: name the stack (#10)")
    git(seed, "remote", "add", "origin", str(origin))
    git(seed, "push", "-q", "origin", "trunk")
    subprocess.run(["git", "clone", "-q", str(origin), str(work)], cwd=str(tmp_path), check=True)
    git(work, "checkout", "-q", "-b", "stack")
    (work / "t").mkdir()
    (work / "src").mkdir()
    for path, text, subject in (("t/test_a.py", "case", "feat: a (#11)"), ("src/flag", "red", "feat: b (#12)")):
        (work / path).write_text(text)
        git(work, "add", "-A")
        git(work, "commit", "-q", "-m", subject)
    git(work, "push", "-q", "origin", "stack")
    git(work, "checkout", "-q", "trunk")
    return work, git(work, "rev-parse", "origin/stack")


@pytest.mark.process("stack-fix.sh run as its /bin/sh shim in a real fix worktree of a clone of a local bare origin, with a stub gh on PATH, pushing to that origin")
def test_stack_fix_pushes_a_hand_fix_from_a_fix_worktree_to_the_stack_and_a_second_run_is_refused(tmp_path):
    work, red = red_stack(tmp_path)
    fix = work / ".tdd" / "fix"
    git(work, "worktree", "add", "-q", "--detach", str(fix), "origin/stack")
    (fix / "src" / "flag").write_text("green")
    git(fix, "commit", "-q", "-am", "fix: the flag is green again (#12)", "-m", "Stack-fix: " + red)
    culprit = tmp_path / "culprit"
    culprit.write_text("red: %s\nissue: 12\ncommit: %s\nbefore: x\ncase: %s\tFAILED %s - red\n" % (red, red, CASE, CASE))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(str(bin_dir / "gh"), GH)
    (bin_dir / "runs").write_text(json.dumps({"total_count": 1, "workflow_runs": [
        {"head_sha": red, "html_url": "https://github.com/o/r/actions/runs/42", "status": "completed",
         "conclusion": "failure", "created_at": "2026-11-16T10:00:00Z", "repository": {"full_name": "o/r"},
         "head_repository": {"full_name": "o/r"}, "run_attempt": 1, "workflow_id": 7}]}))
    env = {**os.environ, "PATH": "%s:%s" % (bin_dir, os.environ["PATH"])}

    done = subprocess.run([SHIM, "12", red, str(culprit)], cwd=str(fix), env=env, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=60)
    again = subprocess.run([SHIM, "12", red, str(culprit)], cwd=str(fix), env=env, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=60)

    head = git(fix, "rev-parse", "HEAD")
    assert (done.returncode, done.stdout, git(work, "ls-remote", "origin", "refs/heads/stack").split()[0]) == (
        0, head + "\n", head), done.stderr
    assert (again.returncode, "one fix per culprit" in again.stderr, os.path.isdir(work / ".tdd" / "merge.lock")) == (
        1, True, False), again.stderr
    assert sum("comments" in line for line in (bin_dir / "calls").read_text().splitlines()) == 1


MOVER = """[ -e "$1/moved" ] && exit 0
: > "$1/moved"
git clone -q "$1/origin.git" "$1/other" && cd "$1/other" && git checkout -q stack && echo d > other-party \\
  && git add other-party && git -c user.name=o -c user.email=o@example.com commit -q -m "feat: d (#14)" \\
  && git push -q origin stack && git rev-parse HEAD > "$1/other-sha"
"""


def mover(tmp_path):
    """A fast tier that, the first time it runs, pushes another party's commit onto origin's stack from a second
    clone, so origin's stack moves after the fetch: the command for CLAUDE.md."""
    (tmp_path / "mover.sh").write_text(MOVER)
    return "sh %s %s" % (tmp_path / "mover.sh", tmp_path)


def gh_env(tmp_path, head):
    """A stub gh in a directory of its own answering a red run on <head>: the environment to run the shim with."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(str(bin_dir / "gh"), GH)
    (bin_dir / "runs").write_text(json.dumps({"total_count": 1, "workflow_runs": [
        {"head_sha": head, "html_url": "https://github.com/o/r/actions/runs/42", "status": "completed",
         "conclusion": "failure", "created_at": "2026-11-16T10:00:00Z", "repository": {"full_name": "o/r"},
         "head_repository": {"full_name": "o/r"}, "run_attempt": 1, "workflow_id": 7}]}))
    return {**os.environ, "PATH": "%s:%s" % (bin_dir, os.environ["PATH"])}


@pytest.mark.process("stack-fix.sh run as its /bin/sh shim in a real fix worktree, its fast tier pushing another party's commit to the local bare origin from a second clone, so the leased push is refused")
def test_stack_fix_exits_1_when_origins_stack_moved_after_the_fetch_leaving_the_other_partys_commit_the_tip(tmp_path):
    work, red = red_stack(tmp_path, fast=mover(tmp_path))
    fix = work / ".tdd" / "fix"
    git(work, "worktree", "add", "-q", "--detach", str(fix), "origin/stack")
    (fix / "src" / "flag").write_text("green")
    git(fix, "commit", "-q", "-am", "fix: the flag is green again (#12)", "-m", "Stack-fix: " + red)
    culprit = tmp_path / "culprit"
    culprit.write_text("red: %s\nissue: 12\ncommit: %s\nbefore: x\ncase: %s\tFAILED %s - red\n" % (red, red, CASE, CASE))

    done = subprocess.run([SHIM, "12", red, str(culprit)], cwd=str(fix), env=gh_env(tmp_path, red), capture_output=True,
                          text=True, stdin=subprocess.DEVNULL, timeout=60)

    other = (tmp_path / "other-sha").read_text().strip()
    assert (done.returncode, done.stdout, git(work, "ls-remote", "origin", "refs/heads/stack").split()[0],
            "moved" in done.stderr, os.path.isdir(work / ".tdd" / "merge.lock")) == (1, "", other, True, False), done.stderr


@pytest.mark.process("stack-fix.sh run as its /bin/sh shim with bad arguments")
def test_stack_fix_refuses_bad_arguments_with_its_usage(tmp_path):
    done = subprocess.run([SHIM, "12"], cwd=str(tmp_path), capture_output=True, text=True, stdin=subprocess.DEVNULL,
                          timeout=60)

    assert (done.returncode, "usage: stack-fix.sh <n> <red-sha> <culprit-file>" in done.stderr) == (2, True), done.stderr
