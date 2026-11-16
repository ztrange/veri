"""queued-merge.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import entry
import event
import paths
import run_dir
import tunables
from github import gh_api, gh_probe

USAGE = "usage: queued-merge.sh <pr-url> <worktree> <branch> <tag-message|->"
FETCH_ATTEMPTS = 5
REFRESH_RETRIES = 10
SCRIPTS = paths.resolved_scripts_of(__file__)

RELEASE, LEAVE = "release", "leave"

RELEASE_FILES = ("merge-lock.sh", "lib/shim-python.sh", "lib/venv-python.sh", "veri/merge_lock.py",
                 "veri/tunables.py", "veri/entry.py", "veri/pycache_prefix.py")


def _start(name, *args, scripts=SCRIPTS, cwd=None, capture=False):
    try:
        return subprocess.run([os.path.join(scripts, name), *args], cwd=cwd, capture_output=capture, text=True)
    except OSError:
        return subprocess.CompletedProcess(name, 2, "", "")


def _script(name, *args, scripts=SCRIPTS, cwd=None):
    return _start(name, *args, scripts=scripts, cwd=cwd).returncode


def _gate(pid, *cmd, keep=False):
    return _script("merge-lock.sh", "gate", *(["--keep"] if keep else []), "--pid", pid, "--", *cmd)


def _gate_output(pid, *cmd):
    run = _start("merge-lock.sh", "gate", "--keep", "--pid", pid, "--", *cmd, capture=True)
    sys.stdout.write(run.stdout or "")
    sys.stderr.write(run.stderr or "")
    return run.returncode, (run.stdout or "") + (run.stderr or "")


def _rebase(pid, worktree, git_args):
    code, output = _gate_output(pid, "git", "-C", worktree, *git_args)
    for _ in range(REFRESH_RETRIES):
        if not code or "would be overwritten by merge" not in output or _git(worktree, "status", "--porcelain").stdout.strip():
            break
        _gate(pid, "git", "-C", worktree, "update-index", "--really-refresh", keep=True)
        event.mark(worktree, {}, "rebase-refresh-retry")
        code, output = _gate_output(pid, "git", "-C", worktree, "rebase", "--continue")
    return code


def _git(worktree, *args):
    return subprocess.run(["git", "-C", worktree, *args], capture_output=True, text=True)


def _repo(pr):
    return pr.removeprefix("https://github.com/").rsplit("/pull/", 1)[0]


def _number(pr):
    return pr.rsplit("/pull/", 1)[-1]


def _say(message):
    print("queued-merge: %s" % message, file=sys.stderr)


def _release(pid, scripts=SCRIPTS, cwd=None):
    code = _script("merge-lock.sh", "release", "--pid", pid, scripts=scripts, cwd=cwd)
    if code:
        _say("releasing the merge lock failed (exit %d)" % code)
    return code


def _rev(worktree, ref):
    run = _git(worktree, "rev-parse", "--verify", ref)
    return run.stdout.strip() if run.returncode == 0 else ""


def _synced(worktree, lease):
    if not _git(worktree, "merge-base", "--is-ancestor", lease, "HEAD").returncode:
        return True
    return (not _git(worktree, "merge-base", "--is-ancestor", "HEAD", lease).returncode
            and not _git(worktree, "status", "--porcelain").stdout.strip()
            and not _git(worktree, "merge", "--ff-only", lease).returncode)


def _pull(repo, pr):
    """GitHub's pull record for <pr> as a dict; None when it cannot be read."""
    run = gh_api("repos/%s/pulls/%s" % (repo, _number(pr)))
    try:
        pull = json.loads(run.stdout) if run.returncode == 0 else None
    except ValueError:
        return None
    return pull if isinstance(pull, dict) else None


def _merged(repo, pr):
    """GitHub's pull record when it answers merged: true; None when it answers anything else."""
    pull = _pull(repo, pr)
    return pull if pull and pull.get("merged") is True else None


def _closed(repo, pr):
    pull = _pull(repo, pr)
    return bool(pull) and pull.get("state") == "closed" and pull.get("merged") is False


