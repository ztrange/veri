"""tick-ledger.sh's tick, run in-process."""
import os
import shutil
import sys
import tempfile

import ledger

USAGE = "usage: tick-ledger.sh [--refactor-pending] <ledger-file> <matcher>"


def main(argv):
    pending = argv[:1] == ["--refactor-pending"]
    if pending:
        argv = argv[1:]
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        with open(argv[0], newline="") as file:
            text = file.read()
    except OSError as error:
        print(f"tick-ledger.sh: {argv[0]}: {error.strerror}", file=sys.stderr)
        return 2
    except UnicodeDecodeError as error:
        print(f"tick-ledger.sh: {argv[0]}: {error.reason}", file=sys.stderr)
        return 2
    ticked, new = ledger.ledger_tick(text.replace("\0", ""), (argv[1:] or [""])[0], pending)
    if not ticked:
        return 3
    path = os.path.realpath(argv[0])
    try:
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
    except OSError:
        return 2
    try:
        with os.fdopen(fd, "w") as file:
            file.write(new.rstrip("\n") + "\n")
        shutil.copymode(path, tmp)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
