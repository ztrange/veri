"""issue-decisions.sh's work, run in-process: the comments on an issue that count as a decision, oldest first, each
marked `owner:` or `judge:`, so a judge reading an issue never takes a stranger's or veri's own comment for one."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import github
from park_decision import own_words

USAGE = "usage: issue-decisions.sh <issue-number>\n"
JUDGE = "Decided:"


def records(number):
    """Issue <number>'s comments, oldest first; None when gh gave no answer or the answer is not comment records with a
    text body (stderr written): an unread answer is never "no decision"."""
    try:
        comments = github.issue_comments(number)
    except github.NoAnswer:
        comments = None
    if not (isinstance(comments, list)
            and all(isinstance(c, dict) and isinstance(c.get("body"), str) for c in comments)):
        sys.stderr.write("issue-decisions.sh: no answer from gh to reading the comments of issue #%s\n" % number)
        return None
    return comments


def decision(comment):
    """`owner: <words>` or `judge: <words>` for a comment that counts as a decision, else None: a trusted comment
    (github.trusted_comment) that is not one of veri's own headed comments, its quoted lines and fences dropped."""
    body = comment["body"]
    if not github.trusted_comment(comment) or body.startswith(github.VERI_COMMENT_PREFIXES):
        return None
    words = own_words(body)
    if not words.strip():
        return None
    return ("judge: " if words.lstrip().startswith(JUDGE) else "owner: ") + words


def main(argv):
    if len(argv) != 1 or not re.fullmatch(r"[1-9][0-9]*", argv[0]):
        sys.stderr.write(USAGE)
        return 2
    number = argv[0]
    comments = records(number)
    if comments is None:
        return 2
    found = [d for d in (decision(c) for c in comments) if d is not None]
    if not found:
        sys.stderr.write("issue-decisions.sh: issue #%s has no decision comment\n" % number)
        return 3
    sys.stdout.write("\n".join(d + "\n" for d in found))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
