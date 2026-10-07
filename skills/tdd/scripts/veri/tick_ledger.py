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
    with open(argv[0], newline="") as file:
        ticked, new = ledger.ledger_tick(file.read().replace("\0", ""), (argv[1:] or [""])[0], pending)
    if not ticked:
        return 3
    try:
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(argv[0])))
    except OSError:
        return 2
    try:
        with os.fdopen(fd, "w") as file:
            file.write(new.rstrip("\n") + "\n")
        shutil.copymode(argv[0], tmp)
        os.replace(tmp, argv[0])
    except OSError:
        os.unlink(tmp)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
