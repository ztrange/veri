"""criterion-finished.sh's computation, run in-process."""
import sys

import ledger

USAGE = "usage: criterion-finished.sh <k> < .tdd/issue-<n>.md"


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    if sys.stdin is None:
        return 3
    text = sys.stdin.buffer.read().replace(b"\0", b"").decode("utf-8", "surrogateescape")
    served = False
    for _, state, _, pending, _, criterion, _ in ledger.ledger_steps(text):
        if criterion != argv[0]:
            continue
        served = True
        if state != "done" or pending != "0":
            return 3
    return 0 if served else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
