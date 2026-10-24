"""parked-issues.sh's work, run in-process."""
import sys

import github
from json_documents import items

USAGE = "usage: parked-issues.sh"


def field(body, name):
    prefix = name + ": "
    return next(line[len(prefix):] for line in body.splitlines() if line.startswith(prefix))


def main(argv):
    if argv:
        sys.stderr.write(USAGE + "\n")
        return 2
    try:
        listing = github.gh_rest_list("repos/{owner}/{repo}/issues?state=open&labels=parked&per_page=100")
    except github.NoAnswer:
        sys.stderr.write("parked-issues.sh: no answer from gh to listing the issues\n")
        return 2
    issues = items(listing, strict=False)
    if not issues:
        return 3
    for issue in issues:
        number = issue["number"]
        try:
            raw = github.gh_rest_list("repos/{owner}/{repo}/issues/%d/comments?per_page=100" % number)
        except github.NoAnswer:
            sys.stderr.write("parked-issues.sh: no answer from gh to reading the comments of issue #%d\n" % number)
            return 2
        comments = items(raw, strict=False)
        bodies = [c["body"] for c in comments if c["body"].startswith(github.PARKED_HEADING)]
        if not bodies:
            sys.stderr.write("parked-issues.sh: issue #%d has no parked comment\n" % number)
            return 2
        body = bodies[-1]
        sys.stdout.write("%d\t%s\t%s\t%s\n" % (number, issue["title"], field(body, "Cause"), field(body, "Unblock")))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
