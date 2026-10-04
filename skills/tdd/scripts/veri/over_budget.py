"""over-budget.sh's verdict, run in-process."""
import os
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USAGE = "usage: over-budget.sh <tier> <seconds> <usual>"


def _number(text):
    try:
        return float(text)
    except ValueError:
        return float(int(text, 16))


def main(argv):
    if len(argv) < 3 or not all(argv[:3]):
        print(USAGE, file=sys.stderr)
        return 2
    tier, seconds, usual = argv[:3]
    limits = subprocess.run([os.path.join(SCRIPTS, "time-budget.sh")], stdout=subprocess.PIPE, text=True)
    if limits.returncode != 0:
        return 2
    lines = limits.stdout.splitlines()
    budget, ratio = lines[0], lines[-1]
    s = _number(seconds)
    over = (tier == "unit" and s > _number(budget)) or s > _number(ratio) * _number(usual)
    if not over:
        return 1
    print("⏱ %s tier took %s s (usual %s s, ratio %s, unit budget %s s)" % (tier, seconds, usual, ratio, budget))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
