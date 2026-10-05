"""next-pending-refactor.sh's computation, run in-process."""
import sys

from ledger import ledger_steps


def refactor_pending(record):
    return record[1] == "done" and record[3] == "1"


def main(argv):
    for record in ledger_steps(sys.stdin.buffer.read().decode()):
        if refactor_pending(record):
            sys.stdout.buffer.write((record[6] + "\n").encode())
            return 0
    return 3

