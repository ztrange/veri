"""leaf-timeout.sh's derivation, run in-process."""
import os
import re
import sys

USAGE = "usage: leaf-timeout.sh <baseline-seconds> [refactor | --full <full-seconds>]"


def is_whole(text):
    return re.fullmatch(r"[0-9]+", text) is not None


def arith(text):
    match = re.fullmatch(r"(-?)([0-9]+)", text)
    if match is None:
        return None
    value = int(match[2])
    return -value if match[1] else value


def refuse(message):
    print(message, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


def require_seconds(name, value):
    if not is_whole(value):
        return refuse(f"leaf-timeout: {name} must be a whole number >= 0: {value}")
    return 0


def main(argv):
    override = os.environ.get("VERI_TIMEOUT", "")
    if override:
        if not is_whole(override) or int(override) < 1:
            print(f"leaf-timeout: VERI_TIMEOUT must be a whole number >= 1: {override}", file=sys.stderr)
            return 2
        print(override)
        return 0
    baseline = argv[0] if argv else ""
    code = require_seconds("<baseline-seconds>", baseline)
    if code:
        return code
    if argv[1:2] == ["--full"]:
        full = argv[2] if len(argv) > 2 else ""
        code = require_seconds("<full-seconds>", full)
        if code:
            return code
        baseline = full
    baseline = arith(baseline)
    if baseline is None:
        return 1
    derived = max(900, baseline * 6)
    if argv[1:2] == ["refactor"]:
        budget = arith(os.environ.get("VERI_REFACTOR_BUDGET") or "5")
        if budget is None:
            return 1
        derived = derived * max(1, budget)
    print(derived)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
