"""coverage-blocker.sh's logic: file a coverage issue and block the refactor issue on it."""
import json
import os
import sys
import tempfile

try:
    from github import NoAnswer, gh_issue_create, gh_issue_edit, gh_issue_view, gh_rest_list
    from json_documents import documents
except ImportError:
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


def block(body, new):
    blocker = "- #" + new
    lines = []
    last = None
    in_blocked = False
    for line in body.split("\n"):
        if line.startswith("## "):
            in_blocked = line.startswith("## Blocked by")
        if in_blocked and line.startswith("None"):
            lines.append(blocker)
            continue
        if in_blocked and line.startswith("- #"):
            last = len(lines)
        lines.append(line)
    if last is not None:
        lines.insert(last + 1, blocker)
    return "\n".join(lines)


def main(argv):
    if not argv or not argv[0]:
        print(USAGE, file=sys.stderr)
        return 2
    n = argv[0]
    text = ("Refactor #%s refused: its Cover probe found the code it would move uncovered (`COVERED: no`). "
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
    fd, tmp = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as f:
            f.write(block(body.rstrip("\n"), url.rsplit("/", 1)[-1]) + "\n")
        gh_issue_edit(n, tmp)
    except NoAnswer:
        return 2
    finally:
        os.remove(tmp)
    print(url)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
