"""tick-ledger.sh's tick, run in-process."""
import sys

import ledger

USAGE = "usage: tick-ledger.sh [--refactor-pending] <ledger-file> <matcher>"


def complain(message):
    print(f"tick-ledger.sh: {message}", file=sys.stderr)


def main(argv):
    pending = argv[:1] == ["--refactor-pending"]
    if pending:
        argv = argv[1:]
    phase = argv[1] if argv[:1] == ["--phase"] and len(argv) > 1 else None
    if phase:
        argv = argv[2:]
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        with open(argv[0], newline="") as file:
            text = file.read()
    except OSError as error:
        complain(f"{argv[0]}: {error.strerror}")
        return 2
    except UnicodeDecodeError as error:
        complain(f"{argv[0]}: {error.reason}")
        return 2
    text, matcher = text.replace("\0", ""), (argv[1:] or [""])[0]
    if phase:
        try:
            ticked, new = ledger.ledger_mark_phase(text, matcher, phase)
        except ValueError as error:
            complain(str(error))
            return 2
    else:
        ticked, new = ledger.ledger_tick(text, matcher, pending)
    if not ticked:
        return 3
    try:
        ledger.replace_ledger(argv[0], new.rstrip("\n") + "\n")
    except ledger.LeftBehind as error:
        complain(f"left {error.filename} behind")
        return 2
    except OSError:
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
