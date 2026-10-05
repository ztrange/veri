"""transform-touches-tests.sh's range check, run in-process."""
import subprocess
import sys

USAGE = "usage: transform-touches-tests.sh <base-sha>"


def refuse(message=None):
    if message:
        print(message, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


def main(argv):
    base = argv[0] if argv else ""
    if not base:
        return refuse()
    check = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"])
    if check.returncode != 0:
        return refuse(f"transform-touches-tests.sh: base-sha does not resolve to a commit: {base}")
    return 0
