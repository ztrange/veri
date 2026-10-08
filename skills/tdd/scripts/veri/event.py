"""event.sh's mark, run in-process."""
import os
import sys

USAGE = "usage: event.sh <event> [key=value …]\n".encode()
STOPPED = (b"candidates-done", b"budget-spent", b"nothing-structural")
REASONS = b", ".join(STOPPED)


def structural_pass_refusal(args):
    transforms = budget = stopped = b""
    for arg in args:
        key, sep, value = arg.partition(b"=")
        if not sep:
            continue
        if key == b"transforms":
            transforms = value
        elif key == b"budget":
            budget = value
        elif key == b"stopped":
            stopped = value
            if stopped not in STOPPED:
                return b"event.sh: structural-pass stopped=" + stopped + b" is not one of " + REASONS
    if not stopped:
        return b"event.sh: structural-pass needs stopped=, one of " + REASONS
    if stopped == b"budget-spent" and transforms != budget:
        return (b"event.sh: structural-pass stopped=budget-spent needs transforms equal to budget, got transforms="
                + transforms + b" budget=" + budget)
    return None


def main(argv):
    args = [os.fsencode(arg) for arg in argv]
    if not args or not args[0]:
        sys.stderr.buffer.write(USAGE)
        return 2
    if args[0] == b"structural-pass":
        refusal = structural_pass_refusal(args[1:])
        if refusal:
            sys.stderr.buffer.write(refusal + b"\n")
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
