"""stop-requested.sh's answer, run in-process."""
import os
import sys

FILE = ".tdd/stop"
USAGE = b"usage: stop-requested.sh [--clear]\n"


def main(argv):
    if argv == ["--clear"]:
        os.unlink(FILE)
        return 0
    if argv:
        sys.stderr.buffer.write(USAGE)
        return 2
    if not os.path.isfile(FILE):
        return 3
    with open(FILE, "rb") as stop:
        sys.stdout.buffer.write(stop.readline())
    return 0
