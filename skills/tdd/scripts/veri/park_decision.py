"""park-decision.sh's work, run in-process: the owner's answer to a park, read from the issue's comments."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import github
import markdown_sections

USAGE = "usage: park-decision.sh <issue-number>\n"


def own_words(body):
    """<body> without its quoted lines (`>`) and its code fences, stripped; "" when nothing else is left. A quote or a
    fence holds someone else's words (the park's own question, a leaf's output), never the decision."""
    fenced = markdown_sections.fenced_lines(body)
    lines = [line for line, f in zip(body.splitlines(), fenced, strict=True) if not f and not line.lstrip().startswith(">")]
    return "\n".join(lines).strip("\n")


def records(number):
    """Issue <number>'s comments, oldest first; None when gh gave no answer or the answer is not comment records with a
    text body (stderr written): an unread answer is never "no decision"."""
    try:
        comments = github.issue_comments(number)
    except github.NoAnswer:
        comments = None
    if not (isinstance(comments, list) and all(isinstance(c, dict) and isinstance(c.get("body"), str) for c in comments)):
        sys.stderr.write("park-decision.sh: no answer from gh to reading the comments of issue #%s\n" % number)
        return None
    return comments


def main(argv):
    if len(argv) != 1 or not re.fullmatch(r"[1-9][0-9]*", argv[0]):
        sys.stderr.write(USAGE)
        return 2
    number = argv[0]
    comments = records(number)
    if comments is None:
        return 2
    comments = [c for c in comments if github.trusted_comment(c)]
    parks = [i for i, c in enumerate(comments) if c["body"].startswith(github.PARKED_HEADING)]
    if not parks:
        sys.stderr.write("park-decision.sh: issue #%s has no parked comment\n" % number)
        return 3
    answers = [c["body"] for c in comments[parks[-1] + 1:] if not c["body"].startswith(github.VERI_COMMENT_PREFIXES)]
    after = [words for words in (own_words(body) for body in answers) if words.strip()]
    if not after:
        sys.stderr.write("park-decision.sh: issue #%s has no trusted comment after its newest parked comment\n" % number)
        return 3
    sys.stdout.write("\n".join(words + "\n" for words in after))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
