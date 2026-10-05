"""run-affordable.sh's projection, run in-process."""
import os
import re
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USAGE = "usage: run-affordable.sh <steps-remaining> (a whole number)"


def main(argv):
    remaining = argv[0] if argv else ""
    if not re.fullmatch(r"[0-9]+", remaining):
        print("run-affordable.sh: <steps-remaining> is not a whole number: '%s'" % remaining, file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    steps = subprocess.run([os.path.join(SCRIPTS, "step-cost.sh"), "--steps"], stdout=subprocess.PIPE, text=True)
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
    print("spent %.2f, steps remaining %d, median %.2f, projection %.2f" % (spent, n, median, projection))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
