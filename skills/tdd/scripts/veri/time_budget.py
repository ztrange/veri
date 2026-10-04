"""time-budget.sh's two tunables, run in-process."""
import os
import re
import sys


def main(argv):
    budget = os.environ.get("VERI_UNIT_BUDGET") or "10"
    ratio = os.environ.get("VERI_TIME_WARN_RATIO") or "1.5"
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", budget):
        print(f"time-budget: VERI_UNIT_BUDGET must be a number of seconds: {budget}", file=sys.stderr)
        return 2
    print(budget)
    print(ratio)
    return 0

