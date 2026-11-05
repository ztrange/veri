"""full-tier-time.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys

USAGE = "usage: full-tier-time.sh [--record <seconds>] <command>"


def main_tree(start):
    directory = os.path.abspath(start)
    while True:
        dotgit = os.path.join(directory, ".git")
        if os.path.isdir(dotgit):
            return directory
        if os.path.isfile(dotgit):
            with open(dotgit) as f:
                gitdir = f.read().strip().removeprefix("gitdir:").strip()
            gitdir = os.path.join(directory, gitdir)
            with open(os.path.join(gitdir, "commondir")) as f:
                common = os.path.join(gitdir, f.read().strip())
            return os.path.dirname(os.path.normpath(common))
        parent = os.path.dirname(directory)
        if parent == directory:
            return os.path.abspath(start)
        directory = parent


def record_path():
    return os.path.join(main_tree(os.getcwd()), ".tdd", "full-tier-time.json")


def read_times(record):
    if not os.path.exists(record):
        return {}
    with open(record) as f:
        return json.load(f)


def refuse():
    print(USAGE, file=sys.stderr)
    return 2


def main(argv):
    if not argv:
        return refuse()
    if argv[0] == "--record":
        if len(argv) < 3 or not argv[1].isascii() or not argv[1].isdigit():
            return refuse()
        record = record_path()
        os.makedirs(os.path.dirname(record), exist_ok=True)
        times = read_times(record)
        times[argv[2]] = argv[1]
        with open(record, "w") as f:
            json.dump(times, f)
        return 0
    times = read_times(record_path())
    if argv[0] not in times:
        return 3
    print(times[argv[0]])
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
