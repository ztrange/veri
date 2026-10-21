"""reorder-ledger-steps.sh's move, run in-process."""
import sys

import ledger

USAGE = "usage: reorder-ledger-steps.sh <ledger-file> <step-substring> before|after <anchor-substring>"


def _matches(lines, substring):
    return [i for i, line in enumerate(lines) if substring in line]


def _only_match(lines, substring):
    matched = _matches(lines, substring)
    if not matched:
        print(f"no step matches: {substring}", file=sys.stderr)
        return None
    if len(matched) > 1:
        print(f"more than one step matches: {substring}", file=sys.stderr)
        return None
    return matched[0]


def _frozen(line):
    return line.startswith("- [x]") or ledger.PENDING_MARK in line


def _open_match(lines, substring, refusal):
    index = _only_match(lines, substring)
    if index is None:
        return None
    if _frozen(lines[index]):
        print(f"{refusal}: {lines[index]}", file=sys.stderr)
        return None
    return index


def main(argv):
    if len(argv) != 4 or argv[2] not in ("before", "after"):
        print(USAGE, file=sys.stderr)
        return 2
    lines = ledger.read_ledger(argv[0]).split("\n")
    moved = _open_match(lines, argv[1], "cannot move a ticked step")
    if moved is None:
        return 1
    anchor = _open_match(lines, argv[3], "cannot move a step relative to a ticked step")
    if anchor is None:
        return 1
    step = lines.pop(moved)
    if anchor > moved:
        anchor -= 1
    lines.insert(anchor if argv[2] == "before" else anchor + 1, step)
    ledger.replace_ledger(argv[0], "\n".join(lines).encode(errors="surrogateescape"))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
