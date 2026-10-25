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


def _rev(worktree, ref):
    run = _git(worktree, "rev-parse", "--verify", ref)
    return run.stdout.strip() if run.returncode == 0 else ""


def _tag(worktree, message):
    tags = subprocess.run(["git", "-C", worktree, "tag", "--sort=-v:refname"], capture_output=True, text=True).stdout.split()
    major, minor = tags[0].removeprefix("v").split(".")
    name = "v%s.%d" % (major, int(minor) + 1)
    subprocess.run(["git", "-C", worktree, "tag", "-a", name, "-m", message, "origin/main"])
    subprocess.run(["git", "-C", worktree, "push", "origin", name])


def main(argv):
    if len(argv) != 4:
        print(USAGE, file=sys.stderr)
        return 2
    pr, worktree, branch, message = argv
    repo = _repo(pr)
    pid = str(os.getpid())
    _script("merge-lock.sh", "take", "--pid", pid)
    code = _gate(pid, "git", "-C", worktree, "fetch", "origin")
    if code:
        return code
    lease = _rev(worktree, "refs/remotes/origin/%s" % branch)
    if not lease:
        _say("origin/%s does not resolve; no lease to pin" % branch)
        _script("merge-lock.sh", "release", "--pid", pid)
        return 2
    for git_args in (("rebase", "origin/main"),
                     ("push", "--force-with-lease=%s:%s" % (branch, lease), "origin", branch)):
        code = _gate(pid, "git", "-C", worktree, *git_args, keep=True)
        if code:
            return code
    head = _rev(worktree, "HEAD")
    if not head:
        _say("the pushed head does not resolve")
        _script("merge-lock.sh", "release", "--pid", pid)
        return 2
    code = 3
    while code == 3:
        code = _gate(pid, os.path.join(SCRIPTS, "wait-ci.sh"), pr, "540", "", head)
    if code:
        return code
    code = _gate(pid, "gh", "pr", "merge", pr, "--rebase", "--match-head-commit", head)
    if code:
        return code
    landed = json.loads(gh_api("repos/%s/pulls/%s" % (repo, pr.rsplit("/pull/", 1)[-1])).stdout).get("merged") is not False
    _script("merge-lock.sh", "release", "--pid", pid)
    if not landed:
        return 1
    subprocess.run(["git", "-C", worktree, "push", "origin", "--delete", branch])
    subprocess.run(["git", "-C", worktree, "worktree", "remove", worktree])
    if message != "-":
        _tag(worktree, message)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
