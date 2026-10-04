"""tick-issue-criterion.sh's read, tick and write-back, run in-process."""
import os
import subprocess
import sys

from github import gh_issue_view

USAGE = "usage: tick-issue-criterion.sh <issue-number> <matcher>"
SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    n = argv[0]
    matcher = argv[1]
    body = gh_issue_view(n, "body")
    tick = subprocess.run([os.path.join(SCRIPTS, "tick-criterion.sh"), matcher], input=body, text=True)
    if tick.returncode == 3:
        print("tick-issue-criterion: no unchecked criterion matched '%s' on #%s" % (matcher, n),
              file=sys.stderr)
        return 3
    return 0
