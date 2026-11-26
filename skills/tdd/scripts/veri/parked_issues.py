"""parked-issues.sh's work, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import re
import sys

import github
import markdown_sections
from json_documents import documents, items
from park_decision import own_words

USAGE = "usage: parked-issues.sh"


def head(body):
    """The parked comment's field lines: after its heading (and any blank lines right below it), up to the next blank
    line, where park-issue.sh writes them. A line further down (the question --question-file appends) is not a field."""
    lines = body.splitlines()[1:]
    while lines and not lines[0].strip():
        lines.pop(0)
    return lines[:next((i for i, line in enumerate(lines) if not line.strip()), len(lines))]


def field(body, name):
    prefix = name + ": "
    return next((line[len(prefix):] for line in head(body) if line.startswith(prefix)), None)


def open_question(comments):
    """`question` when the newest trusted parked comment among <comments> holds an unfenced `#### Question` line and
    no trusted comment after it is an answer (park-decision.sh's rule: not one of veri's headed comments, and words of
    its own outside quotes and fences), else `-`: a question the human has not answered."""
    trusted = [c for c in comments if github.trusted_comment(c)]
    park = max(i for i, c in enumerate(trusted) if str(c.get("body") or "").startswith(github.PARKED_HEADING))
    if not any(line.rstrip() == "#### Question" for _, line in markdown_sections.unfenced(trusted[park]["body"])):
        return "-"
    answered = any(not body.startswith(github.VERI_COMMENT_PREFIXES) and own_words(body).strip()
                   for body in (str(c.get("body") or "") for c in trusted[park + 1:]))
    return "-" if answered else "question"


def read(fetch, path, what):
    """gh's answer to `path`; None once it has given none (stderr written)."""
    try:
        return fetch(path)
    except github.NoAnswer:
        sys.stderr.write("parked-issues.sh: no answer from gh to %s\n" % what)
        return None


def comment_records(raw):
    """The comment records of a comments listing gh answered; None when the answer is not JSON lists of objects."""
    try:
        pages = documents(raw, strict=False)
    except ValueError:
        return None
    if not all(isinstance(page, list) and all(isinstance(c, dict) for c in page) for page in pages):
        return None
    return [c for page in pages for c in page]


def blockers_status(blocked_by):
    """`ready`, `waiting` or `-`; None once gh has given no answer (stderr written)."""
    if blocked_by is None:
        return "-"
    status = "ready"
    for blocker in re.findall(r"#(\d+)", blocked_by):
        state = read(github.gh_api, "repos/{owner}/{repo}/issues/%s" % blocker, "reading the state of #%s" % blocker)
        if state is None:
            return None
        info = json.loads(state.stdout)
        if info.get("state") != "closed":
            status = "waiting"
        elif "pull_request" in info:
            pull = read(github.gh_api, "repos/{owner}/{repo}/pulls/%s" % blocker, "reading the merged state of #%s" % blocker)
            if pull is None:
                return None
            if not json.loads(pull.stdout).get("merged"):
                status = "waiting"
    return status


def main(argv):
    if argv:
        sys.stderr.write(USAGE + "\n")
        return 2
    listing = read(github.gh_rest_list, "repos/{owner}/{repo}/issues?state=open&labels=parked&per_page=100", "listing the issues")
    if listing is None:
        return 2
    issues = [i for i in items(listing, strict=False) if "pull_request" not in i]
    if not issues:
        return 3
    for issue in issues:
        number = issue["number"]
        raw = read(github.gh_rest_list, "repos/{owner}/{repo}/issues/%d/comments?per_page=100" % number,
                   "reading the comments of issue #%d" % number)
        if raw is None:
            return 2
        comments = comment_records(raw)
        if comments is None:
            sys.stderr.write("parked-issues.sh: no answer from gh to reading the comments of issue #%d\n" % number)
            return 2
        # Only a trusted comment (github.trusted_comment) is the parked record: a stranger's cannot change the answer.
        bodies = [c["body"] for c in comments if github.trusted_comment(c)
                  and str(c.get("body") or "").startswith(github.PARKED_HEADING)]
        if not bodies:
            sys.stderr.write("parked-issues.sh: issue #%d has no parked comment\n" % number)
            return 2
        body = bodies[-1]
        cause, unblock = field(body, "Cause"), field(body, "Unblock")
        if cause is None or unblock is None:
            sys.stderr.write("parked-issues.sh: issue #%d's parked comment lacks its Cause or Unblock line\n" % number)
            return 2
        blocked_by = field(body, "Blocked by")
        status = blockers_status(blocked_by)
        if status is None:
            return 2
        sys.stdout.write("%d\t%s\t%s\t%s\t%s\t%s\n" % (number, issue["title"], cause, unblock, status,
                                                      open_question(comments)))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
