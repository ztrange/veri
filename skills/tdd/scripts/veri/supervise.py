"""supervise.sh's watchdog, run in-process."""
import os
import re
import subprocess
import sys

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
    subprocess.Popen(argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
