"""clear-refactor-pending.sh's clear, run in-process."""
import sys

import ledger

USAGE = "usage: clear-refactor-pending.sh <ledger-file> <matcher>"


def complain(path, message):
    print(f"clear-refactor-pending.sh: {path}: {message}", file=sys.stderr)


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        with open(argv[0], "rb") as file:
            raw = file.read()
    except OSError as error:
        complain(argv[0], error.strerror)
        return 2
    text = ledger.decode_ledger(raw)
    cleared, new = ledger.ledger_clear_pending(text, argv[1] if len(argv) > 1 else "")
    if not cleared:
        return 3
    data = (new.rstrip("\n") + "\n").encode(errors="surrogateescape")
    try:
        ledger.replace_ledger(argv[0], data)
    except ledger.LeftBehind as error:
        complain(argv[0], f"left {error.filename} behind")
        return 2
    except OSError:
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
