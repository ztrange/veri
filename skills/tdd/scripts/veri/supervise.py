"""supervise.sh's watchdog, run in-process."""
import os
import re
import subprocess
import sys
import time

USAGE = "usage: supervise.sh <name> <cmd> [args...]"


def refuse(*lines):
    for line in lines:
        print(line, file=sys.stderr)
    return 2


def main(argv):
    if not argv or not argv[0]:
        return refuse(USAGE)
    if len(argv) < 2:
        return refuse("supervise: missing <cmd>", USAGE)
    timeout = os.environ.get("VERI_TIMEOUT", "")
    issue = os.environ.get("VERI_ISSUE", "")
    if not timeout and issue:
        settled = f".tdd/issue-{issue}-timeout"
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, text=True)
        if top.returncode == 0:
            settled = f"{top.stdout.rstrip("\n")}/{settled}"
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
    subprocess.Popen(["/bin/sh", "-c", 'log=$1 rc=$2; shift 2; "$@" >"$log" 2>&1; echo $? >"$rc"',
                      "sh", log, rcfile, *argv[1:]], process_group=0)
    while not os.path.isfile(rcfile):
        time.sleep(0.1)
    with open(rcfile) as f:
        status = "success" if f.read().rstrip("\n") == "0" else "failure"
    ec = 0 if status == "success" else 1
    print(f"supervise[{name}]: {status}", file=sys.stderr)
    sys.stderr.flush()
    with open(log, "rb") as f:
        sys.stdout.buffer.write(f.read())
    sys.stdout.flush()
    with open(exitfile, "w") as f:
        f.write(f"{ec}\n")
    return ec


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
