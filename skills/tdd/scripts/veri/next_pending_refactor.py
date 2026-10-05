"""next-pending-refactor.sh's computation, run in-process."""
import sys

from ledger import ledger_steps


def refactor_pending(record):
    return record[1] == "done" and record[3] == "1"


def main(argv):
    for record in ledger_steps(sys.stdin.buffer.read().replace(b"\0", b"").decode(errors="surrogateescape")):
        if refactor_pending(record):
            sys.stdout.buffer.write((record[6] + "\n").encode(errors="surrogateescape"))
            return 0
    return 3

