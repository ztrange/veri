"""record-answer.sh's work, run in-process: the owner's answer to a question tied to an issue, posted on that issue as
one comment, so it outlives its question file as a decision issue-decisions.sh and park-decision.sh read."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import github
import markdown_sections

USAGE = "usage: record-answer.sh <issue-number> <question-file>\n"


def under(text, heading, level):
    """The text under the first unfenced line that is <heading>, up to the next unfenced heading of <level> `#` or
    fewer, stripped; None when no such line exists."""
    lines = text.splitlines()
    fenced = markdown_sections.fenced_lines(text)
    starts = [i for i, line in enumerate(lines) if not fenced[i] and line.rstrip() == heading]
    if not starts:
        return None
    end = re.compile(r"#{1,%d} " % level)
    body = []
    for line, f in zip(lines[starts[0] + 1:], fenced[starts[0] + 1:]):
        if not f and end.match(line):
            break
        body.append(line)
    return "\n".join(body).strip()


def body_of(text):
    return "Question: %s\n\nOwner's answer: %s" % (under(text, "#### Question", 4), under(text, "## Answer", 2))


def main(argv):
    number, path = argv
    with open(path, encoding="utf-8") as f:
        body = body_of(f.read())
    comments = github.issue_comments(number)
    if any(github.trusted_comment(c) and c["body"].strip() == body.strip() for c in comments):
        sys.stderr.write("record-answer.sh: issue #%s already has this answer\n" % number)
        return 3
    github.gh_comment_post(number, body)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
