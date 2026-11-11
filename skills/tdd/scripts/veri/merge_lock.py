"""merge-lock.sh's verbs, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time

import tunables

VERBS = ("take", "release", "holder", "gate")


def _caller_pid(args):
    pid = _value(args, "--pid")
    return pid if pid is not None else str(os.getppid())


USAGE = ("usage: merge-lock.sh take --pid <pid> [--owner <token>] | release --pid <pid> [--owner <token>] "
         "| release --force | holder | gate [--keep] --pid <pid> [--owner <token>] -- <cmd>")


class _Usage(Exception):
    pass


def _usage_guarded(handler):
    def guarded(lock, record, args):
        try:
            return handler(lock, record, args)
        except _Usage:
            print(USAGE, file=sys.stderr)
            return 2
    return guarded


def _value(args, flag):
    if flag not in args:
        return None
    i = args.index(flag) + 1
    if i >= len(args) or args[i].startswith("--"):
        raise _Usage
    return args[i]


def _owner(args):
    return _value(args, "--owner")


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


def _reused(text, pid):
    return not _alive(pid) or text.split()[2:3] != [_start_time(str(pid))]


def _needs_pid(args, force_ok):
    if "--pid" in args or (force_ok and "--force" in args):
        return False
    print("merge-lock.sh: --pid <pid> is required", file=sys.stderr)
    return True


def _poll_wait():
    time.sleep(float(tunables.read("VERI_MERGE_LOCK_POLL", "30")))


# release unlinks the record before the directory, so a take can read in that gap;
# a directory that keeps no record past this many polls is not a release in progress.
_MISSING_RECORD_GRACE = 5


@_usage_guarded
def _take(lock, record, args):
    if _needs_pid(args, False):
        return 2
    pid = _caller_pid(args)
    _owner(args)
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    staged = tempfile.mkdtemp(prefix=".merge.lock.", dir=os.path.dirname(lock))
    try:
        with open(os.path.join(staged, "holder"), "w") as f:
            owner = _owner(args)
            f.write(f"{pid} {socket.gethostname()} {_start_time(pid)}" + (f" {owner}" if owner else "") + "\n")
        reported = False
        missing = 0
        while True:
            if not _alive(int(pid)):
                print(f"merge-lock.sh: pid {pid} is no longer alive", file=sys.stderr)
                return 2
            if not os.path.isdir(lock):
                try:
                    os.rename(staged, lock)
                    return 0
                except OSError:
                    if not os.path.isdir(staged):
                        print(f"merge-lock.sh: staged lock dir {staged} is gone", file=sys.stderr)
                        return 2
            try:
                text, holder = _read_pid(record)
            except (OSError, ValueError, IndexError) as err:
                if not os.path.isdir(lock):
                    _poll_wait()
                    continue
                if isinstance(err, FileNotFoundError):
                    missing += 1
                    if missing <= _MISSING_RECORD_GRACE:
                        _poll_wait()
                        continue
                print(f"merge-lock.sh: missing, unreadable or malformed holder record {record}", file=sys.stderr)
                return 2
            missing = 0
            if not reported:
                if _reused(text, holder):
                    print("stale lock: " + text, end="", file=sys.stderr, flush=True)
                    reported = True
            _poll_wait()
    finally:
        shutil.rmtree(staged, ignore_errors=True)


@_usage_guarded
def _release(lock, record, args):
    if _needs_pid(args, True):
        return 2
    forced = "--force" in args
    pid = _caller_pid([a for a in args if a != "--force"])
    owner = _owner(args)
    if not os.path.isdir(lock):
        return 3
    if not forced:
        fields = _read(record).split()
        if fields[0] != pid:
            return 1
        if fields[3:4] != ([owner] if owner else []):
            return 1
    if os.path.isfile(record):
        owner = (_read(record).split()[3:4] or [""])[0]
    shutil.rmtree(lock)
    git_dir = os.path.join(os.path.dirname(os.path.dirname(lock)), ".git")
    for path in glob.glob(os.path.join(git_dir, "veri-merge-*.token")):
        if not forced or _read(path).strip() == owner:
            os.remove(path)
    return 0


def _holder(lock, record, args):
    if not os.path.isdir(lock):
        return 3
    text, pid = _read_pid(record)
    if _reused(text, pid):
        print("stale lock: " + text, end="")
        return 1
    print(text, end="")
    return 0


@_usage_guarded
def _gate(lock, record, args):
    head = args[:args.index("--")] if "--" in args else args
    value = head[head.index("--pid") + 1:][:1] if "--pid" in head else []
    if not (value and value[0].isdigit() and int(value[0]) > 0) or "--" not in args or args.index("--") == len(args) - 1:
        print("usage: merge-lock.sh gate [--keep] --pid <pid> [--owner <token>] -- <cmd>", file=sys.stderr)
        return 2
    _owner(head)
    code = subprocess.run(args[args.index("--") + 1:]).returncode
    if code in (0, 3):
        return code
    if "--keep" in args:
        print(f"merge-lock.sh: command exited {code}; lock kept, clear it with merge-lock.sh release --force", file=sys.stderr)
        return code
    _release(lock, record, head)
    return code


_HANDLERS = {"take": _take, "release": _release, "holder": _holder, "gate": _gate}


def main(argv):
    if not argv or argv[0] not in VERBS:
        print(USAGE, file=sys.stderr)
        return 2
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            stdout=subprocess.PIPE, text=True, check=True).stdout.strip()
    lock = os.path.join(os.path.dirname(common), ".tdd", "merge.lock")
    return _HANDLERS[argv[0]](lock, os.path.join(lock, "holder"), argv[1:])


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
