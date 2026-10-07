"""detach-command.sh's start and wait, run in-process."""
import os
import re
import subprocess
import sys
import time

import detach

WRAPPER = '"$@"; rc=$?; echo "$rc" > "$0.tmp"; mv "$0.tmp" "$0"'
USAGE = "usage: detach-command.sh start <name> <cmd> [args…] | wait <name> [max-seconds]"


def _read(path):
    with open(path) as handle:
        return handle.read().rstrip("\n")


def _recorded(exit_file):
    if not os.path.isfile(exit_file):
        return None
    code = _read(exit_file)
    if code == "0":
        return 0
    print(code)
    return 1


def _alive(pid_file):
    try:
        pid = _read(pid_file)
        if not re.fullmatch(r"\s*[-+]?[0-9]+\s*", pid):
            return False
        os.kill(int(pid), 0)
    except OSError:
        return False
    return True


def _wait(exit_file, pid_file, limit):
    start = int(time.time())
    while True:
        code = _recorded(exit_file)
        if code is not None:
            return code
        if not _alive(pid_file):
            code = _recorded(exit_file)
            return 2 if code is None else code
        if int(time.time()) - start >= limit:
            return 3
        time.sleep(1)


def _refused(argv):
    if len(argv) < 2 or argv[0] not in ("start", "wait"):
        return True
    if argv[0] == "start":
        return len(argv) < 3
    return len(argv) > 2 and argv[2] != "" and not re.fullmatch("[0-9]+", argv[2])


def main(argv):
    if _refused(argv):
        print(USAGE, file=sys.stderr)
        return 2
    mode, name, rest = argv[0], argv[1], argv[2:]
    exit_file, pid_file = f".tdd/{name}.exit", f".tdd/{name}.pid"
    if mode == "wait":
        return _wait(exit_file, pid_file, int(rest[0]) if rest and rest[0] else 60)
    try:
        os.unlink(exit_file)
    except FileNotFoundError:
        pass
    with open(f".tdd/{name}.out", "w") as out:
        pid = detach.start(["sh", "-c", WRAPPER, exit_file, *rest], subprocess.DEVNULL, out, out)
    with open(pid_file, "w") as handle:
        handle.write(f"{pid}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
