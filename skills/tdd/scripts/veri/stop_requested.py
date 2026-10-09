"""stop-requested.sh's answer, run in-process."""
import contextlib
import os
import sys

import stop_modes

FILE = ".tdd/stop"
USAGE = b"usage: stop-requested.sh [--clear]\n"


def main(argv):
    if argv == ["--clear"]:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(FILE)
        return 0
    if argv and argv != [""]:
        sys.stderr.buffer.write(USAGE)
        return 2
    if not os.path.isfile(FILE):
        return 3
    try:
        with open(FILE, "rb") as stop:
            line = stop.readline().replace(b"\0", b"")
    except OSError:
        line = b""
    mode = line[:-1] if line.endswith(b"\n") else b""
    if not stop_modes.stop_mode_known(mode.decode(errors="surrogateescape")):
        sys.stderr.buffer.write(
            f"stop-requested: {FILE} must name a mode — {stop_modes.modes_named()}: '".encode()
            + mode + b"'\n")
        return 2
    sys.stdout.buffer.write(mode + b"\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
