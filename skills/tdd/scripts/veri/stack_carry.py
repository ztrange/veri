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


def _carry(stack):
    """Carry <stack> with the merge lock held, never releasing it: the exit code, or _Stop."""
    fetch = git.network("fetch", "--prune", "origin", cwd=".")
    if fetch.returncode:
        raise _Stop(2, "git fetch origin failed (exit %d): %s; nothing rebased or pushed"
                    % (fetch.returncode, " ".join(fetch.stderr.split())))
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
        return _carry(stack)
    except _Stop as stop:
        print(PREFIX + "%s; the merge lock freed" % stop, file=sys.stderr)
        return stop.code
    finally:
        # Every exit frees the lock, an unexpected error's included: merge-lock.sh never takes over a dead holder's
        # lock, so a held one would block every later merge.
        stack_fix.script("merge-lock.sh", "release", "--pid", pid)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
