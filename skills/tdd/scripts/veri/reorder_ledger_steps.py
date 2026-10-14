"""reorder-ledger-steps.sh's move, run in-process."""
import sys

import ledger

USAGE = "usage: reorder-ledger-steps.sh <ledger-file> <step-substring> after <anchor-substring>"


def main(argv):
    if len(argv) != 4:
        print(USAGE, file=sys.stderr)
        return 2
    with open(argv[0], newline="") as file:
        lines = file.read().split("\n")
    moved = next(i for i, line in enumerate(lines) if argv[1] in line)
    step = lines.pop(moved)
    anchor = next(i for i, line in enumerate(lines) if argv[3] in line)
    lines.insert(anchor + 1, step)
    ledger.replace_ledger(argv[0], "\n".join(lines))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
