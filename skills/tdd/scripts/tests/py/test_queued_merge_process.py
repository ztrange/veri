"""queued-merge.sh through the real /bin/sh shim, with gh and git faked on PATH."""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]

FAKE_GH = """#!/bin/sh
case "$*" in
  *"check-runs?page=1"*) echo '{"check_runs": [{"name": "CI", "status": "completed", "conclusion": "failure"}]}' ;;
  *check-runs*) echo '{"check_runs": []}' ;;
  *"/status"*) echo '{"statuses": []}' ;;
  *"/pulls/"*) echo '{"merged": true, "merge_commit_sha": "fedcba9", "mergeable": true, "draft": false, "head": {"sha": "abc1234"}}' ;;
  *) echo '[]' ;;
esac
exit 0
"""

FAKE_GIT = """#!/bin/sh
case "$*" in
  *"rev-parse --verify refs/remotes/origin/"*) echo 1111111; exit 0 ;;
  *"rev-parse --verify HEAD"*) echo abc1234; exit 0 ;;
  *"merge-base --is-ancestor"*|*"cat-file -e"*) exit 0 ;;
esac
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
case "$*" in
  *"rev-parse --verify refs/remotes/origin/"*) echo 1111111; exit 0 ;;
  *"rev-parse --verify HEAD"*) echo abc1234; exit 0 ;;
  *"merge-base --is-ancestor"*|*"cat-file -e"*) exit 0 ;;
esac
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
echo "git $*" >> "$CALL_LOG"
case " $* " in
  *" push --force-with-lease=feature:1111111 "*) echo "! [rejected] feature -> feature (stale info)" >&2; exit 1 ;;
esac
case "$*" in
  *"rev-parse --verify refs/remotes/origin/"*) echo 1111111; exit 0 ;;
  *"rev-parse --verify HEAD"*) echo abc1234; exit 0 ;;
  *"merge-base --is-ancestor"*|*"cat-file -e"*) exit 0 ;;
esac
for word in "$@"; do
  case "$word" in
    push|rebase|fetch|pull|worktree) exit 0 ;;
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
    call_log = tmp_path / "calls.log"
    call_log.write_text("")
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "REAL_GIT": real_git, "CALL_LOG": str(call_log),
           "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0"}
    run = dict(cwd=repo, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    stopped = subprocess.run(["/bin/sh", str(SCRIPTS / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(repo), "feature", "-"],
                             timeout=30, **run)
    try:
        second = subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "take", "--pid", str(os.getpid())],
                                timeout=5, **run).returncode
    except subprocess.TimeoutExpired:
        second = "blocked"

    pushes = [c.split() for c in call_log.read_text().splitlines() if " push " in c]
    assert (stopped.returncode, second, pushes) == (
        1, "blocked", [["git", "-C", str(repo), "push", "--force-with-lease=feature:1111111", "origin", "feature"]])


FAKE_GH_MERGING = FAKE_GH_GREEN.replace("#!/bin/sh\n", '#!/bin/sh\necho "gh $*" >> "$CALL_LOG"\n', 1)

FAKE_GIT_LOGGING = """#!/bin/sh
echo "git $*" >> "$CALL_LOG"
case "$*" in
  *"rev-parse --verify refs/remotes/origin/"*) echo 1111111; exit 0 ;;
  *"rev-parse --verify HEAD"*) echo abc1234; exit 0 ;;
  *"merge-base --is-ancestor"*|*"cat-file -e"*|*"branch -D"*) exit 0 ;;
esac
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
           "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0", "VERI_GH_DRIVER": "graphql"}
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
    worktree_removes = [i for i, c in enumerate(calls) if c.startswith("git") and "worktree remove" in c]
    local_deletes = [i for i, c in enumerate(calls) if c.startswith("git") and c.endswith(" branch -D feature")]
    deleted_once_after_remove = len(local_deletes) == 1 and bool(worktree_removes) and local_deletes[0] > worktree_removes[-1]
    assert (merged.returncode, second, len(rebase_merges), branch_deleted, bool(worktree_removes), deleted_once_after_remove) == (
        0, 0, 1, True, True, True)


FAKE_GH_UNMERGED = FAKE_GH_GREEN.replace(
    "case \"$*\" in\n",
    "case \"$*\" in\n"
    "  *\"pr merge\"*) exit 0 ;;\n"
    "  *\"pr view\"*--jq*|*\"pr view\"*\" -q\"*) echo OPEN ;;\n"
    "  *\"pr view\"*) echo '{\"state\": \"OPEN\", \"mergedAt\": null}' ;;\n", 1,
).replace('"merged": true,', '"merged": false, "state": "open",')


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


