"""Process cases for stack-revert.sh, the shim over veri/stack_revert.py: a real git clone of a local bare origin whose
default branch is `trunk` and whose CLAUDE.md names the stack branch `stack` and a fast tier, a stack holding issue
#12's commit and its hand fix above another issue's, and a stub gh answering the stack's runs and merged pull requests
and taking the body edit and the comments."""
import json
import os
import subprocess

import pytest

from repo_builder import git
from stub_script import write_stub
from test_stack_fix_process import red_stack

SHIM = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "stack-revert.sh"))
GH = """here="$(dirname "$0")"
echo "$*" >> "$here/calls"
case "$*" in
  *actions/runs?branch=stack*) cat "$here/runs" ;;
  "pr list --base stack"*) cat "$here/merged" ;;
  *pulls?state=open*) echo '[]' ;;
  *"-X PATCH"*pulls/41*) echo '{}' ;;
  *"-X POST"*comments*) echo '{}' ;;
  *) exit 1 ;;
esac
"""


@pytest.mark.process("stack-revert.sh run as its /bin/sh shim in a clone of a local bare origin holding a stack, with a stub gh on PATH, adding and removing a real worktree and pushing to that origin")
def test_stack_revert_reverts_the_culprit_and_its_hand_fix_on_top_and_lifts_its_claim(tmp_path):
    work, red = red_stack(tmp_path)
    git(work, "checkout", "-q", "stack")
    (work / "src" / "other").write_text("c")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "feat: c (#13)")
    (work / "src" / "flag").write_text("green")
    git(work, "commit", "-q", "-am", "fix: the flag (#12)", "-m", "Stack-fix: " + red)
    git(work, "push", "-q", "origin", "stack")
    fix = git(work, "rev-parse", "HEAD")
    git(work, "checkout", "-q", "trunk")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(str(bin_dir / "gh"), GH)
    (bin_dir / "runs").write_text(json.dumps({"total_count": 1, "workflow_runs": [
        {"head_sha": fix, "html_url": "https://github.com/o/r/actions/runs/43", "status": "completed",
         "conclusion": "failure", "created_at": "2026-11-16T10:00:00Z", "repository": {"full_name": "o/r"},
         "head_repository": {"full_name": "o/r"}, "run_attempt": 1, "workflow_id": 7}]}))
    (bin_dir / "merged").write_text(json.dumps([{"number": 41, "body": "Closes #12", "state": "MERGED",
                                                 "baseRefName": "stack", "isCrossRepository": False}]))
    env = {**os.environ, "PATH": "%s:%s" % (bin_dir, os.environ["PATH"]), "VERI_GH_DRIVER": "graphql"}

    done = subprocess.run([SHIM, "12"], cwd=str(work), env=env, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=60)

    tip = git(work, "ls-remote", "origin", "refs/heads/stack").split()[0]
    git(work, "fetch", "-q", "origin")
    assert (done.returncode, done.stdout, git(work, "rev-parse", "origin/stack~1")) == (0, tip + "\n", fix), done.stderr
    assert (git(work, "log", "-1", "--format=%s", "origin/stack").endswith("(#12)"),
            git(work, "ls-tree", "-r", "--name-only", "origin/stack").split()) == (
        True, [".gitignore", "CLAUDE.md", "run.sh", "src/other", "t/test_a.py"])
    calls = (bin_dir / "calls").read_text()
    assert ("body=Reverted from stack by " + tip in calls, calls.count("comments"), "/labels" in calls) == (True, 1, False)
    assert (git(work, "worktree", "list", "--porcelain").count("worktree "), os.path.isdir(work / ".tdd" / "merge.lock")) == (
        1, False)


@pytest.mark.process("stack-revert.sh run as its /bin/sh shim with bad arguments")
def test_stack_revert_refuses_bad_arguments_with_its_usage(tmp_path):
    done = subprocess.run([SHIM], cwd=str(tmp_path), capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)

    assert (done.returncode, "usage: stack-revert.sh <n>" in done.stderr) == (2, True), done.stderr
