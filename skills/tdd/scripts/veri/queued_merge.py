"""queued-merge.sh's logic, run in-process."""
import json
import os
import subprocess
import sys

try:
    from github import gh_api
except ImportError:
    from .github import gh_api

USAGE = "usage: queued-merge.sh <pr> <worktree> <branch> <tag-message|->"
SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _script(name, *args):
    return subprocess.run([os.path.join(SCRIPTS, name), *args]).returncode


def _gate(pid, *cmd, keep=False):
    return _script("merge-lock.sh", "gate", *(["--keep"] if keep else []), "--pid", pid, "--", *cmd)


def _git(worktree, *args):
    return subprocess.run(["git", "-C", worktree, *args], capture_output=True, text=True)


def _repo(pr):
    return pr.removeprefix("https://github.com/").rsplit("/pull/", 1)[0]


def _say(message):
    print("queued-merge: %s" % message, file=sys.stderr)


def _release(pid):
    code = _script("merge-lock.sh", "release", "--pid", pid)
    if code:
        _say("releasing the merge lock failed (exit %d)" % code)
    return code


def _rev(worktree, ref):
    run = _git(worktree, "rev-parse", "--verify", ref)
    return run.stdout.strip() if run.returncode == 0 else ""


def _merged(repo, pr):
    """GitHub's pull record when it answers merged: true; None when it answers anything else."""
    run = gh_api("repos/%s/pulls/%s" % (repo, pr.rsplit("/pull/", 1)[-1]))
    try:
        pull = json.loads(run.stdout) if run.returncode == 0 else None
    except ValueError:
        return None
    return pull if isinstance(pull, dict) and pull.get("merged") is True else None


def _merge_commit(worktree, pull, pr):
    """The merge commit GitHub reports for <pr>, fetched into <worktree>; "" when either step fails."""
    sha = pull.get("merge_commit_sha") or ""
    if not isinstance(sha, str) or not sha:
        _say("GitHub reports no merge commit for %s" % pr)
        return ""
    if _git(worktree, "fetch", "origin").returncode or _git(worktree, "cat-file", "-e", sha + "^{commit}").returncode:
        _say("merge commit %s of %s is not in the clone after a fetch" % (sha, pr))
        return ""
    return sha


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
    return True


def _cleanup(pid, pr, pull, worktree, branch, message):
    """Tag, delete the branch, remove the worktree, release the lock: every step runs, each failure is named."""
    failed = []
    if message != "-" and not _tag(worktree, message, pull, pr):
        failed.append("tag")
    for what, args in (("branch delete", ("push", "origin", "--delete", branch)),
                       ("worktree remove", ("worktree", "remove", worktree))):
        run = _git(worktree, *args)
        if run.returncode:
            _say("%s failed (exit %d): %s" % (what, run.returncode, run.stderr.strip()))
            failed.append(what)
    if _release(pid):
        failed.append("release")
    if failed:
        _say("merged, but cleanup failed: %s" % ", ".join(failed))
        return 2
    return 0


def main(argv):
    if len(argv) != 4:
        print(USAGE, file=sys.stderr)
        return 2
    pr, worktree, branch, message = argv
    repo = _repo(pr)
    pid = str(os.getpid())
    code = _script("merge-lock.sh", "take", "--pid", pid)
    if code:
        _say("taking the merge lock failed (exit %d)" % code)
        return code
    code = _gate(pid, "git", "-C", worktree, "fetch", "origin")
    if code:
        return code
    lease = _rev(worktree, "refs/remotes/origin/%s" % branch)
    if not lease:
        _say("origin/%s does not resolve; no lease to pin" % branch)
        _release(pid)
        return 2
    if _git(worktree, "merge-base", "--is-ancestor", lease, "HEAD").returncode:
        _say("origin/%s has commits the worktree lacks; nothing pushed" % branch)
        _release(pid)
        return 2
    for git_args in (("rebase", "origin/main"),
                     ("push", "--force-with-lease=%s:%s" % (branch, lease), "origin", branch)):
        code = _gate(pid, "git", "-C", worktree, *git_args, keep=True)
        if code:
            return code
    head = _rev(worktree, "HEAD")
    if not head:
        _say("the pushed head does not resolve")
        _release(pid)
        return 2
    code = 3
    while code == 3:
        code = _gate(pid, os.path.join(SCRIPTS, "wait-ci.sh"), pr, "540", "", head)
    if code:
        return code
    code = _gate(pid, "gh", "pr", "merge", pr, "--rebase", "--match-head-commit", head)
    if code:
        return code
    pull = _merged(repo, pr)
    if pull is None:
        _say("%s is not reported merged; no tag, branch delete or worktree removal" % pr)
        _release(pid)
        return 1
    return _cleanup(pid, pr, pull, worktree, branch, message)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
