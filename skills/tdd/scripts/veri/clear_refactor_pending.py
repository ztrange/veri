"""clear-refactor-pending.sh's clear, run in-process."""
import sys

import ledger

USAGE = "usage: clear-refactor-pending.sh <ledger-file> <matcher>"


def to_contract(code):
    return code if 0 <= code <= 3 else 2


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    with open(argv[0], newline="") as file:
        cleared, new = ledger.ledger_clear_pending(file.read(), argv[1] if len(argv) > 1 else "")
    if not isinstance(cleared, bool):
        return to_contract(cleared)
    if not cleared:
        return 3
    with open(argv[0], "w", newline="") as file:
        file.write(new)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
