"""merge-lock.sh's verbs, run in-process."""
import os
import socket
import subprocess
import sys
import time

VERBS = ("take", "release", "holder")


def main(argv):
    if not argv or argv[0] not in VERBS:
        print("usage: merge-lock.sh take|release|holder", file=sys.stderr)
        return 2
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            stdout=subprocess.PIPE, text=True, check=True).stdout.strip()
    lock = os.path.join(os.path.dirname(common), ".tdd", "merge.lock")
    record = os.path.join(lock, "holder")
    if argv[0] == "take":
        pid = argv[2] if argv[1:2] == ["--pid"] else str(os.getppid())
        os.makedirs(os.path.dirname(lock), exist_ok=True)
        os.mkdir(lock)
        with open(record, "w") as f:
            f.write(f"{pid} {socket.gethostname()} {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n")
    elif argv[0] == "holder":
        if not os.path.isdir(lock):
            return 3
        with open(record) as f:
            text = f.read()
        try:
            os.kill(int(text.split()[0]), 0)
        except ProcessLookupError:
            print("stale lock: " + text, end="")
            return 1
        print(text, end="")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
