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
    try:
        with open(argv[0], "rb") as file:
            raw = file.read()
    except OSError as error:
        print(f"clear-refactor-pending.sh: {argv[0]}: {error.strerror}", file=sys.stderr)
        return 2
    text = raw.replace(b"\0", b"").decode(errors="surrogateescape")
    cleared, new = ledger.ledger_clear_pending(text, argv[1] if len(argv) > 1 else "")
    if not isinstance(cleared, bool):
        return to_contract(cleared)
    if not cleared:
        return 3
    data = (new.rstrip("\n") + "\n").encode(errors="surrogateescape")
    path = os.path.realpath(argv[0])
    try:
        backup = write_beside(path, raw)
    except OSError:
        return 2
    code = 0
    try:
        try:
            file = open(argv[0], "wb")
        except OSError:
            return 2
        try:
            with file:
                file.write(data)
        except OSError:
            code = 2
            try:
                with os.fdopen(os.open(argv[0], os.O_WRONLY), "wb") as file:
                    file.write(raw)
            except OSError:
                try:
                    os.replace(backup, path)
                except OSError:
                    pass
    finally:
        try:
            os.unlink(backup)
        except OSError:
            code = 2
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
