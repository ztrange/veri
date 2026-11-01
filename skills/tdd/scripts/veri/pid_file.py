"""The pid-file reader: number_in, live_conductor and supervising, run in-process."""

import os
import re
import subprocess


def _conductors():
    listing = subprocess.run(["ps", "-axo", "pid=,command="], stdout=subprocess.PIPE, text=True).stdout
    return re.findall(r"^\s*(\d+)\s+(?:.*\s)?\S*run_conductor\.py (\d+)(?=\s|$)", listing, re.M)


def _cwd(pid):
    lsof = subprocess.run(["lsof", "-a", "-d", "cwd", "-Fn", "-p", pid], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return next((line[1:] for line in lsof.stdout.splitlines() if line.startswith("n")), None)


def conductor_processes():
    import status
    root = status.main_working_tree()
    return [issue for pid, issue in _conductors() if (_cwd(pid) or "").startswith(root + "/") or _cwd(pid) == root]


def starting_runs(root):
    return [issue for _, issue in _conductors() if os.path.isdir(os.path.join(root, ".tdd", "wt", issue, ".tdd"))]


def number_in(file):
    if not os.path.isfile(file):
        return None
    try:
        with open(file, "rb") as f:
            n = f.readline().rstrip(b"\n").strip(b" \t")
    except OSError:
        return None
    return n.decode() if re.fullmatch(rb"[0-9]+", n) else None


def _pid_path(path):
    return path + "/.tdd/conductor.pid"


def recorded_alive(path):
    pid = number_in(_pid_path(path))
    if pid is None or int(pid) == 0:
        return None
    try:
        os.kill(int(pid), 0)
    except (OSError, OverflowError):
        return None
    return pid


def _ps(field, pid):
    try:
        ps = subprocess.run(["ps", "-o", field + "=", "-p", str(int(pid))], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    except OSError:
        return False
    return ps.stdout.strip() if ps.returncode == 0 else None


def recorded_started(path):
    pid = recorded_alive(path)
    if pid is None:
        return None
    with open(_pid_path(path), "rb") as f:
        f.readline()
        started = f.readline().decode().strip()
    if started and started != _ps("lstart", pid):
        return None
    return pid


def live_conductor(path):
    pid = recorded_started(path)
    if pid is None:
        return None
    parent = _ps("ppid", pid)
    parent_command = _ps("command", parent) if parent else ""
    if parent_command and "run_conductor.py" not in parent_command:
        return None
    own = _ps("command", pid)
    if own and "claude" not in (os.path.basename(word) for word in own.split()[:2]):
        return None
    return pid


def supervising(pid, name):
    ps = subprocess.run(["ps", "-p", pid, "-o", "args="], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return ps.returncode == 0 and (f"supervise.sh {name} " in ps.stdout or f"veri/supervise.py {name} " in ps.stdout)
