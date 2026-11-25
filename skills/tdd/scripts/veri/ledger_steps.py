"""ledger-steps.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry
import issue_body
from ledger import REPIN_STEP, handed_out, ledger_steps, next_phase, read_ledger_stdin, trailing_markers, carries_mark

VERBS = {
    "current": "current",
    "last-done": "last-done",
    "current-or-last-done": "current-or-last-done",
    "open": "open",
    "next-phase": "next-phase",
    "criterion": "criterion <k>",
    "has-mark": "has-mark <name>",
}
USAGE = "usage: ledger-steps.sh [" + "|".join(VERBS.values()) + "]"


def write_lines(lines):
    sys.stdout.buffer.write("".join(line + "\n" for line in lines).encode(errors="surrogateescape"))


def say(text):
    if text is None:
        return 3
    write_lines([text])
    return 0


def answer(record):
    return say(None if record is None else record.text)


def current_record(records):
    """The current step: the first done step whose refactor is pending, else the first open step; None when none."""
    pending = [r for r in records if r.state == "done" and r.pending == "1"]
    open_steps = [r for r in records if handed_out(r)]
    return next(iter(pending + open_steps), None)


def current(records):
    return answer(current_record(records))


def open_record(records):
    """The step a run works on now, as fused_step.open_step takes it: the open re-pin step directly after the first
    refactor-pending step, else the current step; None when none (#4734)."""
    current_step = current_record(records)
    if current_step is not None and current_step.state == "done":
        after = records[records.index(current_step) + 1:][:1]
        if after and after[0].state == "open" and after[0].text.startswith(REPIN_STEP):
            return after[0]
    return current_step


def last_done_record(records):
    done = [r for r in records if r.state == "done"]
    return done[-1] if done else None


def last_done(records):
    return answer(last_done_record(records))


def current_or_last_done_record(records):
    """The step `current-or-last-done` prints: the current step, else the last done one; None when neither."""
    return current_record(records) or last_done_record(records)


def current_or_last_done(records):
    return answer(current_or_last_done_record(records))


def phase_next(records):
    phases = (next_phase(r.text) for r in records)
    return say(next((phase for phase in phases if phase), None))


def has_mark(records, name):
    return 0 if any(carries_mark(trailing_markers(r.text), name) for r in records) else 3


def criterion(text, k):
    # prefix and every section: pinned by test_criterion_prints_the_kth_step_line_of_every_acceptance_criteria_section
    found = issue_body.criteria(text, prefix=True, occurrence="all")
    records = ledger_steps("\n".join(line for _, line in found))
    return answer(records[k - 1] if 1 <= k <= len(records) else None)


def main(argv):
    verb = argv[0] if argv else ""
    if verb and verb not in VERBS:
        return entry.refuse(usage=USAGE)
    if verb == "criterion" and entry.whole_number(argv[1] if len(argv) > 1 else "", 0) is None:
        return entry.refuse(usage=USAGE)
    if verb == "has-mark" and (len(argv) < 2 or not argv[1]):
        return entry.refuse(usage=USAGE)
    text = read_ledger_stdin()
    if verb == "criterion":
        return criterion(text, int(argv[1]) % 2**64)
    records = ledger_steps(text)
    if verb == "has-mark":
        return has_mark(records, argv[1])
    if verb == "current":
        return current(records)
    if verb == "open":
        return answer(open_record(records))
    if verb == "last-done":
        return last_done(records)
    if verb == "current-or-last-done":
        return current_or_last_done(records)
    if verb == "next-phase":
        return phase_next(records)
    write_lines("\t".join(record) for record in records)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
