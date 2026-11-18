"""preflight-refused.sh's event, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys
from pathlib import Path

import classify_bail
import entry
import event
import event_log
import github
import run_dir
import run_end

USAGE = "usage: preflight-refused.sh <issue-number> <check> [<cause>]\n"
CAUSE = "preflight-refused"


def main_checkout():
    here = Path.cwd()
    return next(d for d in (here, *here.parents) if (d / ".git").is_dir())


def main(argv):
    if len(argv) < 2 or not argv[0] or not argv[1]:
        sys.stderr.write(USAGE)
        return 2
    issue, check = argv[0], argv[1]
    detail = argv[2] if len(argv) > 2 else None
    run = run_dir.worktree(main_checkout(), issue)
    if os.path.isfile(event_log.path(run)) and run_end.run_end(run)[2].get("event") == CAUSE:
        return 3
    code = event.mark(run, {"issue": issue}, CAUSE,
                      ["check=" + check, "cause=" + CAUSE, "classification=" + classify_bail.CATEGORIES[CAUSE],
                       *(["detail=" + detail] if detail is not None else [])])
    try:
        body = "### ⛔ Preflight refused — %s\n" % check
        if detail is not None:
            body += "\n%s\n" % detail
        github.gh_issue_comment(issue, github.published(body))
    except github.NoAnswer:
        return 2
    return code


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
