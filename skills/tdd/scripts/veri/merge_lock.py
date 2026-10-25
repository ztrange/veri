"""merge-lock.sh's verbs, run in-process."""
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time

import tunables

VERBS = ("take", "release", "holder")


def _caller_pid(args):
    return args[1] if args[:1] == ["--pid"] else str(os.getppid())


def _start_time(pid):
    out = subprocess.run(["ps", "-o", "lstart=", "-p", pid], stdout=subprocess.PIPE, text=True).stdout
    return "_".join(out.split())


def _read(record):
    with open(record) as f:
        return f.read()


def _read_pid(record):
    text = _read(record)
    return text, int(text.split()[0])


def _alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass
    return True


def _needs_pid(args, force_ok):
    if "--pid" in args or (force_ok and "--force" in args):
        return False
    print("merge-lock.sh: --pid <pid> is required", file=sys.stderr)
    return True


def _take(lock, record, args):
    if _needs_pid(args, False):
        return 2
    pid = _caller_pid(args)
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    staged = tempfile.mkdtemp(prefix=".merge.lock.", dir=os.path.dirname(lock))
    with open(os.path.join(staged, "holder"), "w") as f:
        f.write(f"{pid} {socket.gethostname()} {_start_time(pid)}\n")
    reported = False
    while True:
        if not os.path.isdir(lock):
            try:
                os.rename(staged, lock)
                break
            except OSError:
                pass
        try:
            text, holder = _read_pid(record)
        except (OSError, ValueError, IndexError):
            print(f"merge-lock.sh: missing, unreadable or malformed holder record {record}", file=sys.stderr)
            return 2
        if not reported:
            if not _alive(holder):
                print("stale lock: " + text, end="", file=sys.stderr, flush=True)
                reported = True
        time.sleep(float(tunables.read("VERI_MERGE_LOCK_POLL", "30")))
    return 0


def _release(lock, record, args):
    if _needs_pid(args, True):
        return 2
    if not os.path.isdir(lock):
        return 3
    pid = _caller_pid([a for a in args if a != "--force"])
    if "--force" not in args:
        if _read(record).split()[0] != pid:
            return 1
    shutil.rmtree(lock)
    return 0


def _holder(lock, record, args):
    if not os.path.isdir(lock):
        return 3
    text, pid = _read_pid(record)
    reused = not _alive(pid) or text.split()[2:3] != [_start_time(str(pid))]
    if reused:
        print("stale lock: " + text, end="")
        return 1
    print(text, end="")
    return 0


_HANDLERS = {"take": _take, "release": _release, "holder": _holder}


def main(argv):
    if not argv or argv[0] not in VERBS:
        print("usage: merge-lock.sh take --pid <pid> | release --pid <pid> | release --force | holder", file=sys.stderr)
        return 2
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            stdout=subprocess.PIPE, text=True, check=True).stdout.strip()
    lock = os.path.join(os.path.dirname(common), ".tdd", "merge.lock")
    return _HANDLERS[argv[0]](lock, os.path.join(lock, "holder"), argv[1:])


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
