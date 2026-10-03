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
    digits = match[2]
    try:
        value = int(digits, 8 if digits[0] == "0" else 10)
    except ValueError:
        return None
    return -value if match[1] else value


def wrap(value):
    return (value + 2**63) % 2**64 - 2**63


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
    if argv[1:2] == ["--full"]:
        full = argv[2] if len(argv) > 2 else ""
        if not is_whole(full):
            return refuse(f"leaf-timeout: <full-seconds> must be a whole number >= 0: {full}")
        baseline = full
    baseline = arith(baseline)
    if baseline is None:
        return 1
    derived = max(900, wrap(baseline * 6))
    if argv[1:2] == ["refactor"]:
        budget = arith(os.environ.get("VERI_REFACTOR_BUDGET") or "5")
        if budget is None:
            return 1
        derived = wrap(derived * max(1, budget))
    print(derived)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
