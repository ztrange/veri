"""stack-land.sh's logic, run in-process: lands the stack's tested cut on the default branch (PRD 034.4a)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry
import stack_branch

USAGE = "usage: stack-land.sh [--now]"


def main(argv):
    if argv not in ([], ["--now"]):
        return entry.refuse(usage=USAGE)
    try:
        stack = stack_branch.named(".")
    except stack_branch.Refused as refused:
        return entry.refuse("stack-branch.sh exits 2: %s" % refused, prefix="stack-land: ")
    if stack is None:
        return entry.refuse("stack-branch.sh exits 3: the repository's CLAUDE.md names no stack branch",
                            prefix="stack-land: ")


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
