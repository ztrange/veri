"""parked-issues.sh's work, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import re
import sys

import github
from json_documents import items

USAGE = "usage: parked-issues.sh"


def field(body, name):
    prefix = name + ": "
    return next((line[len(prefix):] for line in body.splitlines() if line.startswith(prefix)), None)


def read(fetch, path, what):
    """gh's answer to `path`; None once it has given none (stderr written)."""
    try:
        return fetch(path)
    except github.NoAnswer:
        sys.stderr.write("parked-issues.sh: no answer from gh to %s\n" % what)
        return None


def blockers_status(blocked_by):
    """`ready`, `waiting` or `-`; None once gh has given no answer (stderr written)."""
    if blocked_by is None:
        return "-"
    status = "ready"
    for blocker in re.findall(r"#(\d+)", blocked_by):
        state = read(github.gh_api, "repos/{owner}/{repo}/issues/%s" % blocker, "reading the state of #%s" % blocker)
        if state is None:
            return None
        info = json.loads(state)
        if info.get("state") != "closed":
            status = "waiting"
        elif "pull_request" in info:
            pull = read(github.gh_api, "repos/{owner}/{repo}/pulls/%s" % blocker, "reading the merged state of #%s" % blocker)
            if pull is None:
                return None
            if not json.loads(pull).get("merged"):
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
        comments = items(raw, strict=False)
        bodies = [c["body"] for c in comments if c["body"].startswith(github.PARKED_HEADING)]
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
        sys.stdout.write("%d\t%s\t%s\t%s\t%s\n" % (number, issue["title"], cause, unblock, status))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
