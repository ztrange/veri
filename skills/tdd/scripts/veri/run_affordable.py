"""run-affordable.sh's projection, run in-process."""
import os
import re
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USAGE = "usage: run-affordable.sh <steps-remaining> (a whole number)"


def _passed(status):
    return status if 0 <= status <= 3 else 2


def main(argv):
    remaining = argv[0] if argv else ""
    if not re.fullmatch(r"[0-9]+", remaining):
        print("run-affordable.sh: <steps-remaining> is not a whole number: '%s'" % remaining, file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    budgets = subprocess.run([os.path.join(SCRIPTS, "step-budget.sh")], stdout=subprocess.PIPE, text=True)
    if budgets.returncode:
        return _passed(budgets.returncode)
    ceiling = float(budgets.stdout.splitlines()[-1])
    steps = subprocess.run([os.path.join(SCRIPTS, "step-cost.sh"), "--steps"], stdout=subprocess.PIPE, text=True)
    if steps.returncode:
        return _passed(steps.returncode)
    spent = 0.0
    full = []
    for line in steps.stdout.splitlines():
        dollars, leaves = line.split()
        spent += float(dollars)
        if int(leaves) > 2:
            full.append(float(dollars))
    if not full:
        return 3
    median = full[len(full) // 2]
    n = int(remaining)
    projection = spent + n * median
    if not projection > ceiling:
        return 0
    print("spent %.2f, steps remaining %d, median %.2f, projection %.2f" % (spent, n, median, projection))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
