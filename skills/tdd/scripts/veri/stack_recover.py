"""stack-recover.sh's logic, run in-process: once a GitHub outage ends, pushes each offline join's commit to its run's
branch and then the stack, so each joined draft pull request reads merged (PRD 033.3)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import entry
import git
import run_dir
import stack_branch
import stack_fix

USAGE = "usage: stack-recover.sh"
# The trailer an offline join leaves on the stack commit it made: the run's pull request url and its branch.
TRAILER = re.compile(r"(https://\S+/pull/\d+) (\S+)")
# A push refused because origin's ref is not what the lease expected.
LEASE = re.compile(r"stale info|\[rejected\]")


def _refuse(line):
    """Say <line> on stderr, behind this script's prefix: no answer (exit 2)."""
    return entry.refuse(line, prefix="stack-recover: ")


def _rev(ref):
    """The commit <ref> names, or None when it names none."""
    try:
        return git.out("rev-parse", "--verify", "--quiet", ref, cwd=".")
    except git.GitFailed:
        return None


def _ancestor(older, newer):
    """Whether commit <older> is <newer> or one of its ancestors."""
    return git.ok("merge-base", "--is-ancestor", older, newer, cwd=".")


class _Garbled(Exception):
    """A commit's Veri-Joined trailer is not `<pull request url> <branch>`; the message names the commit."""


def _joins(stack):
    """The offline joins of origin/<stack>..<stack>, oldest first: (commit, pull request url, branch) for each commit
    carrying a Veri-Joined trailer; a commit without one is a stack commit of its own and skipped. _Garbled naming the
    first commit whose trailer is anything else; git.GitFailed when git cannot read the range."""
    joins = []
    for sha in git.out("log", "--reverse", "--format=%H", "origin/%s..%s" % (stack, stack), cwd=".").split():
        said = git.out("show", "-s", "--format=%(trailers:key=Veri-Joined,valueonly,unfold)", sha, cwd=".")
        lines = [line.strip() for line in said.splitlines() if line.strip()]
        if not lines:
            continue
        found = TRAILER.fullmatch(lines[0]) if len(lines) == 1 else None
        if not found:
            raise _Garbled("the commit %s carries a Veri-Joined trailer that is not '<pull request url> <branch>': %r"
                           % (sha, " | ".join(lines)[:200]))
        joins.append((sha, found[1], found[2]))
    return joins


def _held(stack):
    """The recovery of <stack> with the merge lock held, never releasing it: an exit code."""
    fetch = git.network("fetch", "--prune", "origin", cwd=".")
    if fetch.returncode:
        return _refuse("git fetch origin failed (exit %d): %s; nothing pushed" % (
            fetch.returncode, " ".join(fetch.stderr.split())))
    local, fetched = _rev("refs/heads/" + stack), _rev("refs/remotes/origin/" + stack)
    if local is None or (fetched and _ancestor(local, fetched)):
        print("stack-recover: the local %s is absent, at origin/%s or behind it: nothing joined offline, nothing to"
              " push" % (stack, stack), file=sys.stderr)
        return 3
    if fetched is None:
        print("stack-recover: origin/%s is gone after the fetch, while the local %s is at %s: the stack moved on GitHub,"
              " so what to push is the human's call; nothing pushed" % (stack, stack, local), file=sys.stderr)
        return 1
    if not _ancestor(fetched, local):
        print("stack-recover: origin/%s at %s is not an ancestor of the local %s at %s: the stack moved on GitHub, and"
              " rebasing it is the human's call; nothing pushed" % (stack, fetched, stack, local), file=sys.stderr)
        return 1
    try:
        joins = _joins(stack)
    except _Garbled as garbled:
        print("stack-recover: %s; nothing pushed" % garbled, file=sys.stderr)
        return 1
    except git.GitFailed as failed:
        return _refuse("reading origin/%s..%s failed: %s; nothing pushed" % (stack, stack, " ".join(str(failed).split())))
    # Each lease is origin's branch as fetched, read before anything is pushed.
    leases = [_rev("refs/remotes/origin/" + branch) or "" for _, _, branch in joins]
    for (sha, _, branch), lease in zip(joins, leases):
        push = git.network("push", "--force-with-lease=%s:%s" % (branch, lease), "origin",
                           "%s:refs/heads/%s" % (sha, branch), cwd=".")
        if push.returncode and LEASE.search(push.stderr or ""):
            print("stack-recover: the leased push of %s to %s was refused: origin's %s is not %s as fetched (%s); the"
                  " stack not pushed" % (sha, branch, branch, lease or "absent", " ".join(push.stderr.split())),
                  file=sys.stderr)
            return 1
        if push.returncode:
            return _refuse("the push of %s to %s failed (exit %d): %s; the stack not pushed" % (
                sha, branch, push.returncode, " ".join((push.stderr or "").split())))
    # A compare-and-swap, never --force: the lease is origin's stack as fetched, and the local stack descends from it.
    push = git.network("push", "--force-with-lease=%s:%s" % (stack, fetched), "origin",
                       "%s:refs/heads/%s" % (local, stack), cwd=".")
    if push.returncode and LEASE.search(push.stderr or ""):
        print("stack-recover: the leased push of %s to %s was refused: origin's %s is not %s as fetched (%s); the joined"
              " branches are pushed" % (local, stack, stack, fetched, " ".join(push.stderr.split())), file=sys.stderr)
        return 1
    if push.returncode:
        return _refuse("the push of %s to %s failed (exit %d): %s; the joined branches are pushed" % (
            local, stack, push.returncode, " ".join((push.stderr or "").split())))
    return 3


def main(argv):
    if argv:
        return entry.refuse(usage=USAGE)
    try:
        outage = os.path.exists(os.path.join(run_dir.main_tree_from_files(), ".tdd", "github-outage"))
    except OSError as error:
        return _refuse("the main working tree cannot be read (%s), so whether GitHub is out is not known" % error)
    if outage:
        return _refuse(".tdd/github-outage exists, so recovery waits for the GitHub outage to end; nothing read, locked"
                       " or pushed")
    try:
        stack = stack_branch.named(".")
    except stack_branch.Refused as refused:
        return _refuse("stack-branch.sh exits 2: %s" % refused)
    if stack is None:
        print("stack-recover: stack-branch.sh exits 3: the repository's CLAUDE.md names no stack branch, so nothing was"
              " joined offline", file=sys.stderr)
        return 3
    pid = str(os.getpid())
    code, _ = stack_fix.script("merge-lock.sh", "take", "--pid", pid)
    if code:
        return _refuse("merge-lock.sh take exits %d: the merge lock not taken; nothing fetched or pushed" % code)
    try:
        return _held(stack)
    finally:
        # Every way out frees the lock, an interrupt among them: merge-lock.sh never takes over a dead holder's lock.
        stack_fix.script("merge-lock.sh", "release", "--pid", pid)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
