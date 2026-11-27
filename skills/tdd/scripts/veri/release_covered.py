"""release-covered.sh's work, run in-process: put back on the queue the refactor issue a legacy coverage issue
blocked."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import re
import subprocess
import sys

import github
import release_issue

USAGE = "usage: release-covered.sh <issue-number>\n"
# The title coverage_blocker.py files and deduplicates on: the refactor issue is read from it, never from the
# `## Blocked by` of every open issue, which would also release an issue a human blocked on this one (PRD 031, D6).
TITLE = re.compile(r"Cover the behaviour #([1-9][0-9]*) refactors")


def issue(number):
    """Issue <number>'s REST record; None once gh has given no answer, or one that is not a JSON object (stderr
    written)."""
    run = github.gh_api("repos/{owner}/{repo}/issues/%s" % number, stderr=subprocess.PIPE)
    try:
        record = json.loads(run.stdout) if run.returncode == 0 else None
    except json.JSONDecodeError:
        record = None
    if not isinstance(record, dict):
        sys.stderr.write("release-covered.sh: no answer from gh reading #%s\n" % number)
        return None
    return record


def main(argv):
    if len(argv) != 1 or not re.fullmatch(r"[1-9][0-9]*", argv[0]):
        sys.stderr.write(USAGE)
        return 2
    covering = issue(argv[0])
    if covering is None:
        return 2
    match = TITLE.fullmatch(covering.get("title") or "")
    if not match:
        sys.stderr.write("release-covered.sh: #%s is not a coverage issue a refactor run filed; nothing to release\n"
                         % argv[0])
        return 3
    refactor = match.group(1)
    record = issue(refactor)
    if record is None:
        return 2
    labels = [label.get("name") for label in record.get("labels") or [] if isinstance(label, dict)]
    if record.get("state") != "open" or "bailed" not in labels:
        sys.stderr.write("release-covered.sh: #%s is not an open bailed issue; nothing to release\n" % refactor)
        return 3
    code = release_issue.released(refactor)
    if code == 0:
        print("released #%s" % refactor)
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
