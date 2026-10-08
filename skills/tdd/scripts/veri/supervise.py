"""supervise.sh's watchdog, run in-process."""
import os
import re
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
    clock = getattr(time, "CLOCK_UPTIME_RAW", time.CLOCK_MONOTONIC)
    return int(time.clock_gettime(clock))


def git_answer(*args):
    done = subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return done.stdout.rstrip("\n") if done.returncode == 0 else None


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
        top = git_answer("rev-parse", "--show-toplevel")
        if top is not None:
            settled = f"{top}/{settled}"
        if os.path.isfile(settled):
            with open(settled) as f:
                timeout = f.read().rstrip("\n")
            if not re.fullmatch(r"[0-9]+", timeout) or int(timeout, 10) < 1:
                return refuse(f"supervise: {settled} must hold a whole number of seconds >= 1: '{timeout}'")
    kill_poll = os.environ.get("VERI_KILL_POLL") or "0.1"
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", kill_poll):
        return refuse(f"supervise: VERI_KILL_POLL must be a non-negative number: {kill_poll}")
    name = argv[0]
    os.makedirs(".tdd", exist_ok=True)
    log, rcfile, exitfile = f".tdd/{name}.log", f".tdd/{name}.rc", f".tdd/{name}.exit"
    role = model = ""
    if not name.startswith("verdict-"):
        found = leaf_role(name)
        if found is not None:
            role = " ".join(f"{k}={v}" for k, v in found.items())
        model = leaf_model(name)
    skill_commit = git_answer("-C", HERE, "rev-parse", "HEAD") or os.environ.get("VERI_SKILL_COMMIT") or "unknown"
    leaf_env = {**os.environ, "VERI_LEAF_MODEL": model, "VERI_SKILL_COMMIT": skill_commit}
    mark(role, "launch", f"name={name}", f"cmd={' '.join(argv[1:])}", f"model={model}")
    write_line(f".tdd/{name}.pid", os.getpid())
    for stale in (exitfile, rcfile):
        try:
            os.remove(stale)
        except FileNotFoundError:
            pass
    open(log, "wb").close()
    a0 = awake_seconds()
    subprocess.Popen(["/bin/sh", "-c", 'log=$1 rc=$2; shift 2; "$@" >"$log" 2>&1; echo $? >"$rc"',
                      "sh", log, rcfile, *argv[1:]], process_group=0, env=leaf_env)
    while not os.path.isfile(rcfile):
        time.sleep(0.1)
    with open(rcfile) as f:
        rc = f.read().rstrip("\n")
    status = "success" if rc == "0" else "failure"
    ec = 0 if status == "success" else 1
    if rc == "2":
        ec = 2
    secs = awake_seconds() - a0
    print(f"supervise[{name}]: {status}", file=sys.stderr)
    sys.stderr.flush()
    mark(role, "exit", f"status={ec}", f"secs={secs}")
    with open(log, "rb") as f:
        sys.stdout.buffer.write(f.read())
    sys.stdout.flush()
    if number_in(exitfile) is None:
        write_line(exitfile, ec)
    return ec


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
