"""merge-lock.sh's verbs, run in-process."""
import os
import shutil
import socket
import subprocess
import sys
import time

VERBS = ("take", "release", "holder")


def _caller_pid(args):
    return args[1] if args[:1] == ["--pid"] else str(os.getppid())


def main(argv):
    if not argv or argv[0] not in VERBS:
        print("usage: merge-lock.sh take|release|holder", file=sys.stderr)
        return 2
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            stdout=subprocess.PIPE, text=True, check=True).stdout.strip()
    lock = os.path.join(os.path.dirname(common), ".tdd", "merge.lock")
    record = os.path.join(lock, "holder")
    if argv[0] == "take":
        pid = _caller_pid(argv[1:])
        os.makedirs(os.path.dirname(lock), exist_ok=True)
        reported = False
        while True:
            try:
                os.mkdir(lock)
                break
            except FileExistsError:
                if not reported:
                    try:
                        with open(record) as f:
                            text = f.read()
                        os.kill(int(text.split()[0]), 0)
                    except ProcessLookupError:
                        print("stale lock: " + text, end="", file=sys.stderr, flush=True)
                        reported = True
                    except (OSError, ValueError, IndexError):
                        pass
                time.sleep(float(os.environ.get("VERI_MERGE_LOCK_POLL", "30")))
        with open(record, "w") as f:
            f.write(f"{pid} {socket.gethostname()} {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n")
    elif argv[0] == "release":
        rest = [a for a in argv[1:] if a != "--force"]
        pid = _caller_pid(rest)
        if "--force" not in argv:
            with open(record) as f:
                if f.read().split()[0] != pid:
                    return 1
        shutil.rmtree(lock)
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
