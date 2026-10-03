"""tier-usual.sh's median, run in-process."""
import sys


def main(argv):
    if not argv:
        print("usage: tier-usual.sh <tier>", file=sys.stderr)
        return 2
    return 0

