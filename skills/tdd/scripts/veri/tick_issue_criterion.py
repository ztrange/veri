"""tick-issue-criterion.sh's read, tick and write-back, run in-process."""
import os
import sys
import tempfile

import ledger
from github import NoAnswer, gh_issue_edit, gh_issue_view

USAGE = "usage: tick-issue-criterion.sh <issue-number> <matcher>"


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    n = argv[0]
    matcher = argv[1] if len(argv) > 1 else ""
    try:
        body = gh_issue_view(n, "body").rstrip("\n")
    except NoAnswer:
        return 2
    ticked, text = ledger.ledger_tick(body.replace("\0", ""), matcher)
    if not ticked:
        print("tick-issue-criterion: no unchecked criterion matched '%s' on #%s" % (matcher, n),
              file=sys.stderr)
        return 3
    fd, tmp = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        gh_issue_edit(n, tmp)
    except NoAnswer:
        return 2
    finally:
        os.unlink(tmp)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
