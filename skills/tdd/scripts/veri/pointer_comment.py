"""pointer-comment.sh's logic: the one `### 📍 Run state` comment on an issue, posted when it has none and edited in
place otherwise, saying where the issue's run is."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry
import git
import github

HEADING = "### 📍 Run state"
USAGE = "usage: pointer-comment.sh <issue-number>"


def branch():
    try:
        return git.out("rev-parse", "--abbrev-ref", "HEAD") or "none"
    except git.GitFailed:
        return "none"


def pr_url(name):
    if name == "none":
        return "none"
    pulls = github.rest_items("repos/{owner}/{repo}/pulls?state=all&per_page=100&head={owner}:%s" % name)
    return next((p.get("html_url") or p.get("url") for p in pulls if (p.get("head") or {}).get("ref") == name), "none")


def render(issue):
    name = branch()
    return "\n".join([
        HEADING,
        "",
        "Branch: %s" % name,
        "PR: %s" % pr_url(name),
        "Resume: $S/run-conductor.sh %s" % issue,
    ]) + "\n"


def write(issue):
    body = render(issue)
    held = [c for c in github.issue_comments(issue) if (c.get("body") or "").startswith(HEADING)]
    if held:
        github.gh_comment_edit(held[0]["id"], body)
    else:
        github.gh_comment_post(issue, body)
    return 0


def main(argv):
    if len(argv) != 1 or not argv[0].isdecimal():
        return entry.refuse(usage=USAGE)
    return write(argv[0])


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
