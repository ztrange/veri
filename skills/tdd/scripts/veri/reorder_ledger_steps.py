"""reorder-ledger-steps.sh's move, run in-process."""
import sys

import ledger

USAGE = "usage: reorder-ledger-steps.sh <ledger-file> <step-substring> before|after <anchor-substring>"


def _matches(lines, substring):
    return [i for i, line in enumerate(lines) if substring in line]


def _frozen(line):
    return line.startswith("- [x]") or ledger.PENDING_MARK in line


def main(argv):
    if len(argv) != 4:
        print(USAGE, file=sys.stderr)
        return 2
    with open(argv[0], newline="") as file:
        lines = file.read().split("\n")
    matched = _matches(lines, argv[1])
    if not matched:
        print(f"no step matches: {argv[1]}", file=sys.stderr)
        return 1
    if len(matched) > 1:
        print(f"more than one step matches: {argv[1]}", file=sys.stderr)
        return 1
    moved = matched[0]
    if _frozen(lines[moved]):
        print(f"cannot move a ticked step: {lines[moved]}", file=sys.stderr)
        return 1
    matched = _matches(lines, argv[3])
    if not matched:
        print(f"no step matches: {argv[3]}", file=sys.stderr)
        return 1
    anchor = matched[0]
    if _frozen(lines[anchor]):
        print(f"cannot move a step relative to a ticked step: {lines[anchor]}", file=sys.stderr)
        return 1
    step = lines.pop(moved)
    anchor = _matches(lines, argv[3])[0]
    lines.insert(anchor if argv[2] == "before" else anchor + 1, step)
    ledger.replace_ledger(argv[0], "\n".join(lines))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
