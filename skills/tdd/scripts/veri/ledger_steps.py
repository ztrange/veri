"""ledger-steps.sh's computations, run in-process."""
import re
import sys

from ledger import handed_out, ledger_steps, next_phase, read_ledger_stdin, trailing_markers

VERBS = {
    "current": "current",
    "last-done": "last-done",
    "current-or-last-done": "current-or-last-done",
    "next-phase": "next-phase",
    "criterion": "criterion <k>",
    "has-mark": "has-mark <name>",
}
USAGE = "usage: ledger-steps.sh [" + "|".join(VERBS.values()) + "]"


def refuse():
    sys.stderr.buffer.write((USAGE + "\n").encode())
    return 2


def write_lines(lines):
    sys.stdout.buffer.write("".join(line + "\n" for line in lines).encode(errors="surrogateescape"))


def say(text):
    if text is None:
        return 3
    write_lines([text])
    return 0


def answer(record):
    return say(None if record is None else record[6])


def current(records):
    pending = [r for r in records if r[1] == "done" and r[3] == "1"]
    open_steps = [r for r in records if handed_out(r)]
    return answer(next(iter(pending + open_steps), None))


def last_done(records):
    done = [r for r in records if r[1] == "done"]
    return answer(done[-1] if done else None)


def current_or_last_done(records):
    code = current(records)
    return last_done(records) if code == 3 else code


def phase_next(records):
    phases = (next_phase(r[6]) for r in records)
    return say(next((phase for phase in phases if phase), None))


def has_mark(records, name):
    mark = f"⟦{name}⟧"
    return 0 if any(mark in trailing_markers(r[6]) for r in records) else 3


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
    if verb and verb not in VERBS:
        return refuse()
    if verb == "criterion" and not re.fullmatch("[0-9]+", argv[1] if len(argv) > 1 else ""):
        return refuse()
    if verb == "has-mark" and (len(argv) < 2 or not argv[1]):
        return refuse()
    text = read_ledger_stdin()
    if verb == "criterion":
        return criterion(text, int(argv[1]) % 2**64)
    records = ledger_steps(text)
    if verb == "has-mark":
        return has_mark(records, argv[1])
    if verb == "current":
        return current(records)
    if verb == "last-done":
        return last_done(records)
    if verb == "current-or-last-done":
        return current_or_last_done(records)
    if verb == "next-phase":
        return phase_next(records)
    write_lines("\t".join(record) for record in records)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
