"""drop-ledger-step.sh's removal, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import ledger
import reorder_ledger_steps

USAGE = "usage: drop-ledger-step.sh <ledger-file> <step-substring>"


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    lines = ledger.read_ledger(argv[0]).split("\n")
    index = reorder_ledger_steps._open_match(lines, argv[1], "cannot drop a ticked step")
    if index is None:
        return 1
    del lines[index]
    ledger.replace_ledger(argv[0], "\n".join(lines).encode(errors="surrogateescape"))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
