"""clear-refactor-pending.sh's clear, run in-process."""
import os
import sys
import tempfile

import ledger

USAGE = "usage: clear-refactor-pending.sh <ledger-file> <matcher>"


def to_contract(code):
    return code if 0 <= code <= 3 else 2


def write_beside(path, data):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "wb") as file:
            file.write(data)
    except BaseException:
        os.unlink(tmp)
        raise
    return tmp


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    with open(argv[0], "rb") as file:
        raw = file.read()
    text = raw.replace(b"\0", b"").decode(errors="surrogateescape")
    cleared, new = ledger.ledger_clear_pending(text, argv[1] if len(argv) > 1 else "")
    if not isinstance(cleared, bool):
        return to_contract(cleared)
    if not cleared:
        return 3
    data = (new.rstrip("\n") + "\n").encode(errors="surrogateescape")
    try:
        tmp = write_beside(os.path.abspath(argv[0]), data)
    except OSError:
        return 2
    os.unlink(tmp)
    file = open(argv[0], "wb")
    try:
        with file:
            file.write(data)
    except OSError:
        try:
            with os.fdopen(os.open(argv[0], os.O_WRONLY), "wb") as file:
                file.write(raw)
        except OSError:
            os.replace(write_beside(os.path.realpath(argv[0]), raw), os.path.realpath(argv[0]))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
