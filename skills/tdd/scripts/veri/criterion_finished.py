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
    steps = ledger.ledger_steps(text)
    for step in steps:
        if step[6].count(ledger.CRITERION_TAG) > 1:
            print(f"criterion-finished.sh: step '{step[6]}' carries more than one criterion tag; one step serves one criterion", file=sys.stderr)
            return 2
    served = False
    for _, state, _, pending, _, criterion, _ in steps:
        if criterion != argv[0]:
            continue
        served = True
        if state != "done" or pending != "0":
            return 3
    return 0 if served else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
