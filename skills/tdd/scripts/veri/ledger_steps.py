"""ledger-steps.sh's computations, run in-process."""
import sys

from veri.ledger import ledger_steps

USAGE = "usage: ledger-steps.sh [current|last-done|criterion <k>]"


def refuse():
    sys.stderr.buffer.write((USAGE + "\n").encode())
    return 2


def write_lines(lines):
    sys.stdout.buffer.write("".join(line + "\n" for line in lines).encode())


def answer(record):
    if record is None:
        return 3
    write_lines([record[6]])
    return 0


def current(records):
    pending = [r for r in records if r[1] == "done" and r[3] == "1"]
    open_steps = [r for r in records if r[1] == "open" and r[2] in ("step", "diff-checked")]
    return answer(next(iter(pending + open_steps), None))


def last_done(records):
    done = [r for r in records if r[1] == "done"]
    return answer(done[-1] if done else None)


def main(argv):
    verb = argv[0] if argv else ""
    if verb not in ("", "current", "last-done"):
        return refuse()
    records = ledger_steps(sys.stdin.buffer.read().decode())
    if verb == "current":
        return current(records)
    if verb == "last-done":
        return last_done(records)
    write_lines("\t".join(record) for record in records)
    return 0
