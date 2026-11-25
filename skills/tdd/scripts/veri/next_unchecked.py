"""next-unchecked.sh's computation, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

from entry import no_arguments
from ledger import handed_out, ledger_steps, read_ledger_stdin


USAGE = "usage: next-unchecked.sh (the ledger on stdin)"


def main(argv):
    refused = no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    text = read_ledger_stdin()
    for record in ledger_steps(text):
        if handed_out(record):
            sys.stdout.buffer.write((record.text + "\n").encode(errors="surrogateescape"))
            return 0
    return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
