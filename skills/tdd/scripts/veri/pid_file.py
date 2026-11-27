"""The pid-file reader: number_in, live_conductor and supervising, run in-process."""

import os
import re
import subprocess

import run_dir
import tunables


def listing(*, quiet=False):
    """The process table as `ps -axo pid=,command=` prints it, one `<pid> <command line>` per line.

    Whatever ps printed is the answer, whatever it exited with; `quiet` sends its stderr to /dev/null. A machine
    without ps raises FileNotFoundError: every caller lets that propagate."""
    return subprocess.run(["ps", "-axo", "pid=,command="], stdout=subprocess.PIPE,
                          **({"stderr": subprocess.DEVNULL} if quiet else {}), text=True).stdout


def argument_lines():
    """Every process's arguments as `ps -axo args=` prints them, one line each.

    A ps that exits non-zero raises CalledProcessError, a missing one FileNotFoundError."""
    return subprocess.run(["ps", "-axo", "args="], capture_output=True, text=True, check=True).stdout


def ps_env():
    """The environment every ps call here runs under: `LC_ALL=C` and `TZ=UTC`, since `lstart` text depends on both and
    a start time written under one environment is compared under another."""
    return {**os.environ, "LC_ALL": "C", "TZ": "UTC"}


def started_utc(pid):
    """The start time of <pid> as `ps -o lstart=` prints it under LC_ALL=C TZ=UTC, stripped: the same text whatever
    the caller's locale or zone. A pid ps does not know answers ""; a machine without ps raises FileNotFoundError."""
    return subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)], capture_output=True, text=True,
                          env=tunables.with_values(LC_ALL="C", TZ="UTC")).stdout.strip()


def pids_matching(pattern):
    """The pids `pgrep -f <pattern>` prints, as strings in its order; none when pgrep matches nothing.

    A machine without pgrep raises FileNotFoundError."""
    return subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True).stdout.split()


def commands_of(pids):
    """The `<pid> <command line>` lines `ps -p <pids> -o pid=,command=` prints for those pids, in one call.

    A pid ps does not know is absent from the text; a machine without ps raises FileNotFoundError."""
    return subprocess.run(["ps", "-p", ",".join(pids), "-o", "pid=,command="], capture_output=True, text=True).stdout


def conductors():
    return re.findall(r"^\s*(\d+)\s+(?:\S*(?:python|/sh)\S*\s+)?\S*run_conductor\.py (\d+)(?=\s|$)", listing(), re.M)


def cwd_of(pid):
    lsof = subprocess.run(["lsof", "-a", "-d", "cwd", "-Fn", "-p", pid], stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL, text=True)
    return next((line[1:] for line in lsof.stdout.splitlines() if line.startswith("n")), None)


def is_inside(cwd, root):
    return cwd == root or (cwd or "").startswith(root + "/")


def conductor_processes():
    try:
        root = run_dir.main_tree()
    except run_dir.NoMainTree:
        root = ""
    return [issue for pid, issue in conductors() if is_inside(cwd_of(pid), root)]


def _with_run_directory(root):
    return [(pid, issue) for pid, issue in conductors()
            if os.path.isdir(run_dir.run_file(run_dir.worktree(root, issue), ""))]


def runs_with_directory(root):
    return [issue for _, issue in _with_run_directory(root)]


def starting_runs(root):
    return [issue for pid, issue in _with_run_directory(root) if is_inside(cwd_of(pid), root)]


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
    return run_dir.run_file(path, "conductor.pid")


def recorded_alive(path):
    pid = number_in(_pid_path(path))
    if pid is None or int(pid) == 0:
        return None
    try:
        os.kill(int(pid), 0)
    except (OSError, OverflowError):
        return None
    return pid


def ps_field(field, pid):
    try:
        ps = subprocess.run(["ps", "-o", field + "=", "-p", str(int(pid))], stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True, env=ps_env())
    except OSError:
        return False
    return ps.stdout.strip() if ps.returncode == 0 else None


def ancestors():
    """The pids from this process up to pid 1: this one and each parent `ps` can read."""
    found = set()
    pid = os.getpid()
    while pid > 1 and pid not in found:
        found.add(pid)
        parent = ps_field("ppid", pid)
        pid = int(parent) if parent and parent.isdigit() else 0
    return found


def record(path, pid, atomic=False):
    """Write <pid> on line 1 and its start time on line 2, the form conductor.pid has; returns the text written.

    In place by default (detach-command.sh pins its pid file's inode). <atomic>: the file is replaced by renaming a
    temporary file beside it, so a reader never sees a half-written one and a failed write leaves the old text and
    no temporary file."""
    started = ps_field("lstart", pid)
    text = f"{pid}\n{started}\n" if started else f"{pid}\n"
    if not atomic:
        with open(path, "w") as handle:
            handle.write(text)
        return text
    temporary = "%s.tmp.%d" % (path, os.getpid())
    try:
        with open(temporary, "w") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.remove(temporary)
        except FileNotFoundError:
            pass
        raise
    return text


def _recorded(path):
    if number_in(_pid_path(path)) is None:
        return None, "pid file unreadable"
    pid = recorded_alive(path)
    if pid is None:
        return None, "pid dead"
    if not start_matches(_pid_path(path), pid):
        return None, "lstart mismatch" if ps_field("lstart", pid) else "lstart unreadable"
    return pid, None


def recorded_started(path):
    return _recorded(path)[0]


def start_recorded(file):
    with open(file, "rb") as f:
        f.readline()
        return f.readline().decode().strip()


def same_start(started, pid):
    """Whether <started> is <pid>'s start time: as read now under the pinned environment, or, only when that differs,
    under the caller's own (the text an older snapshot recorded before the read was pinned)."""
    if started == ps_field("lstart", pid):
        return True
    return started == caller_start(pid)


def caller_start(pid):
    """<pid>'s start time as `ps -o lstart=` prints it under the caller's own environment, or None when ps cannot read
    it."""
    try:
        caller = subprocess.run(["ps", "-o", "lstart=", "-p", str(int(pid))], stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, text=True)
    except OSError:
        return None
    return caller.stdout.strip() if caller.returncode == 0 else None


def conductor_alive(start):
    """Whether the conductor a `conductor-start` event names (its `pid` and `started`) is still that process: the pid
    answers kill 0 and its start time is `started` (same_start)."""
    pid = int(start["pid"])
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return bool(start["started"]) and same_start(start["started"], pid)

def start_matches(file, pid):
    started = start_recorded(file)
    return not started or same_start(started, pid)


def _reading(path):
    pid, reason = _recorded(path)
    if pid is None:
        return None, reason
    parent = ps_field("ppid", pid)
    parent_command = ps_field("command", parent) if parent else ""
    if parent_command and "run_conductor.py" not in parent_command:
        return None, "parent command"
    own = ps_field("command", pid)
    if own and "claude" not in (os.path.basename(word) for word in own.split()[:2]):
        return None, "own command"
    return pid, None


def live_conductor(path):
    return _reading(path)[0]


def not_live_reason(path):
    return _reading(path)[1]


def _args(pid):
    ps = subprocess.run(["ps", "-p", pid, "-o", "args="], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return ps.stdout if ps.returncode == 0 else ""


def supervising(pid, name):
    args = _args(pid)
    return f"supervise.sh {name} " in args or f"veri/supervise.py {name} " in args


def detached(pid):
    return _args(pid).startswith("sh -c ")
