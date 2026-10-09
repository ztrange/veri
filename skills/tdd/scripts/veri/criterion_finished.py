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
    text = ledger.read_ledger_stdin()
    steps = ledger.ledger_steps(text)
    refusal = ledger.multi_tag_refusal(steps)
    if refusal:
        print("criterion-finished.sh: " + refusal, file=sys.stderr)
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
    import entry
    entry.run(main, sys.argv[1:])
