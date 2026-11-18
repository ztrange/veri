"""stack-carry.sh's logic, run in-process: carries the stack onto the new default branch after a slice landed (PRD 034.4b)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import entry
import git
import stack_branch
import stack_fix

USAGE = "usage: stack-carry.sh <old-cut>"
PREFIX = "stack-carry: "


class _Stop(Exception):
    """The carry-over ends with <code>, <line> said on stderr."""

    def __init__(self, code, line):
        super().__init__(line)
        self.code = code


def _git(*args, cwd="."):
    """`git <args>` in <cwd>, text captured: its CompletedProcess."""
    return git.git(*args, cwd=cwd, capture_output=True, text=True)


def _unanswered(what, run):
    """_Stop(2) saying <what> got no answer from git, with <run>'s exit and stderr."""
    return _Stop(2, "%s got no answer from git (exit %d): %s; nothing rebased or pushed"
                 % (what, run.returncode, " ".join((run.stderr or "").split())[:300]))


def _rev(name, what):
    """The commit <name> (said as <what>) resolves to; _Stop(2) when it resolves to none, or git gives no answer."""
    run = _git("rev-parse", "--verify", "--quiet", "--end-of-options", name + "^{commit}")
    if run.returncode == 1:
        raise _Stop(2, "%s does not resolve to a commit; nothing rebased or pushed" % what)
    if run.returncode or not run.stdout.strip():
        raise _unanswered("reading " + what, run)
    return run.stdout.strip()


def _ancestor(older, newer):
    """Whether <older> is an ancestor of <newer>; _Stop(2) when git gives no answer, never read as "no"."""
    run = _git("merge-base", "--is-ancestor", older, newer)
    if run.returncode not in (0, 1):
        raise _unanswered("git merge-base --is-ancestor %s %s" % (older, newer), run)
    return run.returncode == 0


def _carry(stack, name):
    """Carry <stack> with the merge lock held, never releasing it: the exit code, or _Stop."""
    fetch = git.network("fetch", "--prune", "origin", cwd=".")
    if fetch.returncode:
        raise _Stop(2, "git fetch origin failed (exit %d): %s; nothing rebased or pushed"
                    % (fetch.returncode, " ".join(fetch.stderr.split())))
    tip = _rev("refs/remotes/origin/" + stack, "origin/" + stack)
    cut = _rev(name, name)
    if not _ancestor(cut, tip):
        raise _Stop(2, "the old cut %s is not an ancestor of origin/%s at %s; nothing rebased or pushed" % (cut, stack, tip))
    return 0


def main(argv):
    if len(argv) != 1 or argv[0].startswith("-"):
        return entry.refuse(usage=USAGE)
    try:
        stack = stack_branch.named(".")
    except stack_branch.Refused as refused:
        return entry.refuse("stack-branch.sh exits 2: %s" % refused, prefix=PREFIX)
    if stack is None:
        return entry.refuse("stack-branch.sh exits 3: the repository's CLAUDE.md names no stack branch", prefix=PREFIX)
    pid = str(os.getpid())
    code, _ = stack_fix.script("merge-lock.sh", "take", "--pid", pid)
    if code:
        return entry.refuse("merge-lock.sh take exits %d: the merge lock not taken; nothing fetched or pushed" % code,
                            prefix=PREFIX)
    try:
        return _carry(stack, argv[0])
    except _Stop as stop:
        print(PREFIX + "%s; the merge lock freed" % stop, file=sys.stderr)
        return stop.code
    finally:
        # Every exit frees the lock, an unexpected error's included: merge-lock.sh never takes over a dead holder's
        # lock, so a held one would block every later merge.
        stack_fix.script("merge-lock.sh", "release", "--pid", pid)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
