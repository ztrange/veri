"""next-pending-refactor.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import ledger
import run_dir
from entry import no_arguments
from ledger import ledger_steps, read_ledger_stdin


def refactor_pending(record):
    return record.state == "done" and record.pending == "1"


def repin_next(wt, n):
    """The open re-pin step pin-reject-route.sh --recheck inserted directly after the first refactor-pending step, or
    None (#4510)."""
    records = ledger.ledger_steps(ledger.read_ledger(run_dir.ledger(wt, n)))
    for before, record in zip(records, records[1:]):
        if refactor_pending(before):
            return record.text if record.state == "open" and record.text.startswith(ledger.REPIN_STEP) else None
    return None


USAGE = "usage: next-pending-refactor.sh (the ledger on stdin)"


def main(argv):
    refused = no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    for record in ledger_steps(read_ledger_stdin()):
        if refactor_pending(record):
            sys.stdout.buffer.write((record.text + "\n").encode(errors="surrogateescape"))
            return 0
    return 3



if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
