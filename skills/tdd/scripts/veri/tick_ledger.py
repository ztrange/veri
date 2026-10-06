"""tick-ledger.sh's tick, run in-process."""
import sys

import ledger

USAGE = "usage: tick-ledger.sh [--refactor-pending] <ledger-file> <matcher>"


def main(argv):
    pending = argv[:1] == ["--refactor-pending"]
    if pending:
        argv = argv[1:]
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    with open(argv[0], newline="") as file:
        ticked, new = ledger.ledger_tick(file.read().replace("\0", ""), (argv[1:] or [""])[0], pending)
    if not ticked:
        return 3
    with open(argv[0], "w") as file:
        file.write(new.rstrip("\n") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
