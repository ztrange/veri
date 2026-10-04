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
    if not NUMBER.fullmatch(budget):
        write(sys.stderr, b"time-budget: VERI_UNIT_BUDGET must be a number of seconds: " + budget + b"\n")
        return 2
    if not NUMBER.fullmatch(ratio):
        write(sys.stderr, b"time-budget: VERI_TIME_WARN_RATIO must be a number: " + ratio + b"\n")
        return 2
    write(sys.stdout, budget + b"\n" + ratio + b"\n")
    return 0
