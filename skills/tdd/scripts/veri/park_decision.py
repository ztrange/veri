"""park-decision.sh's work, run in-process: the owner's answer to a park, read from the issue's comments."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import github
import markdown_sections

USAGE = "usage: park-decision.sh <issue-number>\n"


def own_words(body):
    """<body> without its quoted lines (`>`) and its code fences, stripped; "" when nothing else is left. A quote or a
    fence holds someone else's words (the park's own question, a leaf's output), never the decision."""
    fenced = markdown_sections.fenced_lines(body)
    lines = [line for line, f in zip(body.splitlines(), fenced) if not f and not line.lstrip().startswith(">")]
    return "\n".join(lines).strip("\n")


def main(argv):
    number = argv[0]
    comments = [c for c in github.issue_comments(number) if github.trusted_comment(c)]
    parks = [i for i, c in enumerate(comments) if c["body"].startswith(github.PARKED_HEADING)]
    if not parks:
        sys.stderr.write("park-decision.sh: issue #%s has no parked comment\n" % number)
        return 3
    after = [words for words in (own_words(c["body"]) for c in comments[parks[-1] + 1:]) if words.strip()]
    if not after:
        sys.stderr.write("park-decision.sh: issue #%s has no trusted comment after its newest parked comment\n" % number)
        return 3
    sys.stdout.write("\n".join(words + "\n" for words in after))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
