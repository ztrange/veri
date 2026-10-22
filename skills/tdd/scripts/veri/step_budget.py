"""step-budget.sh's two budgets, run in-process."""
import os
import re
import sys

import tunables
from entry import write

USAGE = "usage: step-budget.sh (takes no arguments)"
NUMBER = re.compile(rb"[0-9]+(\.[0-9]+)?")


def budgets():
    step = tunables.read_bytes("VERI_STEP_BUDGET", b"12")
    run = tunables.read_bytes("VERI_RUN_BUDGET", b"120")
    for name, value in ((b"VERI_STEP_BUDGET", step), (b"VERI_RUN_BUDGET", run)):
        if not NUMBER.fullmatch(value):
            write(sys.stderr, b"step-budget: " + name + b" must be a non-negative decimal number: " + value, before=False)
            return 2, step, run
    return 0, step, run


def main(argv):
    if argv:
        write(sys.stderr, os.fsencode(USAGE), before=False)
        return 2
    code, step, run = budgets()
    if code:
        return code
    write(sys.stdout, step, before=False)
    write(sys.stdout, run, before=False)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
