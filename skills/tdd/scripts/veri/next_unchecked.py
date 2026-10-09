"""next-unchecked.sh's computation, run in-process."""
import sys

from ledger import ledger_steps, read_ledger_stdin


def handed_out(record):
    return record[1] == "open" and record[2] in ("step", "diff-checked")


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
