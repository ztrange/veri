"""pointer-comment.sh's logic: the one `### 📍 Run state` comment on an issue, posted when it has none and edited in
place otherwise, saying where the issue's run is."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry
import github

HEADING = "### 📍 Run state"
USAGE = "usage: pointer-comment.sh <issue-number>"


def render(issue):
    return HEADING + "\n"


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
