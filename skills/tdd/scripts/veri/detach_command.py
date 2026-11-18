"""detach-command.sh's start and wait, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import calendar
import os
import re
import signal
import subprocess
import sys
import time

import detach
import entry
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
    if alone and rerun_alone.rerun(alone, exit_file[:-5] + ".out") == 0:
        return 0
    print(code)
    return 1


def _pid(pid_file):
    return _read(pid_file).split("\n")[0]


def _alive(pid_file):
    try:
        pid = _pid(pid_file)
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


def _started(pid_file, fallback):
    """The epoch second `start` recorded on the pid file's line 2 (ps lstart under TZ=UTC); <fallback> without one."""
    try:
        return calendar.timegm(time.strptime(pid_file_module.start_recorded(pid_file), "%a %b %d %H:%M:%S %Y"))
    except (OSError, ValueError):
        return fallback


def _stopping_now():
    try:
        return _read(".tdd/stop") == "now"
    except OSError:
        return False


def _wait(exit_file, pid_file, text, alone=None, total=None):
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
        if total is not None and int(time.time()) - _started(pid_file, start) >= total:
            pid = int(_pid(pid_file))
            if not pid_file_module.start_matches(pid_file, pid):
                return 2
            _stop_group(pid)
            print(f"detach-command.sh: still running past --total {total} seconds; stopped its process group",
                  file=sys.stderr)
            return 2
        limit = _limit(text)
        if limit is not None and int(time.time()) - start >= limit:
            return 3
        time.sleep(float(poll))


def _stop_group(group):
    """As a `now` stop ends a detached command: TERM its process group, then KILL after VERI_STOP_KILL_GRACE."""
    try:
        os.killpg(group, signal.SIGTERM)
        time.sleep(float(tunables.get("VERI_STOP_KILL_GRACE", unless_empty=True)))
        os.killpg(group, signal.SIGKILL)
    except ProcessLookupError:
        pass


def _refused(argv):
    if len(argv) < 2 or argv[0] not in ("start", "wait"):
        return True
    if argv[0] == "start":
        return len(argv) < 3
    return len(argv) > 2 and argv[2] != "" and entry.whole_number(argv[2], minimum=0) is None


def main(argv):
    total = None
    if argv[:1] == ["wait"] and "--total" in argv[2:-1]:
        at = argv.index("--total", 2)
        total, argv = entry.whole_number(argv[at + 1], minimum=0), argv[:at] + argv[at + 2:]
        if total is None:
            print(USAGE, file=sys.stderr)
            return 2
    alone = None
    if argv[:1] == ["wait"] and len(argv) >= 4 and argv[-2] == "--alone":
        alone, argv = argv[-1], argv[:-2]
    if _refused(argv):
        print(USAGE, file=sys.stderr)
        return 2
    mode, name, rest = argv[0], argv[1], argv[2:]
    exit_file, pid_file = f".tdd/{name}.exit", f".tdd/{name}.pid"
    if mode == "wait":
        return _wait(exit_file, pid_file, rest[0] if rest and rest[0] else "590", alone, total)
    try:
        os.unlink(exit_file)
    except FileNotFoundError:
        pass
    with open(f".tdd/{name}.out", "w") as out:
        pid = detach.start(["sh", "-c", WRAPPER, exit_file, *rest], subprocess.DEVNULL, out, out)
    pid_file_module.record(pid_file, pid)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
