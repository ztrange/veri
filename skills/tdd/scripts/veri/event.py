"""event.sh's mark, run in-process."""
import os
import sys
import time

USAGE = "usage: event.sh <event> [key=value …]\n".encode()
CONTEXT = ((b"issue", b"VERI_ISSUE"), (b"actor", b"VERI_ACTOR"), (b"phase", b"VERI_PHASE"),
           (b"step", b"VERI_STEP"), (b"event", None), (b"attempt", b"VERI_ATTEMPT"),
           (b"skill_commit", b"VERI_SKILL_COMMIT"))
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


def line(args):
    fields = [(key, os.environb.get(name, b"") if name else args[0]) for key, name in CONTEXT]
    fields += [arg.partition(b"=")[::2] for arg in args[1:]]
    clock = getattr(time, "CLOCK_UPTIME_RAW", time.CLOCK_MONOTONIC)
    text = b'{"ts": %d, "awake": %d' % (int(time.time()), int(time.clock_gettime(clock)))
    for key, value in fields:
        text += b', "' + key + b'": "' + value + b'"'
    return text + b"}\n"


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
    os.makedirs(".tdd", exist_ok=True)
    with open(".tdd/events.jsonl", "ab") as log:
        log.write(line(args))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
