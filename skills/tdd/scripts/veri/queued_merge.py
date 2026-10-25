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
    """True only when GitHub answers merged: true; False when it answers anything else."""
    run = gh_api("repos/%s/pulls/%s" % (repo, pr.rsplit("/pull/", 1)[-1]))
    try:
        return run.returncode == 0 and json.loads(run.stdout).get("merged") is True
    except (ValueError, AttributeError):
        return False


def _tag(worktree, message):
    tags = _git(worktree, "tag", "--sort=-v:refname").stdout.split()
    if not tags:
        _say("no vN.M tag to bump from; no tag cut")
        return False
    major, minor = tags[0].removeprefix("v").split(".")
    name = "v%s.%d" % (major, int(minor) + 1)
    for args in (("tag", "-a", name, "-m", message, "origin/main"), ("push", "origin", name)):
        if _git(worktree, *args).returncode:
            _say("git %s failed; tag %s not published" % (args[0], name))
            return False
    return True


def _cleanup(pid, worktree, branch, message):
    """Tag, delete the branch, remove the worktree, release the lock: every step runs, each failure is named."""
    failed = []
    if message != "-" and not _tag(worktree, message):
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
    if not _merged(repo, pr):
        _say("%s is not reported merged; no tag, branch delete or worktree removal" % pr)
        _release(pid)
        return 1
    return _cleanup(pid, worktree, branch, message)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
