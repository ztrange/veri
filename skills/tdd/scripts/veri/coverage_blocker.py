"""coverage-blocker.sh's logic: file a coverage issue and block the refactor issue on it."""
import json
import os
import subprocess
import sys
import tempfile

try:
    from github import NoAnswer, gh_issue_view
except ImportError:
    from .github import NoAnswer, gh_issue_view

USAGE = "usage: coverage-blocker.sh <refactor-issue-number>"
ISSUES = "repos/{owner}/{repo}/issues"


def gh(*args, stderr=None):
    return subprocess.run(["gh", *args], stdout=subprocess.PIPE, stderr=stderr, text=True)


def issue(number):
    return "%s/%s" % (ISSUES, number)


def read_body(number):
    try:
        return gh_issue_view(number, "body")
    except NoAnswer:
        return None


def existing(title):
    found = gh("api", ISSUES, "-X", "GET", "-f", "state=open", "-f", "per_page=100")
    try:
        listing = json.loads(found.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(listing, list):
        return None
    for item in listing:
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
        create = gh("api", ISSUES, "-f", "title=" + title, "-f", "body=" + text,
                    "-q", ".html_url")
        if create.returncode != 0:
            return 2
        url = create.stdout.rstrip("\n")
    body = read_body(n)
    if body is None:
        return 2
    fd, tmp = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as f:
            f.write(block(body.rstrip("\n"), url.rsplit("/", 1)[-1]) + "\n")
        edit = gh("api", "-X", "PATCH", issue(n), "-F", "body=@" + tmp)
    finally:
        os.remove(tmp)
    if edit.returncode != 0:
        return 2
    print(url)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
