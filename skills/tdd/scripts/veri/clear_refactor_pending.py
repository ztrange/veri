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


def complain(path, message):
    print(f"clear-refactor-pending.sh: {path}: {message}", file=sys.stderr)


def holds(path, raw):
    try:
        with open(path, "rb") as file:
            return file.read() == raw
    except OSError:
        return False


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
                    file.truncate()
            except OSError:
                try:
                    os.replace(backup, path)
                except OSError:
                    if not holds(argv[0], raw):
                        complain(argv[0], f"write failed; old ledger kept at {backup}")
                        backup = None
    finally:
        if backup is not None:
            try:
                os.unlink(backup)
            except OSError as error:
                complain(argv[0], f"could not remove backup {backup}: {error.strerror}")
                code = 2
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
