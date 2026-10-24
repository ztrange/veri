"""parked-issues.sh's work, run in-process."""
import json
import sys

import github

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
    issues = json.loads(listing or "[]")
    if not issues:
        return 3
    for issue in issues:
        number = issue["number"]
        comments = json.loads(github.gh_rest_list("repos/{owner}/{repo}/issues/%d/comments?per_page=100" % number), strict=False)
        body = [c["body"] for c in comments if c["body"].startswith("### ⏸ Parked")][-1]
        sys.stdout.write("%d\t%s\t%s\t%s\n" % (number, issue["title"], field(body, "Cause"), field(body, "Unblock")))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
