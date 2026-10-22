"""time-budget.sh's two tunables, run in-process."""
import re
import sys

import tunables
from entry import write

NUMBER = re.compile(rb"[0-9]+(\.[0-9]+)?")


def limits():
    budget = tunables.read_bytes("VERI_UNIT_BUDGET") or b"10"
    ratio = tunables.read_bytes("VERI_TIME_WARN_RATIO") or b"1.5"
    for value, what in (
        (budget, b"VERI_UNIT_BUDGET must be a number of seconds"),
        (ratio, b"VERI_TIME_WARN_RATIO must be a number"),
    ):
        if not NUMBER.fullmatch(value):
            write(sys.stderr, b"time-budget: " + what + b": " + value + b"\n", before=False, end="")
            return 2, budget, ratio
    return 0, budget, ratio


def main(argv):
    code, budget, ratio = limits()
    if code == 0:
        write(sys.stdout, budget + b"\n" + ratio + b"\n", before=False, end="")
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
