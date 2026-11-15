"""criterion-finished.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
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
    for step in steps:
        if step.criterion != argv[0]:
            continue
        served = True
        if step.state != "done" or step.pending != "0":
            return 3
    return 0 if served else 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