def _merge_commit(worktree, pull, pr):
    """The merge commit GitHub reports for <pr>, fetched into <worktree>; "" when either step fails."""
    sha = pull.get("merge_commit_sha") or ""
    if not isinstance(sha, str) or not sha:
        _say("GitHub reports no merge commit for %s" % pr)
        return ""
    for attempt in range(FETCH_ATTEMPTS):
        if attempt:
            time.sleep(float(tunables.get("VERI_FETCH_RETRY_SLEEP", unless_empty=True)))
        fetch = _git(worktree, "fetch", "origin")
        if not fetch.returncode and not _git(worktree, "cat-file", "-e", sha + "^{commit}").returncode:
            return sha
    if fetch.returncode:
        _say("git fetch origin failed (exit %d): %s" % (fetch.returncode, fetch.stderr.strip()))
        return ""
    _say("merge commit %s of %s is not in the clone after a fetch" % (sha, pr))
    return ""


def _tag(worktree, message, pull, pr):
    """Tag the PR's own merge commit, never a re-read origin/main: a concurrent merge may already sit on it."""
    target = _merge_commit(worktree, pull, pr)
    if not target:
        return False
    tags = _git(worktree, "tag", "--sort=-v:refname").stdout.split()
    if not tags:
        _say("no vN.M tag to bump from; no tag cut")
        return False
    major, minor = tags[0].removeprefix("v").split(".")
    name = "v%s.%d" % (major, int(minor) + 1)
    for args in (("tag", "-a", name, "-m", message, target), ("push", "origin", name)):
        if _git(worktree, *args).returncode:
            _say("git %s failed; tag %s not published" % (args[0], name))
            return False
    return name


def _step(failed, what, cwd, *args, label=None):
    run = _git(cwd, *args)
    if run.returncode:
        _say("%s failed (exit %d): %s" % (what, run.returncode, run.stderr.strip()))
        failed.append(label or what)


