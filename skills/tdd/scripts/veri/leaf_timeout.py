"""leaf-timeout.sh's derivation, run in-process."""
import os
import re
import sys

USAGE = "usage: leaf-timeout.sh <baseline-seconds> [refactor | --full <full-seconds>]"


def is_whole(text):
    return re.fullmatch(r"[0-9]+", text) is not None


def refuse(message):
    print(message, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


def main(argv):
    override = os.environ.get("VERI_TIMEOUT", "")
    if override:
        if not is_whole(override) or int(override) < 1:
            print(f"leaf-timeout: VERI_TIMEOUT must be a whole number >= 1: {override}", file=sys.stderr)
            return 2
        print(override)
        return 0
    baseline = argv[0] if argv else ""
    if not is_whole(baseline):
        return refuse(f"leaf-timeout: <baseline-seconds> must be a whole number >= 0: {baseline}")
    derived = max(900, int(baseline) * 6)
    if argv[1:2] == ["refactor"]:
        derived *= max(1, int(os.environ.get("VERI_REFACTOR_BUDGET") or "5"))
    print(derived)
    return 0
