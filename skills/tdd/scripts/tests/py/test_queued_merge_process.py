"""queued-merge.sh through the real /bin/sh shim, with gh and git faked on PATH."""
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]

FAKE_GH = """#!/bin/sh
marker="$(dirname "$0")/.merge-landed"
for a in "$@"; do
  case "$a" in merge|*/merge) : > "$marker" ;; esac
done
case "$*" in
  *"check-runs?page=1"*) echo '{"check_runs": [{"name": "CI", "status": "completed", "conclusion": "failure"}]}' ;;
  *check-runs*) echo '{"check_runs": []}' ;;
  *"/status"*) echo '{"statuses": []}' ;;
  *"/pulls/"*) if [ -e "$marker" ]; then echo '{"merged": true, "merge_commit_sha": "fedcba9", "mergeable": true, "draft": false, "head": {"sha": "abc1234abc1234abc1234abc1234abc1234abcde"}}'; else echo '{"state": "open", "merged": false, "mergeable": true, "draft": false, "head": {"sha": "abc1234abc1234abc1234abc1234abc1234abcde"}}'; fi ;;
  *) echo '[]' ;;
esac
exit 0
"""

FAKE_GIT = """#!/bin/sh
case "$*" in
  *"rev-parse --verify refs/remotes/origin/"*) echo 1111111; exit 0 ;;
  *"rev-parse --verify HEAD"*) echo abc1234abc1234abc1234abc1234abc1234abcde; exit 0 ;;
  *"diff --name-only origin/main...HEAD"*) exit 0 ;;
  *"merge-base --is-ancestor"*"origin/main"*) exit 1 ;;
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
  *"rev-parse --verify HEAD"*) echo abc1234abc1234abc1234abc1234abc1234abcde; exit 0 ;;
  *"diff --name-only origin/main...HEAD"*) exit 0 ;;
  *"merge-base --is-ancestor"*"origin/main"*) exit 1 ;;
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
  *"rev-parse --verify HEAD"*) echo abc1234abc1234abc1234abc1234abc1234abcde; exit 0 ;;
  *"diff --name-only origin/main...HEAD"*) exit 0 ;;
  *"merge-base --is-ancestor"*"origin/main"*) exit 1 ;;
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

    pushes = [c.split()[:-1] for c in call_log.read_text().splitlines() if " push " in c]
    assert (stopped.returncode, second, pushes) == (
        1, "blocked", [["git", "-C", str(repo), "push", "--force-with-lease=feature:1111111", "origin"]])


FAKE_GH_MERGING = FAKE_GH_GREEN.replace("#!/bin/sh\n", '#!/bin/sh\necho "gh $*" >> "$CALL_LOG"\n', 1)

FAKE_GIT_LOGGING = """#!/bin/sh
echo "git $*" >> "$CALL_LOG"
case "$*" in
  *"rev-parse --verify refs/remotes/origin/"*) echo 1111111; exit 0 ;;
  *"rev-parse --verify HEAD"*) echo abc1234abc1234abc1234abc1234abc1234abcde; exit 0 ;;
  *"diff --name-only origin/main...HEAD"*) exit 0 ;;
  *"merge-base --is-ancestor"*"origin/main"*) exit 1 ;;
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
    rebase_merges = [c for c in calls if c.startswith("gh pr merge") and "--rebase" in c and "abc1234abc1234abc1234abc1234abc1234abcde" in c]
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
  *"rev-parse --verify HEAD"*) echo abc1234abc1234abc1234abc1234abc1234abcde; exit 0 ;;
  *"diff --name-only origin/main...HEAD"*) exit 0 ;;
  *"merge-base --is-ancestor"*"origin/main"*) exit 1 ;;
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

    started = []

    def queued(message):
        call_log.write_text("")
        (bin_dir / ".merge-landed").unlink(missing_ok=True)
        proc = subprocess.Popen(["/bin/sh", str(SCRIPTS / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(repo), "feature", message],
                                start_new_session=True, **run)
        started.append(proc)
        proc.communicate(timeout=30)
        return proc.returncode, call_log.read_text().splitlines()

    try:
        code, calls = queued("the capability")
        tag_cmds = [c for c in calls if " tag " in c and "v0.11" in c and "-a" in c and "the capability" in c and c.split()[-1] == "fedcba9"]
        pushed = [c for c in calls if " push " in c and "v0.11" in c]
        dash_code, dash_calls = queued("-")
        dash_tagged = [c for c in dash_calls if "v0.11" in c]

        assert (code, len(tag_cmds), len(pushed), dash_code, dash_tagged) == (0, 1, 1, 0, [])
    finally:
        for proc in started:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()


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

    (repo / ".tdd" / "merge.lock").mkdir(parents=True)
    (repo / ".tdd" / "merge.lock" / "holder").write_text(f"{dead} {socket.gethostname()} gone\n")
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


FAKE_GH_HEAD_OF_WORKTREE = """#!/bin/sh
marker="$(dirname "$0")/.merge-landed"
for a in "$@"; do
  case "$a" in merge|*/merge) : > "$marker" ;; esac
done
head=$("$REAL_GIT" -C "$WORKTREE" rev-parse HEAD)
case "$*" in
  *"check-runs?page=1"*) echo '{"check_runs": [{"name": "CI", "status": "completed", "conclusion": "failure"}]}' ;;
  *check-runs*) echo '{"check_runs": []}' ;;
  *"/status"*) echo '{"statuses": []}' ;;
  *"/pulls/"*) if [ -e "$marker" ]; then echo "{\\"merged\\": false, \\"mergeable\\": true, \\"draft\\": false, \\"head\\": {\\"sha\\": \\"$head\\"}}"; else echo "{\\"state\\": \\"open\\", \\"merged\\": false, \\"mergeable\\": true, \\"draft\\": false, \\"head\\": {\\"sha\\": \\"$head\\"}}"; fi ;;
  *) echo '[]' ;;
esac
exit 0
"""


FAKE_GIT_MOVING_REMOTE = """#!/bin/sh
case "$*" in
  *"merge-base --is-ancestor"*"origin/main"*) exit 1 ;;
  *" rebase "*)
    "$REAL_GIT" "$@" || exit $?
    if [ -n "$MOVE_REMOTE" ]; then
      "$REAL_GIT" -C "$MOVE_REMOTE" -c user.name=veri -c user.email=veri@example.test commit -q --allow-empty -m raced || exit 1
      "$REAL_GIT" -C "$MOVE_REMOTE" push -q origin HEAD:refs/heads/feature || exit 1
    fi
    exit 0 ;;
esac
exec "$REAL_GIT" "$@"
"""


@pytest.mark.process("queued-merge.sh runs as a /bin/sh shim against real git, a scratch bare remote and a detached-HEAD worktree, with gh planted on PATH")
def test_queued_merge_lease_push_from_a_detached_head_updates_the_remote_branch_but_a_remote_moved_past_the_lease_is_still_refused_3459(tmp_path):
    real_git = shutil.which("git")
    ident = ["-c", "user.name=veri", "-c", "user.email=veri@example.test"]

    def git(repo, *args):
        done = subprocess.run([real_git, "-C", str(repo), *ident, *args], check=True, capture_output=True, text=True, cwd=tmp_path)
        return done.stdout.strip()

    remote = tmp_path / "remote.git"
    subprocess.run([real_git, "init", "-q", "--bare", "-b", "main", str(remote)], check=True, cwd=tmp_path)
    seed = tmp_path / "seed"
    subprocess.run([real_git, "clone", "-q", str(remote), str(seed)], check=True, capture_output=True, cwd=tmp_path)
    git(seed, "checkout", "-q", "-b", "main")
    git(seed, "commit", "-q", "--allow-empty", "-m", "initial")
    git(seed, "push", "-q", "origin", "main")
    git(seed, "checkout", "-q", "-b", "feature")
    (seed / "f.txt").write_text("feature\n")
    git(seed, "add", "f.txt")
    git(seed, "commit", "-q", "-m", "feature work")
    git(seed, "push", "-q", "origin", "feature")
    worktree = tmp_path / "wt"
    subprocess.run([real_git, "clone", "-q", "-b", "feature", str(remote), str(worktree)], check=True, capture_output=True, cwd=tmp_path)
    mover = tmp_path / "mover"
    subprocess.run([real_git, "clone", "-q", "-b", "feature", str(remote), str(mover)], check=True, capture_output=True, cwd=tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    plant(bin_dir, "gh", FAKE_GH_HEAD_OF_WORKTREE)
    plant(bin_dir, "git", FAKE_GIT_MOVING_REMOTE)

    def queued_merge(move):
        git(seed, "checkout", "-q", "main")
        git(seed, "commit", "-q", "--allow-empty", "-m", "main moved")
        git(seed, "push", "-q", "origin", "main")
        git(worktree, "fetch", "-q", "origin")
        git(worktree, "checkout", "-q", "--detach", "origin/feature")
        env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "REAL_GIT": real_git,
               "MOVE_REMOTE": str(mover) if move else "", "WORKTREE": str(worktree), "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0",
               "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@example.test",
               "GIT_COMMITTER_NAME": "veri", "GIT_COMMITTER_EMAIL": "veri@example.test"}
        return subprocess.run(["/bin/sh", str(SCRIPTS / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(worktree), "feature", "-"],
                              cwd=worktree, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, timeout=30)

    queued_merge(move=False)
    pushed = git(remote, "rev-parse", "refs/heads/feature") == git(worktree, "rev-parse", "HEAD")

    git(mover, "fetch", "-q", "origin")
    git(mover, "reset", "-q", "--hard", "origin/feature")
    before = git(remote, "rev-parse", "refs/heads/feature")
    refused = queued_merge(move=True)
    raced = git(remote, "rev-parse", "refs/heads/feature")

    assert (pushed, refused.returncode, raced == git(mover, "rev-parse", "HEAD"), raced != before) == (True, 1, True, True)


FAKE_GH_WITH_BODY = """#!/bin/sh
echo "gh $*" >> "$CALL_LOG"
marker="$(dirname "$0")/.merge-landed"
for a in "$@"; do
  case "$a" in merge|*/merge) : > "$marker" ;; esac
done
head=$("$REAL_GIT" -C "$WORKTREE" rev-parse HEAD)
case "$*" in
  *"pr view"*) echo "{\\"body\\": \\"$PR_BODY\\"}" ;;
  *"check-runs?page=1"*) echo '{"check_runs": [{"name": "CI", "status": "completed", "conclusion": "success"}]}' ;;
  *check-runs*) echo '{"check_runs": []}' ;;
  *"/status"*) echo '{"statuses": []}' ;;
  *"/pulls/"*) if [ -e "$marker" ]; then echo "{\\"merged\\": true, \\"merge_commit_sha\\": \\"fedcba9\\", \\"mergeable\\": true, \\"draft\\": false, \\"head\\": {\\"sha\\": \\"$head\\"}}"; else echo "{\\"state\\": \\"open\\", \\"merged\\": false, \\"mergeable\\": true, \\"draft\\": false, \\"head\\": {\\"sha\\": \\"$head\\"}}"; fi ;;
  *) echo '[]' ;;
esac
exit 0
"""

FAKE_GIT_FAILING_LEDGER_DIFF = """#!/bin/sh
case "$*" in
  *"diff --name-only origin/main...HEAD"*) echo "fatal: bad revision 'origin/main...HEAD'" >&2; exit 128 ;;
esac
exec "$REAL_GIT" "$@"
"""


def queued_merge_on_a_non_tdd_branch(tmp_path, pr_body, failing_diff=False):
    """claude/x adds ledger .tdd/issue-200.md over a main that already holds .tdd/issue-100.md;
    returns the run and the merge PUTs gh saw."""
    real_git = shutil.which("git")
    ident = ["-c", "user.name=veri", "-c", "user.email=veri@example.test"]

    def git(repo, *args):
        done = subprocess.run([real_git, "-C", str(repo), *ident, *args], check=True, capture_output=True, text=True, cwd=tmp_path)
        return done.stdout.strip()

    remote = tmp_path / "remote.git"
    subprocess.run([real_git, "init", "-q", "--bare", "-b", "main", str(remote)], check=True, cwd=tmp_path)
    seed = tmp_path / "seed"
    subprocess.run([real_git, "clone", "-q", str(remote), str(seed)], check=True, capture_output=True, cwd=tmp_path)
    git(seed, "checkout", "-q", "-b", "main")
    (seed / ".tdd").mkdir()
    (seed / ".tdd" / "issue-100.md").write_text("old ledger\n")
    git(seed, "add", ".")
    git(seed, "commit", "-q", "-m", "initial")
    git(seed, "push", "-q", "origin", "main")
    git(seed, "checkout", "-q", "-b", "claude/x")
    (seed / ".tdd" / "issue-200.md").write_text("new ledger\n")
    (seed / "docs").mkdir()
    (seed / "docs" / "issue-300.md").write_text("a doc, not a ledger\n")
    git(seed, "add", ".")
    git(seed, "commit", "-q", "-m", "claude work")
    git(seed, "push", "-q", "origin", "claude/x")
    worktree = tmp_path / "wt"
    subprocess.run([real_git, "clone", "-q", "-b", "claude/x", str(remote), str(worktree)], check=True, capture_output=True, cwd=tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    plant(bin_dir, "gh", FAKE_GH_WITH_BODY)
    if failing_diff:
        plant(bin_dir, "git", FAKE_GIT_FAILING_LEDGER_DIFF)
    call_log = tmp_path / "calls.log"
    call_log.write_text("")
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "REAL_GIT": real_git, "WORKTREE": str(worktree),
           "CALL_LOG": str(call_log), "PR_BODY": pr_body, "VERI_MERGE_LOCK_POLL": "0.05", "VERI_POLL": "0",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_AUTHOR_NAME": "veri", "GIT_AUTHOR_EMAIL": "veri@example.test",
           "GIT_COMMITTER_NAME": "veri", "GIT_COMMITTER_EMAIL": "veri@example.test"}

    run = subprocess.run(["/bin/sh", str(SCRIPTS / "queued-merge.sh"), "https://github.com/o/r/pull/7", str(worktree), "claude/x", "-"],
                         cwd=worktree, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, timeout=30)

    put_merge = [c for c in call_log.read_text().splitlines() if c.startswith("gh api") and "-X PUT" in c and "/merge" in c]
    return run, put_merge


@pytest.mark.process("queued-merge.sh runs as a /bin/sh shim against real git, a scratch bare remote and a non-tdd branch, with gh planted on PATH")
def test_queued_merge_on_a_non_tdd_branch_demands_closes_only_for_the_ledgers_the_pr_adds_not_those_already_on_main_3490(tmp_path):
    run, put_merge = queued_merge_on_a_non_tdd_branch(tmp_path, "Closes #200")

    assert ("lacks the line" in run.stderr, len(put_merge)) == (False, 1), run.stderr


@pytest.mark.process("queued-merge.sh runs as a /bin/sh shim against real git, a scratch bare remote and a non-tdd branch, with gh planted on PATH")
def test_queued_merge_on_a_non_tdd_branch_whose_pr_body_lacks_closes_for_the_ledger_it_adds_exits_2_and_merges_nothing_3490(tmp_path):
    run, put_merge = queued_merge_on_a_non_tdd_branch(tmp_path, "Closes #999")

    assert (run.returncode, "lacks the line" in run.stderr, len(put_merge)) == (2, True, 0), run.stderr


@pytest.mark.process("queued-merge.sh runs as a /bin/sh shim against real git, a scratch bare remote and a non-tdd branch, with gh and git planted on PATH")
def test_queued_merge_on_a_non_tdd_branch_whose_ledger_diff_fails_exits_2_naming_the_diff_and_merges_nothing_3490(tmp_path):
    run, put_merge = queued_merge_on_a_non_tdd_branch(tmp_path, "Closes #999", failing_diff=True)

    assert (run.returncode, "git diff" in run.stderr, len(put_merge)) == (2, True, 0), run.stderr
