"""detach-command.sh's start and wait, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys
import time

import detach
import pid_file as pid_file_module
import rerun_alone
import tunables

WRAPPER = '"$@"; rc=$?; echo "$rc" > "$0.tmp"; mv "$0.tmp" "$0"'
USAGE = "usage: detach-command.sh start <name> <cmd> [args…] | wait <name> [max-seconds]"


def _read(path):
    with open(path) as handle:
        return handle.read().rstrip("\n")


def _recorded(exit_file, alone=None):
    if not os.path.isfile(exit_file):
        return None
    code = _read(exit_file)
    if code == "0":
        return 0
    if alone and rerun_alone.main([alone, exit_file[:-5] + ".out"]) == 0:
        return 0
    print(code)
    return 1


def _alive(pid_file):
    try:
        pid = _read(pid_file).split("\n")[0]
        if not re.fullmatch(r"\s*[-+]?[0-9]+\s*", pid):
            return False
        os.kill(int(pid), 0)
    except OSError:
        return False
    return True


def _limit(text):
    try:
        return int(text, 8 if text.startswith("0") else 10)
    except ValueError:
        print(f'detach-command.sh: {text}: value too great for base (error token is "{text}")',
              file=sys.stderr)
        return None


def _stopping_now():
    try:
        return _read(".tdd/stop") == "now"
    except OSError:
        return False


def _wait(exit_file, pid_file, text, alone=None):
    start = int(time.time())
    poll = tunables.read("VERI_POLL") or "1"
    if not re.fullmatch(r"[0-9]+(\.[0-9]*)?|\.[0-9]+", poll):
        print(f"detach-command.sh: VERI_POLL must be a non-negative number: {poll}", file=sys.stderr)
        return 2
    while True:
        code = _recorded(exit_file, alone)
        if code is not None:
            return code
        if not _alive(pid_file):
            code = _recorded(exit_file, alone)
            return 2 if code is None else code
        if _stopping_now():
            return 2
        limit = _limit(text)
        if limit is not None and int(time.time()) - start >= limit:
            return 3
        time.sleep(float(poll))


def _refused(argv):
    if len(argv) < 2 or argv[0] not in ("start", "wait"):
        return True
    if argv[0] == "start":
        return len(argv) < 3
    return len(argv) > 2 and argv[2] != "" and not re.fullmatch("[0-9]+", argv[2])


def main(argv):
    alone = None
    if argv[:1] == ["wait"] and len(argv) >= 4 and argv[-2] == "--alone":
        alone, argv = argv[-1], argv[:-2]
    if _refused(argv):
        print(USAGE, file=sys.stderr)
        return 2
    mode, name, rest = argv[0], argv[1], argv[2:]
    exit_file, pid_file = f".tdd/{name}.exit", f".tdd/{name}.pid"
    if mode == "wait":
        return _wait(exit_file, pid_file, rest[0] if rest and rest[0] else "590", alone)
    try:
        os.unlink(exit_file)
    except FileNotFoundError:
        pass
    with open(f".tdd/{name}.out", "w") as out:
        pid = detach.start(["sh", "-c", WRAPPER, exit_file, *rest], subprocess.DEVNULL, out, out)
    pid_file_module.record(pid_file, pid)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