def _cleanup(pid, pr, pull, worktree, branch, message):
    """Tag, delete the branch, remove the worktree, release the lock: every step runs, each failure is named."""
    failed = []
    clone = os.path.dirname(_git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    spare = tempfile.mkdtemp(prefix="queued-merge-scripts-")
    scripts = os.path.join(spare, "scripts")
    for name in RELEASE_FILES:
        os.makedirs(os.path.dirname(os.path.join(scripts, name)), exist_ok=True)
        shutil.copy2(os.path.join(SCRIPTS, name), os.path.join(scripts, name))
    name = ""
    if message != "-":
        name = _tag(worktree, message, pull, pr)
        if not name:
            failed.append("tag")
    if message == "-" or name:
        issue = re.match(r"tdd/(\d+)-", branch)
        if issue:
            event.mark(worktree, {"issue": issue.group(1)}, "merged",
                       ["pr=" + pr, "tag=" + name, "message=" + (message if name else "")])
    _step(failed, "branch delete", worktree, "push", "origin", "--delete", branch)
    _step(failed, "worktree remove", worktree, "worktree", "remove", worktree)
    _step(failed, "local branch delete", clone, "branch", "-D", branch)
    if _release(pid, scripts, clone):
        failed.append("release")
    shutil.rmtree(spare)
    current = _git(clone, "branch", "--show-current").stdout.strip()
    if current not in ("", "main"):
        _say("fast-forward of main to origin/main not done: the main clone is on %s" % current)
        failed.append("fast-forward")
    else:
        _step(failed, "fast-forward of main to origin/main", clone, "pull", "--ff-only", ".", "origin/main",
              label="fast-forward")
    if failed:
        _say("merged, but cleanup failed: %s" % ", ".join(failed))
        return 2
    return 0


def _refused(message, code=2):
    """A refusal that frees the lock: main releases it once, after the message."""
    _say(message)
    return code, RELEASE


def _before_rebase(repo, pr, worktree, branch):
    """The checks made before the rebase: (lease, None) to go, ("", (message, code)) to refuse. No lock logic."""
    if _merged(repo, pr) is not None:
        return "", ("%s is already merged; nothing rebased or pushed" % pr, 2)
    if _closed(repo, pr):
        return "", ("%s is closed and unmerged; nothing rebased or pushed" % pr, 2)
    pull = _pull(repo, pr)
    head_sha = ((pull or {}).get("head") or {}).get("sha")
    if not isinstance(head_sha, str) or not head_sha:
        return "", ("could not read the head of %s from GitHub; nothing rebased or pushed" % pr, 2)
    if not _git(worktree, "merge-base", "--is-ancestor", head_sha, "origin/main").returncode:
        return "", ("the head %s of %s is already on origin/main; nothing rebased or pushed" % (head_sha, pr), 2)
    lease = _rev(worktree, "refs/remotes/origin/%s" % branch)
    if not lease:
        return "", ("origin/%s does not resolve; no lease to pin" % branch, 2)
    if not _synced(worktree, lease):
        return "", ("origin/%s has commits the worktree lacks; nothing pushed" % branch, 2)
    return lease, None


def _before_merge(pid, pr, worktree, branch, before, head):
    """The checks between the pushed head's CI and the merge call: None to go, (message, code) to refuse."""
    if tunables.read("VERI_CI_ON_PR") == "0" and before != head:
        found = subprocess.run([os.path.join(SCRIPTS, "detect-test-command.sh"), "--tier", "all"],
                               cwd=worktree, capture_output=True, text=True)
        full = found.stdout.strip()
        if found.returncode or not full:
            return ("no full test command for the rebased tree (%s); not merged" % (
                "detect-test-command.sh exited %d" % found.returncode if found.returncode
                else "detect-test-command.sh printed nothing"), 2)
        if _gate(pid, "sh", "-c", full, keep=True):
            return "the full test command (%s) is red on the rebased tree; not merged" % full, 1
    own = re.match(r"tdd/(\d+)-", branch)
    if own:
        paths = glob.glob(run_dir.ledger(worktree, own.group(1)))
    else:
        changed = _git(worktree, "diff", "--name-only", "origin/main...HEAD", "--", ".tdd/issue-*.md")
        if changed.returncode:
            return ("git diff --name-only origin/main...HEAD failed (exit %d): %s; not merged" % (
                changed.returncode, changed.stderr.strip()), 2)
        paths = changed.stdout.split()
    for path in paths:
        number = re.match(r"issue-(\d+)\.md", os.path.basename(path))
        if not number:
            continue
        shown = gh_probe("pr", "view", pr, "--json", "body")
        if shown.returncode:
            return "could not read the PR body of %s; not merged" % pr, 2
        body = json.loads(shown.stdout)["body"]
        if not re.search(r"Closes #%s\b" % number.group(1), body):
            return "the PR body of %s lacks the line 'Closes #%s'; not merged" % (pr, number.group(1)), 2
    return None


def _to_merge(pid, repo, pr, worktree, branch):
    """Fetch, rebase, push, wait for CI and check before the merge: (head, None) to merge, ("", (code, outcome)) to stop."""
    code = _gate(pid, "git", "-C", worktree, "fetch", "origin")
    if code:
        return "", (code, LEAVE)
    lease, refusal = _before_rebase(repo, pr, worktree, branch)
    if refusal:
        return "", _refused(*refusal)
    before = _rev(worktree, "HEAD")
    code = _rebase(pid, worktree, ("rebase", "origin/main"))
    if code:
        return "", (code, LEAVE)
    code = _gate(pid, "git", "-C", worktree, "push", "--force-with-lease=%s:%s" % (branch, lease),
                 "origin", "HEAD:refs/heads/%s" % branch, keep=True)
    if code:
        return "", (code, LEAVE)
    head = _rev(worktree, "HEAD")
    if not head:
        return "", _refused("the pushed head does not resolve")
    code = 3
    while code == 3:
        code = _gate(pid, os.path.join(SCRIPTS, "wait-ci.sh"), pr, "540", "", head)
    if code:
        return "", (code, LEAVE)
    refusal = _before_merge(pid, pr, worktree, branch, before, head)
    if refusal:
        return "", _refused(*refusal)
    return head, None


def _locked(pid, repo, pr, worktree, branch, message):
    """Everything after the lock is taken: returns (exit code, RELEASE | LEAVE), never releasing itself.

    main releases the lock exactly once when the outcome is RELEASE. LEAVE means the lock needs
    nothing more from main, for one of two reasons:

    Kept on purpose, held for the next merge or the operator to recover:
      - the rebase stops (a conflict, a dirty "would be overwritten" stop, a phantom stop past the
        retry bound): exits git's code, nothing pushed;
      - the push under the pinned lease is refused: exits git's code.

    Already settled by the callee:
      - the first fetch, the wait-ci gate: a gate without --keep releases the lock itself on failure;
      - _cleanup: releases the lock after the tag, branch delete and worktree removal.

    An exception escaping before the merge call is exit 2 with RELEASE, named in entry.refusal's form;
    after the call, _cleanup releases from a copy of the scripts, so no blanket release is safe there.
    """
    try:
        head, stop = _to_merge(pid, repo, pr, worktree, branch)
    except Exception as error:
        sys.stderr.write(entry.refusal(main, error))
        return 2, RELEASE
    if stop:
        return stop
    gh_merge = ("gh", "pr", "merge", pr, "--rebase", "--match-head-commit", head)
    rest_merge = ("gh", "api", "-X", "PUT", "repos/%s/pulls/%s/merge" % (repo, _number(pr)),
                  "-f", "merge_method=rebase", "-f", "sha=%s" % head)
    driver = tunables.get("VERI_GH_DRIVER")
    # The merge call keeps the lock even when it errors: an errored call may have landed, and the
    # settle window below re-reads the PR while still holding it, so a landed merge reaches _cleanup
    # with the lock its release expects, and no other merge takes the lock mid-window.
    if driver == "graphql":
        code = _gate(pid, *gh_merge, keep=True)
    elif driver == "auto":
        code = _gate(pid, *gh_merge, keep=True)
        if code:
            code = _gate(pid, *rest_merge, keep=True)
    else:
        code = _gate(pid, *rest_merge, keep=True)
    pull, answered = None, False
    for attempt in range(int(tunables.get("VERI_MERGE_SETTLE_READS", unless_empty=True))):
        if code or attempt:
            time.sleep(float(tunables.get("VERI_MERGE_SETTLE_SLEEP", unless_empty=True)))
        read = _pull(repo, pr)
        answered = answered or read is not None
        if read and read.get("merged") is True:
            pull = read
            break
    if pull is None and not answered:
        call = "exited %d" % code if code else "succeeded"
        return _refused("the merge call %s and the state of %s could not be read; nothing tagged or cleaned up" % (call, pr))
    if pull is None and code:
        return _refused("%s did not read merged after the merge call exited %d; nothing tagged or cleaned up" % (pr, code), code)
    if pull is None:
        return _refused("%s is not reported merged; no tag, branch delete or worktree removal" % pr, 1)
    return _cleanup(pid, pr, pull, worktree, branch, message), LEAVE


def main(argv):
    if len(argv) != 4:
        print(USAGE, file=sys.stderr)
        return 2
    pr, worktree, branch, message = argv
    if not re.fullmatch(r"https://github\.com/[^/]+/[^/]+/pull/\d+", pr):
        print(USAGE, file=sys.stderr)
        return 2
    driver = tunables.get("VERI_GH_DRIVER")
    if driver not in ("auto", "rest", "graphql"):
        print("VERI_GH_DRIVER is '%s': expected auto, rest or graphql" % driver, file=sys.stderr)
        return 2
    repo = _repo(pr)
    pid = str(os.getpid())
    code = _script("merge-lock.sh", "take", "--pid", pid)
    if code:
        _say("taking the merge lock failed (exit %d)" % code)
        return code
    code, outcome = _locked(pid, repo, pr, worktree, branch, message)
    if outcome is RELEASE:
        _release(pid)
    return code


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
