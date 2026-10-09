"""next-unchecked.sh's computation, run in-process."""
import sys

from ledger import handed_out, ledger_steps, read_ledger_stdin


def main(argv):
    text = read_ledger_stdin()
    for record in ledger_steps(text):
        if handed_out(record):
            sys.stdout.buffer.write((record[6] + "\n").encode(errors="surrogateescape"))
            return 0
    return 3


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
