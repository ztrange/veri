"""supervise.sh's watchdog, run in-process."""
import os
import re
import subprocess
import sys

USAGE = "usage: supervise.sh <name> <cmd> [args...]"


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    if len(argv) < 2:
        print("supervise: missing <cmd>", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
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
                print(f"supervise: {settled} must hold a whole number of seconds >= 1: '{timeout}'",
                      file=sys.stderr)
                return 2
    kill_poll = os.environ.get("VERI_KILL_POLL") or "0.1"
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", kill_poll):
        print(f"supervise: VERI_KILL_POLL must be a non-negative number: {kill_poll}", file=sys.stderr)
        return 2
    subprocess.Popen(argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
