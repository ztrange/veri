"""harvest-usage.sh's computations, run in-process."""
import sys


def main(argv):
    if not argv:
        print("usage: harvest-usage.sh <leaf-name>", file=sys.stderr)
        return 2
    return 0
