"""step-budget.sh's two budgets, run in-process."""
import os
import re
import sys

USAGE = "usage: step-budget.sh (takes no arguments)"
NUMBER = re.compile(rb"[0-9]+(\.[0-9]+)?")


def _write(stream, data):
    stream.buffer.write(data + b"\n")
    stream.buffer.flush()


def main(argv):
    if argv:
        _write(sys.stderr, os.fsencode(USAGE))
        return 2
    step = os.environb.get(b"VERI_STEP_BUDGET", b"12")
    run = os.environb.get(b"VERI_RUN_BUDGET", b"120")
    for name, value in ((b"VERI_STEP_BUDGET", step), (b"VERI_RUN_BUDGET", run)):
        if not NUMBER.fullmatch(value):
            _write(sys.stderr, b"step-budget: " + name + b" must be a non-negative decimal number: " + value)
            return 2
    _write(sys.stdout, step)
    _write(sys.stdout, run)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
