"""red-setup.sh's record and worst, run in-process: the setup a verified Red's case needed, and the run's worst step."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import entry
import event
import ledger
import ledger_steps
import run_dir
import tunables
from report import report_read

USAGE = ("usage: red-setup.sh record <n> < <red-report>\n"
         "       red-setup.sh worst <n> <owed-file>")
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


def main(argv):
    verb, n = (list(argv) + ["", ""])[:2]
    if entry.whole_number(n) is None:
        return entry.refuse(usage=USAGE)
    if verb == "record" and len(argv) == 2:
        return record(n)
    return entry.refuse(usage=USAGE)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
