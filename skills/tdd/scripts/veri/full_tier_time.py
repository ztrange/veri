"""full-tier-time.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys
import tempfile

import entry
import run_dir

USAGE = "usage: full-tier-time.sh [--record <seconds>] <command>"


def record_path():
    return os.path.join(run_dir.main_tree_from_files(os.getcwd()), ".tdd", "full-tier-time.json")


def whole(value):
    return isinstance(value, str) and value.isascii() and value.isdigit()


def read_times(record):
    """The stored {command: seconds}; ValueError (or OSError) when the file is not a valid record."""
    if not os.path.exists(record):
        return {}
    with open(record) as f:
        times = json.load(f)
    if not isinstance(times, dict) or not all(whole(v) for v in times.values()):
        raise ValueError("not a record of whole-number seconds")
    return times


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
        if len(argv) < 3 or not argv[1].isascii() or not argv[1].isdigit():
            return entry.refuse(usage=USAGE)
        record = record_path()
        os.makedirs(os.path.dirname(record), exist_ok=True)
        try:
            times = read_times(record)
        except (OSError, ValueError):
            times = {}
        times[argv[2]] = argv[1]
        write_times(record, times)
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
