"""preflight-refused.sh's event, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys
from pathlib import Path

import classify_bail
import entry
import event
import github
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
    detail = argv[2] if len(argv) > 2 and argv[2].strip() else None
    run = os.path.join(main_checkout(), ".tdd", "wt", issue)
    log = os.path.join(run, ".tdd", "events.jsonl")
    if os.path.isfile(log) and run_end.run_end(run)[2].get("event") == CAUSE:
        return 3
    code = event.mark(run, {"issue": issue}, CAUSE,
                      ["check=" + check, "cause=" + CAUSE, "classification=" + classify_bail.CATEGORIES[CAUSE],
                       *(["detail=" + detail] if detail is not None else [])])
    try:
        body = "### ⛔ Preflight refused — %s\n" % check
        if detail is not None:
            body += "\n%s\n" % detail
        github.gh_issue_comment(issue, body)
    except github.NoAnswer:
        return 2
    return code


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
