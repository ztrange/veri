"""time-budget.sh's two tunables, run in-process."""
import os
import re
import sys

NUMBER = re.compile(rb"[0-9]+(\.[0-9]+)?")


def write(stream, data):
    stream.buffer.write(data)
    stream.buffer.flush()


def main(argv):
    budget = os.environb.get(b"VERI_UNIT_BUDGET") or b"10"
    ratio = os.environb.get(b"VERI_TIME_WARN_RATIO") or b"1.5"
    for value, what in (
        (budget, b"VERI_UNIT_BUDGET must be a number of seconds"),
        (ratio, b"VERI_TIME_WARN_RATIO must be a number"),
    ):
        if not NUMBER.fullmatch(value):
            write(sys.stderr, b"time-budget: " + what + b": " + value + b"\n")
            return 2
    write(sys.stdout, budget + b"\n" + ratio + b"\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
