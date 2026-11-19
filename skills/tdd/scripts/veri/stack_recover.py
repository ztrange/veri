"""stack-recover.sh's logic, run in-process: once a GitHub outage ends, pushes each offline join's commit to its run's
branch and then the stack, so each joined draft pull request reads merged (PRD 033.3)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import entry
import run_dir
import stack_branch

USAGE = "usage: stack-recover.sh"


def _refuse(line):
    """Say <line> on stderr, behind this script's prefix: no answer (exit 2)."""
    return entry.refuse(line, prefix="stack-recover: ")


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
    return 3


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
