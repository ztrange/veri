"""ledger-steps.sh's computations, run in-process."""
import sys

from veri.ledger import ledger_steps

USAGE = "usage: ledger-steps.sh [current|last-done|criterion <k>]"


def refuse():
    sys.stderr.buffer.write((USAGE + "\n").encode())
    return 2


def write_lines(lines):
    sys.stdout.buffer.write("".join(line + "\n" for line in lines).encode())


def main(argv):
    verb = argv[0] if argv else ""
    if verb not in ("", "current"):
        return refuse()
    records = ledger_steps(sys.stdin.buffer.read().decode())
    if verb == "current":
        return 3
    write_lines("\t".join(record) for record in records)
    return 0
