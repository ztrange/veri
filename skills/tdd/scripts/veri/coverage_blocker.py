"""coverage-blocker.sh's logic: file a coverage issue and block the refactor issue on it."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import sys
import tempfile

try:
    from blocked_by import add as block, blockers
    from github import NoAnswer, gh_issue_create, gh_issue_edit, gh_issue_view, gh_rest_list
    from json_documents import documents
except ImportError:
    from .blocked_by import add as block, blockers
    from .github import NoAnswer, gh_issue_create, gh_issue_edit, gh_issue_view, gh_rest_list
    from .json_documents import documents

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
    title = "Cover the behaviour #%s refactors" % n
    url = existing(title)
    if url is None:
        try:
            url = gh_issue_create(title, text).rstrip("\n")
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
