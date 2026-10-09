"""ledger-steps.sh's computations, run in-process."""
import re
import sys

from ledger import handed_out, ledger_steps, read_ledger_stdin

USAGE = "usage: ledger-steps.sh [current|last-done|criterion <k>]"


def refuse():
    sys.stderr.buffer.write((USAGE + "\n").encode())
    return 2


def write_lines(lines):
    sys.stdout.buffer.write("".join(line + "\n" for line in lines).encode(errors="surrogateescape"))


def answer(record):
    if record is None:
        return 3
    write_lines([record[6]])
    return 0


def current(records):
    pending = [r for r in records if r[1] == "done" and r[3] == "1"]
    open_steps = [r for r in records if handed_out(r)]
    return answer(next(iter(pending + open_steps), None))


def last_done(records):
    done = [r for r in records if r[1] == "done"]
    return answer(done[-1] if done else None)


def criterion(text, k):
    kept, in_section = [], False
    for line in text.split("\n"):
        if line.startswith("## "):
            in_section = line.startswith("## Acceptance criteria")
        if in_section:
            kept.append(line)
    found = ledger_steps("\n".join(kept))
    return answer(found[k - 1] if 1 <= k <= len(found) else None)


def main(argv):
    verb = argv[0] if argv else ""
    if verb not in ("", "current", "last-done", "criterion"):
        return refuse()
    if verb == "criterion" and not re.fullmatch("[0-9]+", argv[1] if len(argv) > 1 else ""):
        return refuse()
    text = read_ledger_stdin()
    if verb == "criterion":
        return criterion(text, int(argv[1]) % 2**64)
    records = ledger_steps(text)
    if verb == "current":
        return current(records)
    if verb == "last-done":
        return last_done(records)
    write_lines("\t".join(record) for record in records)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
