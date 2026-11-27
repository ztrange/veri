"""red-setup.sh's record and worst, run in-process: the setup a verified Red's case needed, and the run's worst step."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import entry
import event
import event_log
import ledger
import ledger_steps
import refactor_owed
import run_dir
import run_records
import tunables
from report import report_read

USAGE = ("usage: red-setup.sh record <n> < <red-report>\n"
         "       red-setup.sh worst <n> <owed-file>")
REASON = "testability"
OWN_ROW = refactor_owed.NOT_DONE_MARK + REASON + " | "
SETUP = re.compile(r"\s*([0-9]+)\s*\|\s*(.*?)\s*")


def record(n):
    """Write `red-setup count=<count> what=<what>` for the ledger's current step from stdin's `SETUP:` line: 0 written,
    3 no `SETUP:` line, 2 a malformed line or no current step (nothing written either way)."""
    stream = getattr(sys.stdin, "buffer", None)
    report = stream.read().decode(errors="replace") if stream else sys.stdin.read()
    line = report_read(report, ("SETUP",), optional_space=True).get("SETUP")
    if line is None:
        return 3
    found = SETUP.fullmatch(line)
    if not found:
        sys.stderr.write("red-setup: malformed SETUP: line %r; want SETUP: <n> | <what>\n" % line)
        return 2
    try:
        step = ledger_steps.current_record(ledger.ledger_steps(ledger.read_ledger(run_dir.ledger(".", n))))
    except OSError as error:
        sys.stderr.write("red-setup: cannot read the ledger of #%s: %s\n" % (n, error.strerror))
        return 2
    if step is None:
        sys.stderr.write("red-setup: the ledger of #%s has no current step\n" % n)
        return 2
    return event.mark(".", event.context(tunables.with_values(VERI_ISSUE=n, VERI_STEP=step.text)), "red-setup",
                      ["count=%d" % int(found.group(1)), "what=" + found.group(2)])


def worst(n, owed):
    """Record the run's worst Red, the step whose latest `red-setup` count is highest, as one `testability` not-done row
    of <owed> when that count exceeds VERI_SETUP_THRESHOLD, an earlier entry's row dropped either way: 0 recorded, 3
    none over it, 2 a threshold that is not a whole number or an owed file it cannot write."""
    threshold = entry.whole_number(tunables.get("VERI_SETUP_THRESHOLD", unless_empty=True), 0)
    if threshold is None:
        sys.stderr.write("red-setup: VERI_SETUP_THRESHOLD must be a whole number, got '%s'\n"
                         % tunables.get("VERI_SETUP_THRESHOLD"))
        return 2
    latest = {}
    for mark in event_log.events(".", "red-setup"):
        if str(mark.get("issue")) == n and entry.whole_number(str(mark.get("count")), 0) is not None:
            latest[mark.get("step", "")] = (int(mark["count"]), mark.get("what", ""))
    # An earlier entry's row goes first, on every outcome: a resume whose worst count fell to the threshold or below
    # (a higher threshold, a revised Red) must not leave a stale candidate to be filed.
    try:
        drop_own_row(owed)
    except OSError as error:
        sys.stderr.write("red-setup: cannot rewrite %s: %s\n" % (owed, error.strerror))
        return 2
    if not latest:
        return 3
    step, (count, what) = max(latest.items(), key=lambda item: item[1][0])
    if count <= threshold:
        return 3
    # not_done's 1 is a failed write, which it names on stderr: no answer, not a clean negative.
    # The row reaches the candidates issue: the leaf's own words may name a local path, the host or the account.
    row = run_records.redact_local("%s: %d stubs and setup (%s)" % (step, count, what), os.getcwd())
    return 2 if refactor_owed.not_done(owed, row, REASON) else 0


def drop_own_row(owed):
    """Remove from <owed> the testability row an earlier `worst` recorded, so a resume replaces it rather than adding a
    second; an absent file is left absent."""
    try:
        with open(owed, errors="surrogateescape") as file:
            lines = file.readlines()
    except FileNotFoundError:
        return
    kept = [line for line in lines if not line.startswith(OWN_ROW)]
    if kept != lines:
        with open(owed, "w", errors="surrogateescape") as file:
            file.write("".join(kept))


def main(argv):
    verb, n = (list(argv) + ["", ""])[:2]
    if entry.whole_number(n) is None:
        return entry.refuse(usage=USAGE)
    if verb == "record" and len(argv) == 2:
        return record(n)
    if verb == "worst" and len(argv) == 3 and argv[2]:
        return worst(n, argv[2])
    return entry.refuse(usage=USAGE)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
