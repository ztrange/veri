"""The pid-file reader: number_in, live_conductor and supervising, run in-process."""

import os
import re
import subprocess


def number_in(file):
    if not os.path.isfile(file):
        return None
    try:
        with open(file, "rb") as f:
            n = f.readline().rstrip(b"\n").strip(b" \t")
    except OSError:
        return None
    return n.decode() if re.fullmatch(rb"[0-9]+", n) else None


def recorded_alive(path):
    pid = number_in(path + "/.tdd/conductor.pid")
    if pid is None or int(pid) == 0:
        return None
    try:
        os.kill(int(pid), 0)
    except (OSError, OverflowError):
        return None
    return pid


def _ps(field, pid):
    ps = subprocess.run(["ps", "-o", field + "=", "-p", str(int(pid))], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return ps.stdout.strip() if ps.returncode == 0 else ""


def live_conductor(path):
    pid = recorded_alive(path)
    if pid is None:
        return None
    if "run_conductor.py" not in _ps("command", _ps("ppid", pid)):
        return None
    if "claude" not in (os.path.basename(word) for word in _ps("command", pid).split()[:2]):
        return None
    return pid


def supervising(pid, name):
    ps = subprocess.run(["ps", "-p", pid, "-o", "args="], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return ps.returncode == 0 and (f"supervise.sh {name} " in ps.stdout or f"veri/supervise.py {name} " in ps.stdout)
