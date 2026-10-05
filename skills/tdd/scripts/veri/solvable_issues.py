"""solvable-issues.sh's selection, run in-process."""
import sys

USAGE = "usage: solvable-issues.sh [--repo owner/name]"


def main(argv):
    if argv[:1] == ["--repo"] and not "".join(argv[1:2]):
        print(USAGE, file=sys.stderr)
        return 2
