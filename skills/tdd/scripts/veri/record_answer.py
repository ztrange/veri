"""record-answer.sh's work, run in-process: the owner's answer to a question tied to an issue, posted on that issue as
one comment, so it outlives its question file as a decision issue-decisions.sh and park-decision.sh read."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import github
import markdown_sections
import run_dir
import run_records

USAGE = "usage: record-answer.sh <issue-number> <question-file>\n"
LIMIT = 2000  # characters of the question kept, and of an answer accepted


def under(text, heading, level):
    """The text under the first unfenced line that is <heading>, up to the next unfenced heading of <level> `#` or
    fewer, stripped; None when no such line exists."""
    lines, unfenced = text.splitlines(), markdown_sections.unfenced(text)
    starts = [i for i, line in unfenced if line.rstrip() == heading]
    if not starts:
        return None
    end = re.compile(r"#{1,%d} " % level)
    stop = next((i for i, line in unfenced if i > starts[0] and end.match(line)), len(lines))
    return "\n".join(lines[starts[0] + 1:stop]).strip()


def read(path):
    """The question file's text; (None, why) when it cannot be read as UTF-8 text."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read(), None
    except OSError as e:
        return None, e.strerror or str(e)
    except UnicodeDecodeError as e:
        return None, "not UTF-8 text (byte %d: %s)" % (e.start, e.reason)


def local(text, anchor):
    """<text> as published: the clone's (the main working tree <anchor>, wherever in it this runs, and the root of the
    worktree this runs in, which a linked worktree may hold outside it) and the temp
    directory's paths `<repo>` and `<tmp>`, the home directory `~`, the
    host names `<host>`, the account name `<user>` and every token `[redacted]`, as run_records carries a run record
    (github redacts tokens again when it posts); None stays None."""
    return None if text is None else run_records.redact_local(
        text, anchor, (run_dir.worktree_root_from_files(),)).strip()


def body_of(text, anchor):
    """(the comment body, None), or (None, why) when the file lacks a heading, its answer is empty or over LIMIT. The
    question is cut at LIMIT characters with `…`: the park comment already holds it whole. Both are measured as
    posted, after `local`, so a cut never leaves part of a path or a name behind."""
    question, answer = (local(under(text, heading, level), anchor)
                        for heading, level in (("#### Question", 4), ("## Answer", 2)))
    if question is None:
        return None, "has no #### Question heading"
    if answer is None:
        return None, "has no ## Answer heading"
    if not answer:
        return None, "has an empty answer"
    if len(answer) > LIMIT:
        return None, "has an answer of %d characters, over %d" % (len(answer), LIMIT)
    if len(question) > LIMIT:
        question = question[:LIMIT] + "…"
    return "Question: %s\n\nOwner's answer: %s" % (question, answer), None


def comments_of(number):
    """Issue <number>'s comments; None when gh gave no answer or the answer is not comment records with a text body."""
    try:
        comments = github.issue_comments(number)
    except github.NoAnswer:
        return None
    if not (isinstance(comments, list)
            and all(isinstance(c, dict) and isinstance(c.get("body"), str) for c in comments)):
        return None
    return comments


def main(argv):
    if len(argv) != 2 or not re.fullmatch(r"[1-9][0-9]*", argv[0]):
        sys.stderr.write(USAGE)
        return 2
    number, path = argv
    text, why = read(path)
    if text is None:
        sys.stderr.write("record-answer.sh: cannot read the question file %s: %s\n" % (path, why))
        return 2
    try:
        anchor = run_dir.main_tree_from_files()
    except OSError as e:
        sys.stderr.write("record-answer.sh: cannot find the clone's main working tree: %s\n" % (e.strerror or e))
        return 2
    body, why = body_of(text, anchor)
    if body is None:
        sys.stderr.write("record-answer.sh: the question file %s %s\n" % (path, why))
        return 2
    comments = comments_of(number)
    if comments is None:
        sys.stderr.write("record-answer.sh: no answer from gh reading the comments of issue #%s\n" % number)
        return 2
    if any(github.trusted_comment(c) and c["body"].strip() == github.published(body).strip() for c in comments):
        sys.stderr.write("record-answer.sh: issue #%s already has this answer\n" % number)
        return 3
    try:
        github.gh_comment_post(number, github.published(body))
    except github.NoAnswer:
        sys.stderr.write("record-answer.sh: no answer from gh posting the answer on issue #%s\n" % number)
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
