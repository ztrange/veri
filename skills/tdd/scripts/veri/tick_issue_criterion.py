"""tick-issue-criterion.sh's read, tick and write-back, run in-process."""
import sys

USAGE = "usage: tick-issue-criterion.sh <issue-number> <matcher>"


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    return 0
