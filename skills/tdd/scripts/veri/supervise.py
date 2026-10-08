"""supervise.sh's watchdog, run in-process."""
import os
import re
import signal
import subprocess
import sys
import time

from leaf_model import leaf_model
from leaf_role import leaf_role
from pid_file import number_in

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USAGE = "usage: supervise.sh <name> <cmd> [args...]"


def refuse(*lines):
    for line in lines:
        print(line, file=sys.stderr)
    return 2


def write_line(path, value):
    with open(path, "w") as f:
        f.write(f"{value}\n")


def awake_seconds():
    command = os.environ.get("VERI_AWAKE_CLOCK", "")
    if command:
        return int(captured(command).stdout.rstrip("\n"))
    clock = getattr(time, "CLOCK_UPTIME_RAW", time.CLOCK_MONOTONIC)
    return int(time.clock_gettime(clock))


def captured(*args):
    return subprocess.run(list(args), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)


def answered(*args):
    done = captured(*args)
    return done.stdout.rstrip("\n") if done.returncode == 0 else None


def now():
    return captured("date", "+%s").stdout.rstrip("\n")


def mtime_of(path):
    m = answered("stat", "-c", "%Y", path)
    if m is None:
        m = answered("stat", "-f", "%m", path)
    if not re.fullmatch(r"[0-9]+", m or ""):
        m = now()
    return m


class Unbound(Exception):
    pass


def arithmetic(value):
    if re.fullmatch(r"0[0-7]*", value):
        return int(value, 8)
    if re.fullmatch(r"[1-9][0-9]*", value):
        return int(value, 10)
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise Unbound(f"supervise: {value}: unbound variable")
    raise ValueError(f"supervise: {value}: arithmetic syntax error")


def mark(role, *fields):
    if not role:
        return
    subprocess.run(["env", *role.split(), os.path.join(HERE, "event.sh"), *fields])


def main(argv):
    if not argv or not argv[0]:
        return refuse(USAGE)
    if len(argv) < 2:
        return refuse("supervise: missing <cmd>", USAGE)
    timeout = os.environ.get("VERI_TIMEOUT", "")
    issue = os.environ.get("VERI_ISSUE", "")
    if not timeout and issue:
        settled = f".tdd/issue-{issue}-timeout"
        top = answered("git", "rev-parse", "--show-toplevel")
        if top is not None:
            settled = f"{top}/{settled}"
        if os.path.isfile(settled):
            with open(settled) as f:
                timeout = f.read().rstrip("\n")
            if not re.fullmatch(r"[0-9]+", timeout) or int(timeout, 10) < 1:
                return refuse(f"supervise: {settled} must hold a whole number of seconds >= 1: '{timeout}'")
    timeout = timeout or "900"
    kill_poll = os.environ.get("VERI_KILL_POLL") or "0.1"
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", kill_poll):
        return refuse(f"supervise: VERI_KILL_POLL must be a non-negative number: {kill_poll}")
    heartbeat = os.environ.get("VERI_HEARTBEAT") or "180"
    poll = float(os.environ.get("VERI_POLL") or "1")
    name = argv[0]
    os.makedirs(".tdd", exist_ok=True)
    log, rcfile, exitfile = f".tdd/{name}.log", f".tdd/{name}.rc", f".tdd/{name}.exit"
    role = model = ""
    watched = not name.startswith("verdict-")
    if watched:
        found = leaf_role(name)
        if found is not None:
            role = " ".join(f"{k}={v}" for k, v in found.items())
        model = leaf_model(name)
    skill_commit = answered("git", "-C", HERE, "rev-parse", "HEAD") or os.environ.get("VERI_SKILL_COMMIT") or "unknown"
    leaf_env = {**os.environ, "VERI_LEAF_MODEL": model, "VERI_SKILL_COMMIT": skill_commit}
    mark(role, "launch", f"name={name}", f"cmd={' '.join(argv[1:])}", f"model={model}")
    write_line(f".tdd/{name}.pid", os.getpid())
    for stale in (exitfile, rcfile):
        try:
            os.remove(stale)
        except FileNotFoundError:
            pass
    open(log, "wb").close()
    t0 = now()
    a0 = awake_seconds()
    prev_t, prev_a = int(t0), a0
    leaf = subprocess.Popen(["/bin/sh", "-c", 'log=$1 rc=$2; shift 2; "$@" >"$log" 2>&1; echo $? >"$rc"',
                             "sh", log, rcfile, *argv[1:]], process_group=0, env=leaf_env)
    status = reason = ""
    rc = "0"
    seen_at = int(t0)
    if watched:
        last_m = mtime_of(log)
    while True:
        if os.path.isfile(rcfile):
            with open(rcfile) as f:
                rc = f.read().rstrip("\n")
            status = "success" if rc == "0" else "failure"
            break
        t = int(now())
        a = awake_seconds()
        seen_at += (t - prev_t) - (a - prev_a)
        prev_t, prev_a = t, a
        try:
            expired = a - a0 >= arithmetic(timeout)
        except Unbound as unbound:
            print(unbound, file=sys.stderr)
            return 1
        except ValueError as error:
            print(error, file=sys.stderr)
            expired = False
        if expired:
            status, reason = "killed-stuck", f"hard timeout {timeout}s exceeded"
            os.killpg(leaf.pid, signal.SIGTERM)
            break
        if watched:
            m = mtime_of(log)
            if m != last_m:
                last_m, seen_at = m, t
            silence = t - seen_at
            try:
                silent = silence > arithmetic(heartbeat)
            except Unbound as unbound:
                print(unbound, file=sys.stderr)
                return 1
            except ValueError as error:
                print(error, file=sys.stderr)
                silent = False
            if silent:
                status, reason = "killed-stuck", f"no heartbeat for {silence}s (window {heartbeat}s)"
                os.killpg(leaf.pid, signal.SIGTERM)
                break
        time.sleep(poll)
    leaf.wait()
    ec = {"success": 0, "failure": 1, "killed-stuck": 2}[status]
    if rc == "2":
        ec = 2
    secs = awake_seconds() - a0
    if watched:
        sys.stderr.flush()
        subprocess.run([os.path.join(HERE, "harvest-usage.sh"), name], stdout=2)
    print(f"supervise[{name}]: {status}" + (f" — {reason}" if reason else ""), file=sys.stderr)
    sys.stderr.flush()
    mark(role, "exit", f"status={ec}", *([f"cause={reason}"] if reason else []), f"secs={secs}")
    with open(log, "rb") as f:
        sys.stdout.buffer.write(f.read())
    sys.stdout.flush()
    if number_in(exitfile) is None:
        write_line(exitfile, ec)
    return ec


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
