"""affected-suites.sh's computations, run in-process."""
import sys

USAGE = "usage: affected-suites.sh <base>..<head>"


def refuse(message=None):
    if message is not None:
        print(message, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


def main(argv):
    if not argv or not argv[0]:
        return refuse()
    range_ = argv[0]
    if ".." not in range_:
        return refuse("affected-suites: '%s' is not a <base>..<head> range" % range_)
