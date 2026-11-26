"""coverage-blocker.sh's logic: file a coverage issue and block the refactor issue on it."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys
import tempfile

import run_dir
import tunables
from blocked_by import add as block
from blocked_by import blockers
from detect_test_command import resolved
from github import (
    NoAnswer,
    gh_issue_create,
    gh_issue_edit,
    gh_issue_view,
    gh_label_exists,
    gh_rest_list,
)
from json_documents import documents
from ledger import ledger_steps, read_ledger
from ledger_steps import current_or_last_done_record
from report import report_values

USAGE = "usage: coverage-blocker.sh <refactor-issue-number>"
ISSUES = "repos/{owner}/{repo}/issues"


def existing(title):
    try:
        pages = documents(gh_rest_list(ISSUES + "?state=open&per_page=100"))
    except (NoAnswer, json.JSONDecodeError):
        return None
    if not all(isinstance(page, list) for page in pages):
        return None
    for item in (item for page in pages for item in page):
        if item.get("title") == title:
            return item["html_url"]
    return None


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    n = argv[0]
    text = ("## Problem\n\nRefactor #%s refused: its Cover probe found the code it would move uncovered (`COVERED: no`). "
            "Find a seam and surround the behaviour with tests, then #%s can be retaken." % (n, n))
    try:
        with open(".tdd/develop-cover.out") as f:
            report = f.read()
        uncovered = "no" in report_values(report, "COVERED", strip=True)
        mutations = ["MUTATION:" + m for m in report_values(report, "MUTATION", space="kept", strip=True)] if uncovered else []
    except OSError as error:
        print("coverage-blocker.sh: cannot read .tdd/develop-cover.out: %s" % error.strerror, file=sys.stderr)
        return 2
    ledger = run_dir.ledger(".", n)
    try:
        step = current_or_last_done_record(ledger_steps(read_ledger(ledger)))
    except OSError as error:
        print("coverage-blocker.sh: cannot read %s: %s" % (ledger, error.strerror), file=sys.stderr)
        return 2
    if step is None:
        print("coverage-blocker.sh: %s holds no step to name as the region" % ledger, file=sys.stderr)
        return 2
    text += "\n\n## Region\n\n" + step.text
    if mutations:
        text += "\n\n## Acceptance criteria\n\n" + "".join("- [ ] %s: add a case that goes red under this mutation\n" % m for m in mutations)
    text += "\n\n## Blocked by\n\nNone.\n"
    command = resolved("all", "", ".")
    if command is not None:
        text += "\nTest command: %s\n" % command.decode()
    title = "Cover the behaviour #%s refactors" % n
    url = existing(title)
    if url is None:
        label = tunables.get("VERI_LABEL")
        lane = label.rsplit(":", 1)[1] if ":" in label else "main"
        try:
            legacy = ("legacy",) if gh_label_exists("legacy") else ()
            if not legacy:
                print("coverage-blocker: no legacy label; filed as an ordinary issue", file=sys.stderr)
            labels = ((label,) if mutations else ()) + ("filed-by:" + lane,) + legacy
            url = gh_issue_create(title, text, *labels).rstrip("\n")
        except NoAnswer:
            return 2
    try:
        body = gh_issue_view(n, "body")
    except NoAnswer:
        return 2
    new = url.rsplit("/", 1)[-1]
    blocked = block(body.rstrip("\n"), new)
    if not new.isdigit() or int(new) not in blockers(blocked, ""):
        print("coverage-blocker.sh: could not block issue %s on the new coverage issue" % n, file=sys.stderr)
        return 2
    fd, tmp = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as f:
            f.write(blocked + "\n")
        gh_issue_edit(n, tmp)
    except NoAnswer:
        return 2
    finally:
        os.remove(tmp)
    print(url)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
