"""criterion-finished.sh's computation, run in-process."""
import sys

import ledger

USAGE = "usage: criterion-finished.sh <k> < .tdd/issue-<n>.md"


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    for _, state, *_ in ledger.ledger_steps(sys.stdin.read()):
        if state != "done":
            return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
