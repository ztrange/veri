"""tick-ledger.sh's tick, run in-process."""
import sys

import ledger

USAGE = "usage: tick-ledger.sh [--refactor-pending] <ledger-file> <matcher>"


def main(argv):
    if argv[:1] == ["--refactor-pending"]:
        argv = argv[1:]
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    with open(argv[0]) as file:
        ticked, _ = ledger.ledger_tick(file.read(), argv[1])
    if not ticked:
        return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
