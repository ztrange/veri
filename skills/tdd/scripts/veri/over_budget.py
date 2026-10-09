"""over-budget.sh's verdict, run in-process."""
import math
import os
import re
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USAGE = "usage: over-budget.sh <tier> <seconds> <usual>"
NUMBER = re.compile(r"[+-]?(?:(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?|0[xX][0-9a-fA-F]+|inf(?:inity)?|nan)", re.IGNORECASE)

ESCAPE = re.compile(r"\\([0-7]{1,3}|.)", re.DOTALL)
ESCAPES = {"\\": "\\", "n": "\n", "t": "\t", '"': '"', "r": "\r", "b": "\b", "f": "\f", "v": "\v", "a": "\a",
           "/": "/"}


def _escaped(match):
    code = match.group(1)
    if code[0] in "01234567":
        return chr(int(code, 8))
    return ESCAPES.get(code, match.group(0))


def _unescape(text):
    return ESCAPE.sub(_escaped, text)


def _number(text):
    kept = text.rstrip(" \t\r")
    if kept != kept.rstrip() or not NUMBER.fullmatch(kept.lstrip()):
        return None
    try:
        return float(text)
    except ValueError:
        return float(int(text, 16))


def main(argv):
    if len(argv) < 3 or not all(argv[:3]):
        print(USAGE, file=sys.stderr)
        return 2
    tier, seconds, usual = (_unescape(value) for value in argv[:3])
    limits = subprocess.run([os.path.join(SCRIPTS, "time-budget.sh")], stdout=subprocess.PIPE, text=True)
    if limits.returncode != 0:
        return 2
    lines = limits.stdout.splitlines()
    budget, ratio = lines[0], lines[-1]
    s = _number(seconds)
    product = _number(ratio) * (_number(usual) or 0)
    if s is None:
        s, limit = seconds, budget
        product = "%d" % product if math.isfinite(product) and product == int(product) else "%.6g" % product
    else:
        limit = _number(budget)
    if not ((tier == "unit" and s > limit) or s > product):
        return 1
    if sys.stdout is None:
        print("over-budget: i/o error occurred while writing /dev/stdout", file=sys.stderr)
        return 2
    print("⏱ %s tier took %s s (usual %s s, ratio %s, unit budget %s s)" % (tier, seconds, usual, ratio, budget))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
