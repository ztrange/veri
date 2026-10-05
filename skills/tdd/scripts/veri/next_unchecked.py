"""next-unchecked.sh's computation, run in-process."""
import sys

from ledger import ledger_steps


def handed_out(record):
    return record[1] == "open" and record[2] in ("step", "diff-checked")


def main(argv):
    text = sys.stdin.buffer.read().decode()
    for record in ledger_steps(text):
        if handed_out(record):
            sys.stdout.buffer.write((record[6] + "\n").encode())
            return 0
    return 3
