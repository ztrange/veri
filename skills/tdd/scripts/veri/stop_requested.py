"""stop-requested.sh's answer, run in-process."""
import os
import sys

import stop_modes

FILE = ".tdd/stop"
USAGE = b"usage: stop-requested.sh [--clear]\n"


def main(argv):
    if argv == ["--clear"]:
        os.unlink(FILE)
        return 0
    if argv and argv != [""]:
        sys.stderr.buffer.write(USAGE)
        return 2
    if not os.path.isfile(FILE):
        return 3
    with open(FILE, "rb") as stop:
        line = stop.readline()
    mode = line.removesuffix(b"\n")
    if not stop_modes.stop_mode_known(mode.decode()):
        sys.stderr.buffer.write(
            f"stop-requested: {FILE} must name a mode — {stop_modes.modes_named()}: '".encode()
            + mode + b"'\n")
        return 2
    sys.stdout.buffer.write(line)
    return 0
