"""tick-issue-criterion.sh's read, tick and write-back, run in-process."""
import os
import subprocess
import sys
import tempfile

from github import gh_issue_edit, gh_issue_view

USAGE = "usage: tick-issue-criterion.sh <issue-number> <matcher>"
SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    n = argv[0]
    matcher = argv[1] if len(argv) > 1 else ""
    body = gh_issue_view(n, "body").rstrip("\n")
    tick = subprocess.run([os.path.join(SCRIPTS, "tick-criterion.sh"), matcher], input=body,
                          stdout=subprocess.PIPE, text=True)
    if tick.returncode == 3:
        print("tick-issue-criterion: no unchecked criterion matched '%s' on #%s" % (matcher, n),
              file=sys.stderr)
        return 3
    fd, tmp = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as f:
            f.write(tick.stdout)
        gh_issue_edit(n, tmp)
    finally:
        os.unlink(tmp)
    return 0
