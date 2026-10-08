"""event.sh's mark, run in-process."""
import errno
import os
import shutil
import subprocess
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


ESCAPES = {0x22: b'\\"', 0x5c: b"\\\\", 0x08: b"\\b", 0x0c: b"\\f", 0x0a: b"\\n", 0x0d: b"\\r",
           0x09: b"\\t"}
LEADS = ((0xE0, 0xC0, 2, 0x1F), (0xF0, 0xE0, 3, 0x0F), (0xF8, 0xF0, 4, 0x07))


def escape(value):
    out = bytearray()
    i = 0
    while i < len(value):
        byte = value[i]
        if byte in ESCAPES:
            out += ESCAPES[byte]
        elif 0x20 <= byte < 0x7f:
            out.append(byte)
        else:
            nbytes, cp = next(((n, byte & m) for mask, lead, n, m in LEADS if byte & mask == lead), (1, byte))
            for k in range(1, nbytes):
                cont = value[i + k] if i + k < len(value) else 0
                cp = (cp << 6) | (cont & 0x3F)
            if cp <= 0xFFFF:
                out += b"\\u%04x" % cp
            else:
                cp -= 0x10000
                out += b"\\u%04x\\u%04x" % (0xD800 | (cp >> 10), 0xDC00 | (cp & 0x3FF))
            i += nbytes - 1
        i += 1
    return bytes(out)


def run_clock(clock):
    path = shutil.which(clock) or clock
    try:
        try:
            return subprocess.run([path], stdout=subprocess.PIPE)
        except OSError as error:
            # hazard: a shell runs an executable with no #! line as a script; exec refuses it with ENOEXEC.
            if error.errno != errno.ENOEXEC:
                raise
            return subprocess.run(["/bin/sh", path], stdout=subprocess.PIPE)
    except (FileNotFoundError, PermissionError):
        return None


def line(args, ts, awake):
    fields = [(key, os.environb.get(name, b"") if name else args[0]) for key, name in CONTEXT]
    fields += [arg.partition(b"=")[::2] for arg in args[1:]]
    text = b'{"ts": %d, "awake": ' % ts + awake
    for key, value in fields:
        text += b', "' + escape(key) + b'": "' + escape(value) + b'"'
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
    ts = int(time.time())
    clock = os.environb.get(b"VERI_AWAKE_CLOCK", b"")
    if clock:
        result = run_clock(os.fsdecode(clock))
        if result is None:
            return 2
        if result.returncode != 0:
            return result.returncode if 0 < result.returncode <= 3 else 2
        awake = result.stdout.rstrip(b"\n")
    else:
        awake = b"%d" % time.clock_gettime(getattr(time, "CLOCK_UPTIME_RAW", time.CLOCK_MONOTONIC))
    fd = os.open(".tdd/events.jsonl", os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o666)
    try:
        os.write(fd, line(args, ts, awake))
    finally:
        os.close(fd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
