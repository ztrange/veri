"""event.sh's mark, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import errno
import os
import shutil
import subprocess
import sys
import time

import entry
import tunables

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


def toplevel():
    here = os.getcwd()
    while True:
        if os.path.exists(os.path.join(here, ".git")):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            return ""
        here = parent


def line(args, context, ts, awake):
    fields = [(key, context.get(key, b"") if name else args[0]) for key, name in CONTEXT]
    fields += [arg.partition(b"=")[::2] for arg in args[1:]]
    text = b'{"ts": %d, "awake": ' % ts + awake
    for key, value in fields:
        text += b', "' + escape(key) + b'": "' + escape(value) + b'"'
    return text + b"}\n"


def awake_reading():
    clock = tunables.read_bytes("VERI_AWAKE_CLOCK")
    if clock:
        result = run_clock(os.fsdecode(clock))
        if result is None:
            return 2
        if result.returncode != 0:
            return result.returncode if 0 < result.returncode <= 3 else 2
        awake = result.stdout.rstrip(b"\n")
    else:
        awake = b"%d" % time.clock_gettime(getattr(time, "CLOCK_UPTIME_RAW", time.CLOCK_MONOTONIC))
    return awake


def journal_path(clone, issue):
    try:
        with open(os.path.join(clone, ".git", "config"), "rb") as handle:
            config = handle.read().decode()
    except OSError:
        return None
    url = ""
    for text in config.splitlines():
        text = text.strip()
        if text.startswith("url") and "=" in text:
            url = text.partition("=")[2].strip()
            break
    owner, repo = url.removesuffix(".git").split("/")[-2:] if url.count("/") >= 2 else ("", "")
    if not (owner and repo and issue):
        return None
    home = tunables.read("VERI_HOME") or os.path.expanduser("~/.veri")
    return os.path.join(home, "runs", owner + "-" + repo, issue + ".jsonl")


def append(directory, context, event, fields=(), ts=None):
    args = [os.fsencode(event)] + [os.fsencode(field) for field in fields]
    context = {os.fsencode(key): os.fsencode(value) for key, value in context.items()}
    if not args[0]:
        sys.stderr.buffer.write(USAGE)
        return 2
    if args[0] == b"structural-pass":
        refusal = structural_pass_refusal(args[1:])
        if refusal:
            sys.stderr.buffer.write(refusal + b"\n")
            return 2
    top = os.fspath(directory) or toplevel()
    tdd = os.path.join(top, ".tdd")
    os.makedirs(tdd, exist_ok=True)
    ts = int(time.time()) if ts is None else ts
    awake = awake_reading()
    if isinstance(awake, int):
        return awake
    fd = os.open(tdd + "/events.jsonl", os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o666)
    try:
        text = line(args, context, ts, awake)
        os.write(fd, text)
    finally:
        os.close(fd)
    journal = journal_path(top, os.fsdecode(context.get(b"issue", b"")))
    if journal:
        os.makedirs(os.path.dirname(journal), exist_ok=True)
        fd = os.open(journal, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o666)
        try:
            os.write(fd, text)
        finally:
            os.close(fd)
    return 0


def context(environ):
    return {os.fsdecode(key): environ.get(os.fsdecode(name), "") for key, name in CONTEXT if name}


def mark(directory, context, event, fields=(), ts=None):
    try:
        return append(directory, context, event, fields, ts)
    except Exception as exc:
        sys.stderr.flush()
        os.write(2, entry.refusal(main, exc).encode())
        return 2
    finally:
        sys.stderr.flush()


def main(argv):
    if not argv:
        sys.stderr.buffer.write(USAGE)
        return 2
    context = {key: tunables.read_bytes(name) for key, name in CONTEXT if name}
    return append("", context, argv[0], argv[1:])


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
