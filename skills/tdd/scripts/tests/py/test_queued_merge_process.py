"""queued-merge.sh through the real /bin/sh shim, with gh and git faked on PATH."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]

FAKE_GH = """#!/bin/sh
case "$*" in
  *check-runs*) echo '{"check_runs": [{"name": "CI", "status": "completed", "conclusion": "failure"}]}' ;;
  *"/status"*) echo '{"statuses": []}' ;;
  *"/pulls/"*) echo '{"mergeable": true, "draft": false, "head": {"sha": "abc1234"}}' ;;
  *) echo '[]' ;;
esac
exit 0
"""

FAKE_GIT = """#!/bin/sh
for word in "$@"; do
  case "$word" in
    rebase|push|fetch|pull) exit 0 ;;
  esac
done
exec "$REAL_GIT" "$@"
"""


def plant(directory, name, body):
    path = directory / name
    path.write_text(body)
    path.chmod(0o755)


@pytest.mark.process("queued-merge.sh and merge-lock.sh run as /bin/sh shims in a scratch repository, with gh and git planted on PATH")
def test_queued_merge_stopped_by_red_ci_exits_1_and_leaves_the_merge_lock_free_for_a_second_queued_merge_2372(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    real_git = shutil.which("git")
    for args in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=veri", "-c", "user.email=veri@example.test", "commit", "-q", "--allow-empty", "-m", "initial"]):
        subprocess.run([real_git, "-C", str(repo), *args], check=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    plant(bin_dir, "gh", FAKE_GH)
    plant(bin_dir, "git", FAKE_GIT)
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "REAL_GIT": real_git,
           "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0"}
    run = dict(cwd=repo, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    merged = subprocess.run(["/bin/sh", str(SCRIPTS / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(repo), "feature", "-"],
                            timeout=30, **run)
    try:
        second = subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "take", "--pid", str(os.getpid())],
                                timeout=5, **run).returncode
    except subprocess.TimeoutExpired:
        second = "blocked"

    assert (merged.returncode, second) == (1, 0)
