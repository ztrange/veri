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


FAKE_GH_GREEN = FAKE_GH.replace('"conclusion": "failure"', '"conclusion": "success"')

FAKE_GIT_CONFLICT = """#!/bin/sh
for word in "$@"; do
  case "$word" in
    rebase) echo "CONFLICT (content): Merge conflict in f.txt" >&2; exit 1 ;;
    push|fetch|pull) exit 0 ;;
  esac
done
exec "$REAL_GIT" "$@"
"""


@pytest.mark.process("queued-merge.sh and merge-lock.sh run as /bin/sh shims in a scratch repository, with gh and git planted on PATH")
def test_queued_merge_stopped_by_a_rebase_conflict_exits_1_and_keeps_the_merge_lock_held_2372(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    real_git = shutil.which("git")
    for args in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=veri", "-c", "user.email=veri@example.test", "commit", "-q", "--allow-empty", "-m", "initial"]):
        subprocess.run([real_git, "-C", str(repo), *args], check=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    plant(bin_dir, "gh", FAKE_GH_GREEN)
    plant(bin_dir, "git", FAKE_GIT_CONFLICT)
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "REAL_GIT": real_git,
           "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0"}
    run = dict(cwd=repo, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stopped = subprocess.run(["/bin/sh", str(SCRIPTS / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(repo), "feature", "-"],
                             timeout=30, **run)
    try:
        second = subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "take", "--pid", str(os.getpid())],
                                timeout=5, **run).returncode
    except subprocess.TimeoutExpired:
        second = "blocked"

    assert (stopped.returncode, second) == (1, "blocked")


FAKE_GIT_PUSH_REFUSED = """#!/bin/sh
for word in "$@"; do
  case "$word" in
    push) echo "! [rejected] feature -> feature (stale info)" >&2; exit 1 ;;
    rebase|fetch|pull) exit 0 ;;
  esac
done
exec "$REAL_GIT" "$@"
"""


@pytest.mark.process("queued-merge.sh and merge-lock.sh run as /bin/sh shims in a scratch repository, with gh and git planted on PATH")
def test_queued_merge_whose_push_under_the_pinned_lease_is_refused_exits_1_and_keeps_the_merge_lock_held_2372(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    real_git = shutil.which("git")
    for args in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=veri", "-c", "user.email=veri@example.test", "commit", "-q", "--allow-empty", "-m", "initial"]):
        subprocess.run([real_git, "-C", str(repo), *args], check=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    plant(bin_dir, "gh", FAKE_GH_GREEN)
    plant(bin_dir, "git", FAKE_GIT_PUSH_REFUSED)
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "REAL_GIT": real_git,
           "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0"}
    run = dict(cwd=repo, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stopped = subprocess.run(["/bin/sh", str(SCRIPTS / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(repo), "feature", "-"],
                             timeout=30, **run)
    try:
        second = subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "take", "--pid", str(os.getpid())],
                                timeout=5, **run).returncode
    except subprocess.TimeoutExpired:
        second = "blocked"

    assert (stopped.returncode, second) == (1, "blocked")


FAKE_GH_MERGING = FAKE_GH_GREEN.replace("#!/bin/sh\n", '#!/bin/sh\necho "gh $*" >> "$CALL_LOG"\n', 1)

FAKE_GIT_LOGGING = """#!/bin/sh
echo "git $*" >> "$CALL_LOG"
for word in "$@"; do
  case "$word" in
    rebase|push|fetch|pull|worktree) exit 0 ;;
  esac
done
exec "$REAL_GIT" "$@"
"""


@pytest.mark.process("queued-merge.sh and merge-lock.sh run as /bin/sh shims in a scratch repository, with gh and git planted on PATH")
def test_queued_merge_with_green_ci_rebase_merges_the_pr_for_the_pushed_head_deletes_the_branch_removes_the_worktree_exits_0_and_frees_the_merge_lock_2372(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    real_git = shutil.which("git")
    for args in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=veri", "-c", "user.email=veri@example.test", "commit", "-q", "--allow-empty", "-m", "initial"]):
        subprocess.run([real_git, "-C", str(repo), *args], check=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    plant(bin_dir, "gh", FAKE_GH_MERGING)
    plant(bin_dir, "git", FAKE_GIT_LOGGING)
    call_log = tmp_path / "calls.log"
    call_log.write_text("")
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "REAL_GIT": real_git, "CALL_LOG": str(call_log),
           "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0"}
    run = dict(cwd=repo, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    merged = subprocess.run(["/bin/sh", str(SCRIPTS / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(repo), "feature", "-"],
                            timeout=30, **run)
    try:
        second = subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "take", "--pid", str(os.getpid())],
                                timeout=5, **run).returncode
    except subprocess.TimeoutExpired:
        second = "blocked"

    calls = call_log.read_text().splitlines()
    rebase_merges = [c for c in calls if c.startswith("gh pr merge") and "--rebase" in c and "abc1234" in c]
    branch_deleted = any("--delete" in c and "feature" in c for c in calls)
    worktree_removed = any(c.startswith("git") and "worktree remove" in c for c in calls)
    assert (merged.returncode, second, len(rebase_merges), branch_deleted, worktree_removed) == (0, 0, 1, True, True)


FAKE_GH_UNMERGED = FAKE_GH_GREEN.replace(
    "case \"$*\" in\n",
    "case \"$*\" in\n"
    "  *\"pr merge\"*) exit 0 ;;\n"
    "  *\"pr view\"*--jq*|*\"pr view\"*\" -q\"*) echo OPEN ;;\n"
    "  *\"pr view\"*) echo '{\"state\": \"OPEN\", \"mergedAt\": null}' ;;\n", 1,
).replace('"draft": false,', '"draft": false, "state": "open", "merged": false,')


@pytest.mark.process("queued-merge.sh and merge-lock.sh run as /bin/sh shims in a scratch repository, with gh and git planted on PATH")
def test_queued_merge_whose_pr_is_not_merged_afterwards_exits_1_and_leaves_the_merge_lock_free_2372(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    real_git = shutil.which("git")
    for args in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=veri", "-c", "user.email=veri@example.test", "commit", "-q", "--allow-empty", "-m", "initial"]):
        subprocess.run([real_git, "-C", str(repo), *args], check=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    plant(bin_dir, "gh", FAKE_GH_UNMERGED)
    plant(bin_dir, "git", FAKE_GIT)
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "REAL_GIT": real_git,
           "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0"}
    run = dict(cwd=repo, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stopped = subprocess.run(["/bin/sh", str(SCRIPTS / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(repo), "feature", "-"],
                             timeout=30, **run)
    try:
        second = subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "take", "--pid", str(os.getpid())],
                                timeout=5, **run).returncode
    except subprocess.TimeoutExpired:
        second = "blocked"

    assert (stopped.returncode, second) == (1, 0)