FAKE_GIT_TAGGING = """#!/bin/sh
echo "git $*" >> "$CALL_LOG"
case "$*" in
  *"tag --sort"*|*"tag -l"*|*"tag --list"*) exec "$REAL_GIT" "$@" ;;
esac
case "$*" in
  *"rev-parse --verify refs/remotes/origin/"*) echo 1111111; exit 0 ;;
  *"rev-parse --verify HEAD"*) echo abc1234; exit 0 ;;
  *"merge-base --is-ancestor"*|*"cat-file -e"*|*"branch -D"*) exit 0 ;;
esac
for word in "$@"; do
  case "$word" in
    rebase|push|fetch|pull|worktree|tag) exit 0 ;;
  esac
done
exec "$REAL_GIT" "$@"
"""


@pytest.mark.timeout(90)
@pytest.mark.process("queued-merge.sh and merge-lock.sh run as /bin/sh shims in a scratch repository, with gh and git planted on PATH")
def test_queued_merge_after_a_confirmed_merge_cuts_the_next_version_tag_on_the_reported_merge_commit_with_the_message_and_pushes_it_but_cuts_none_for_a_dash_2372(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    real_git = shutil.which("git")
    for args in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=veri", "-c", "user.email=veri@example.test", "commit", "-q", "--allow-empty", "-m", "initial"],
                 ["tag", "v0.2"], ["tag", "v0.9"], ["tag", "v0.10"]):
        subprocess.run([real_git, "-C", str(repo), *args], check=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    plant(bin_dir, "gh", FAKE_GH_MERGING)
    plant(bin_dir, "git", FAKE_GIT_TAGGING)
    call_log = tmp_path / "calls.log"
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "REAL_GIT": real_git, "CALL_LOG": str(call_log),
           "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0"}
    run = dict(cwd=repo, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def queued(message):
        call_log.write_text("")
        code = subprocess.run(["/bin/sh", str(SCRIPTS / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(repo), "feature", message],
                              timeout=30, **run).returncode
        return code, call_log.read_text().splitlines()

    code, calls = queued("the capability")
    tag_cmds = [c for c in calls if " tag " in c and "v0.11" in c and "-a" in c and "the capability" in c and c.split()[-1] == "fedcba9"]
    pushed = [c for c in calls if " push " in c and "v0.11" in c]
    dash_code, dash_calls = queued("-")
    dash_tagged = [c for c in dash_calls if "v0.11" in c]

    assert (code, len(tag_cmds), len(pushed), dash_code, dash_tagged) == (0, 1, 1, 0, [])


@pytest.mark.process("queued-merge.sh and merge-lock.sh run as /bin/sh shims in a scratch repository, with gh and git planted on PATH")
def test_queued_merge_finding_a_lock_left_by_a_dead_holder_reports_it_on_stderr_naming_that_holder_2372(tmp_path):
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
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    dead = str(child.pid)

    def lock(*args):
        return subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), *args], cwd=repo, env=env,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)

    lock("take", "--pid", dead)
    errfile = tmp_path / "queued.err"
    with open(errfile, "w") as err:
        queued = subprocess.Popen(["/bin/sh", str(SCRIPTS / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(repo), "feature", "-"],
                                  cwd=repo, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=err)
    try:
        deadline = time.monotonic() + 10
        while not errfile.read_text() and queued.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        reported = errfile.read_text()
        lock("release", "--force")
        try:
            queued.wait(timeout=20)
        except subprocess.TimeoutExpired:
            queued.kill()
        assert (dead in reported.split(), "stale" in reported.lower()) == (True, True)
    finally:
        if queued.poll() is None:
            queued.kill()
        queued.communicate()


@pytest.mark.tree_audit("copies the scripts directory into the linked worktree")
@pytest.mark.process("queued-merge.sh and merge-lock.sh run as /bin/sh shims from a copy inside a real linked worktree, with gh and remote git planted on PATH")
def test_queued_merge_run_from_the_scripts_of_the_worktree_it_removes_leaves_the_merge_lock_free_2871(tmp_path):
    primary = tmp_path / "primary"
    primary.mkdir()
    real_git = shutil.which("git")
    for args in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=veri", "-c", "user.email=veri@example.test", "commit", "-q", "--allow-empty", "-m", "initial"],
                 ["worktree", "add", "-q", "-b", "feature", str(tmp_path / "wt")]):
        subprocess.run([real_git, "-C", str(primary), *args], check=True)
    worktree = tmp_path / "wt"
    (primary / ".git" / "info" / "exclude").write_text("scripts-copy/\n")
    copied = worktree / "scripts-copy"
    shutil.copytree(SCRIPTS, copied, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    plant(bin_dir, "gh", FAKE_GH_GREEN)
    plant(bin_dir, "git", FAKE_GIT)
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "REAL_GIT": real_git,
           "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0"}
    run = dict(env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    subprocess.run(["/bin/sh", str(copied / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(worktree), "feature", "-"],
                   cwd=worktree, timeout=30, **run)
    try:
        second = subprocess.run(["/bin/sh", str(SCRIPTS / "merge-lock.sh"), "take", "--pid", str(os.getpid())],
                                cwd=primary, timeout=5, **run).returncode
    except subprocess.TimeoutExpired:
        second = "blocked"

    assert second == 0


FAKE_GIT_LOCAL_PULL = FAKE_GIT.replace('rebase|push|fetch|pull) exit 0 ;;', 'rebase|push|fetch) exit 0 ;;')


@pytest.mark.tree_audit("copies the scripts directory into the linked worktree")
@pytest.mark.process("queued-merge.sh and merge-lock.sh run as /bin/sh shims from a copy inside a real linked worktree, with gh and remote git planted on PATH")
def test_queued_merge_run_from_the_scripts_of_the_worktree_it_removes_fast_forwards_main_and_exits_0_2871(tmp_path):
    primary = tmp_path / "primary"
    primary.mkdir()
    real_git = shutil.which("git")
    ident = ["-c", "user.name=veri", "-c", "user.email=veri@example.test"]
    for args in (["init", "-q", "-b", "main"],
                 [*ident, "commit", "-q", "--allow-empty", "-m", "initial"],
                 ["worktree", "add", "-q", "-b", "feature", str(tmp_path / "wt")],
                 [*ident, "commit", "-q", "--allow-empty", "-m", "merged upstream"],
                 ["update-ref", "refs/remotes/origin/main", "HEAD"],
                 ["reset", "-q", "--hard", "HEAD~1"]):
        subprocess.run([real_git, "-C", str(primary), *args], check=True)
    upstream = subprocess.run([real_git, "-C", str(primary), "rev-parse", "refs/remotes/origin/main"],
                              check=True, capture_output=True, text=True).stdout.strip()
    worktree = tmp_path / "wt"
    (primary / ".git" / "info" / "exclude").write_text("scripts-copy/\n")
    copied = worktree / "scripts-copy"
    shutil.copytree(SCRIPTS, copied, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    plant(bin_dir, "gh", FAKE_GH_GREEN)
    plant(bin_dir, "git", FAKE_GIT_LOCAL_PULL)
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "REAL_GIT": real_git,
           "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0"}

    run = subprocess.run(["/bin/sh", str(copied / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(worktree), "feature", "-"],
                         cwd=worktree, timeout=30, env=env, stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    main_tip = subprocess.run([real_git, "-C", str(primary), "rev-parse", "main"],
                              capture_output=True, text=True).stdout.strip()

    assert (run.returncode, main_tip) == (0, upstream), run.stderr


FAKE_GIT_LOSING_RELEASE_SCRIPT = FAKE_GIT.replace(
    "case \"$*\" in\n",
    "case \"$*\" in\n"
    "  *\"branch -D\"*) rm -f \"$TMPDIR\"/queued-merge-scripts-*/scripts/merge-lock.sh ;;\n", 1)


@pytest.mark.process("queued-merge.sh runs as a /bin/sh shim in a scratch repository, with gh and git planted on PATH")
def test_queued_merge_whose_merge_lock_release_cannot_be_started_names_release_in_the_cleanup_failure_and_exits_2_2871(tmp_path):
    primary = tmp_path / "primary"
    primary.mkdir()
    real_git = shutil.which("git")
    for args in (["init", "-q", "-b", "main"],
                 ["-c", "user.name=veri", "-c", "user.email=veri@example.test", "commit", "-q", "--allow-empty", "-m", "initial"],
                 ["worktree", "add", "-q", "-b", "feature", str(tmp_path / "wt")]):
        subprocess.run([real_git, "-C", str(primary), *args], check=True)
    scratch = tmp_path / "tmp"
    scratch.mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    plant(bin_dir, "gh", FAKE_GH_GREEN)
    plant(bin_dir, "git", FAKE_GIT_LOSING_RELEASE_SCRIPT)
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "REAL_GIT": real_git, "TMPDIR": str(scratch),
           "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0"}

    run = subprocess.run(["/bin/sh", str(SCRIPTS / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(tmp_path / "wt"), "feature", "-"],
                         cwd=primary, timeout=30, env=env, stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    assert (run.returncode, "FileNotFoundError" in run.stderr, "merged, but cleanup failed: release" in run.stderr) == (2, False, True), run.stderr
