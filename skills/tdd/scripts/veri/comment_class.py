"""comment-class.sh's classification, run in-process."""
import sys

USAGE = "usage: comment-class.sh [--sweepable] <file>…"


def main(argv):
    print(USAGE, file=sys.stderr)
    return 2
