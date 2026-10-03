"""leaf-timeout.sh's derivation, run in-process."""
import re
import sys

USAGE = "usage: leaf-timeout.sh <baseline-seconds> [refactor | --full <full-seconds>]"


def refuse(message):
    print(message, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


def main(argv):
    baseline = argv[0] if argv else ""
    if not re.fullmatch(r"[0-9]+", baseline):
        return refuse(f"leaf-timeout: <baseline-seconds> must be a whole number >= 0: {baseline}")
    print(max(900, int(baseline) * 6))
    return 0
