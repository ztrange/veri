"""push-branch.sh's logic, run in-process."""
import os
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USAGE = "usage: push-branch.sh [--force-with-lease=<branch>:<sha>]"


def record(*fields):
    return subprocess.run([os.path.join(SCRIPTS, "event.sh"), *fields]).returncode


def main(argv):
    if argv:
        print("push-branch.sh: the only argument is --force-with-lease=<branch>:<sha>, "
              f"got '{' '.join(argv)}'", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    retries = int(os.environ.get("VERI_PUSH_RETRIES", "3"))
    backoff = int(os.environ.get("VERI_PUSH_BACKOFF", "2"))
    attempt = 0
    while attempt <= retries:
        attempt += 1
        pushed = subprocess.run(["git", "push", "--set-upstream", "origin", "HEAD"],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        out = pushed.stdout.rstrip("\n")
        if attempt <= retries:
            subprocess.run(["sleep", str(backoff)])
    print(f"push-branch.sh: push failed after {attempt} attempts; the branch is not on the remote",
          file=sys.stderr)
    return record("push-failed", f"error={out}", f"attempts={attempt}")
