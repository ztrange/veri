"""next-pending-refactor.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

from ledger import ledger_steps, read_ledger_stdin


def refactor_pending(record):
    return record[1] == "done" and record[3] == "1"


def main(argv):
    for record in ledger_steps(read_ledger_stdin()):
        if refactor_pending(record):
            sys.stdout.buffer.write((record[6] + "\n").encode(errors="surrogateescape"))
            return 0
    return 3



if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
