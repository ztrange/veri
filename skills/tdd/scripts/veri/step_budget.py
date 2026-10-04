"""step-budget.sh's two budgets, run in-process."""
import os
import sys

USAGE = "usage: step-budget.sh (takes no arguments)"


def _write(stream, text):
    stream.buffer.write(os.fsencode(text + "\n"))


def main(argv):
    if argv:
        _write(sys.stderr, USAGE)
        return 2
    _write(sys.stdout, "12")
    _write(sys.stdout, "120")
    return 0

