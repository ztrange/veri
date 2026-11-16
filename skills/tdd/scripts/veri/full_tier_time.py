"""full-tier-time.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys
import tempfile
import time

import entry
import run_dir

USAGE = "usage: full-tier-time.sh [--record <seconds>] <command>"


def record_path():
    return os.path.join(run_dir.main_tree_from_files(os.getcwd()), ".tdd", "full-tier-time.json")


def at_path(record):
    """The recorded-at file beside `record`: {command: the epoch seconds its time was recorded at}."""
    return os.path.join(os.path.dirname(record), "full-tier-time-at.json")


def now():
    return int(time.time())


def whole(value):
    return isinstance(value, str) and entry.whole_number(value, 0) is not None


def read_times(record):
    """The stored {command: seconds}; ValueError (or OSError) when the file is not a valid record."""
    if not os.path.exists(record):
        return {}
    with open(record) as f:
        times = json.load(f)
    if not isinstance(times, dict) or not all(whole(v) for v in times.values()):
        raise ValueError("not a record of whole-number seconds")
    return times


def read_recorded_at(record):
    """The stored {command: epoch seconds} beside `record`; ValueError (or OSError) when that file is not one."""
    path = at_path(record)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        stamps = json.load(f)
    if not isinstance(stamps, dict) or not all(type(v) is int and v >= 0 for v in stamps.values()):
        raise ValueError("not a record of epoch seconds")
    return stamps


def age(record, command):
    """Seconds since `command`'s time was recorded; None when no recorded-at says (no file, no entry, unreadable)."""
    try:
        recorded_at = read_recorded_at(record).get(command)
    except (OSError, ValueError):
        return None
    return None if recorded_at is None else now() - recorded_at


def write_times(record, times):
    directory = os.path.dirname(record)
    fd, partial = tempfile.mkstemp(dir=directory, prefix="full-tier-time.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(times, f)
        os.replace(partial, record)
    except BaseException:
        if os.path.exists(partial):
            os.unlink(partial)
        raise


def main(argv):
    if not argv:
        return entry.refuse(usage=USAGE)
    if argv[0] == "--record":
        if len(argv) < 3 or not whole(argv[1]):
            return entry.refuse(usage=USAGE)
        record = record_path()
        os.makedirs(os.path.dirname(record), exist_ok=True)
        try:
            times = read_times(record)
        except (OSError, ValueError):
            times = {}
        times[argv[2]] = argv[1]
        write_times(record, times)
        try:
            stamps = read_recorded_at(record)
        except (OSError, ValueError):
            stamps = {}
        stamps[argv[2]] = now()
        write_times(at_path(record), stamps)
        return 0
    record = record_path()
    try:
        times = read_times(record)
    except (OSError, ValueError) as exc:
        print("full-tier-time: unreadable record %s: %s" % (record, exc), file=sys.stderr)
        return 2
    if argv[0] not in times:
        return 3
    print(times[argv[0]])
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
