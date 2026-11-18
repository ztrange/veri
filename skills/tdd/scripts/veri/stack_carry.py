"""stack-carry.sh's logic, run in-process: carries the stack onto the new default branch after a slice landed (PRD 034.4b)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry
import stack_branch

USAGE = "usage: stack-carry.sh <old-cut>"
PREFIX = "stack-carry: "


def main(argv):
    if len(argv) != 1 or argv[0].startswith("-"):
        return entry.refuse(usage=USAGE)
    try:
        stack = stack_branch.named(".")
    except stack_branch.Refused as refused:
        return entry.refuse("stack-branch.sh exits 2: %s" % refused, prefix=PREFIX)
    if stack is None:
        return entry.refuse("stack-branch.sh exits 3: the repository's CLAUDE.md names no stack branch", prefix=PREFIX)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
