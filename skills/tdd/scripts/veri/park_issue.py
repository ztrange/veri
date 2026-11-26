"""park-issue.sh's work, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys
import tempfile

import blocked_by
import github
import markdown_sections

USAGE = ("usage: park-issue.sh <issue-number> <cause> <unblock> [<pr-number|PR-URL>] [--blocked-by <n>[,<n>…]]"
         " [--question-file <path>]\n")
QUESTION_HEADINGS = ("#### Question", "#### Options", "#### Found", "#### Recommendation")
COMMENT_LIMIT = 65536  # GitHub refuses an issue comment body longer than this many characters
BYTE_LIMIT = 120000  # the body goes to gh as one argument; Linux refuses a single argument over 131,072 bytes


# Room left under both limits: the body is redacted before it is cut, so what is measured is what github.bounded posts;
# redacting it again there replaces nothing more, and these 256 characters (and bytes) absorb any secret a cut join could
# still form, each replacement ([redacted], 10 characters) at most 2 longer than the shortest value it hides (8).
MARGIN = 256


def fits(body):
    return len(body) <= COMMENT_LIMIT - MARGIN and len(body.encode("utf-8")) <= BYTE_LIMIT - MARGIN


def cut_at(head, question, cut):
    """<head> + <question> with <cut> characters taken from the question's middle and a line in their place saying so."""
    marker = ("\n[%d characters of the question file cut here: a comment is kept within %d characters and %d bytes]\n"
              % (cut, COMMENT_LIMIT, BYTE_LIMIT))
    keep = (len(question) - cut) // 2
    return head + question[:keep] + marker + question[len(question) - (len(question) - cut - keep):]


def fit(head, question):
    """<head> + <question>, both as github.published posts them, the question cut in its middle, on a character boundary,
    by the fewest characters that keep the whole MARGIN within COMMENT_LIMIT characters and BYTE_LIMIT UTF-8 bytes: its
    opening (the question) and its end (the recommendation) stay."""
    head, question = github.published(head), github.published(question)
    if fits(head + question):
        return head + question
    low, high = 1, len(question)
    while low < high:
        mid = (low + high) // 2
        low, high = (low, mid) if fits(cut_at(head, question, mid)) else (mid + 1, high)
    return cut_at(head, question, low)


def origin_slug():
    url = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True).stdout
    return "/".join(re.split(r"[/:]", url.strip().removesuffix(".git"))[-2:])


def split_blocker(argv):
    """(argv without `--blocked-by <n>`, <n> or None); None for argv when the flag is malformed or repeated."""
    if "--blocked-by" not in argv:
        return argv, None
    at = argv.index("--blocked-by")
    rest = argv[:at] + argv[at + 2:]
    if at + 1 >= len(argv) or "--blocked-by" in rest or not re.fullmatch(r"[1-9][0-9]*(,[1-9][0-9]*)*", argv[at + 1]):
        return None, None
    return rest, argv[at + 1].split(",")


def block_on(number, blockers):
    """List each of <blockers> under <number>'s `## Blocked by`, so selection waits on them and it inherits <number>'s band."""
    body = github.gh_issue_view(number, "body").rstrip("\n")
    new = [b for b in blockers if int(b) not in blocked_by.blockers(body, "")]
    if not new:
        return
    fd, tmp = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as f:
            for b in new:
                body = blocked_by.add(body, b)
            f.write(body + "\n")
        github.gh_issue_edit(number, tmp)
    finally:
        os.remove(tmp)


def read_question(argv):
    """(argv without `--question-file <path>`, "\\n" + the file's text, or "" without the flag); (None, why) when the
    flag has no path, is repeated, or names a file that cannot be read."""
    if "--question-file" not in argv:
        return argv, ""
    at = argv.index("--question-file")
    rest = argv[:at] + argv[at + 2:]
    if at + 1 >= len(argv) or "--question-file" in rest:
        return None, "--question-file takes one path, once"
    try:
        with open(argv[at + 1], encoding="utf-8") as f:
            return rest, "\n" + f.read()
    except OSError as e:
        return None, "cannot read the --question-file %s: %s" % (argv[at + 1], e.strerror or e)
    except UnicodeDecodeError as e:
        return None, "cannot read the --question-file %s: not UTF-8 text (byte %d: %s)" % (argv[at + 1], e.start, e.reason)


def main(argv):
    argv, question = read_question(argv)
    if argv is None:
        sys.stderr.write("park-issue.sh: %s\n" % question)
        return 2
    unfenced = [line for line, f in zip(question.splitlines(), markdown_sections.fenced_lines(question), strict=True) if not f]
    missing = [h for h in QUESTION_HEADINGS if question and h not in unfenced]
    if missing:
        sys.stderr.write("park-issue.sh: the question file lacks the heading %s\n" % ", ".join(missing))
        return 2
    argv, blocker = split_blocker(argv)
    if argv is None:
        sys.stderr.write("park-issue.sh: --blocked-by takes a comma-separated list <n>[,<n>…]\n")
        sys.stderr.write(USAGE)
        return 2
    if len(argv) not in (3, 4):
        sys.stderr.write("park-issue.sh: too many arguments\n" if len(argv) > 4 else "")
        sys.stderr.write(USAGE)
        return 2
    number, cause, unblock = argv[:3]
    if not number.strip("0") or not number.isascii():
        sys.stderr.write("park-issue.sh: bad issue number %s\n" % number)
        return 2
    for bad, name in ((not number.isdigit(), "issue number"), (not cause, "cause"), (not unblock, "unblock")):
        if bad:
            sys.stderr.write("park-issue.sh: bad %s\n" % name)
            return 2
    pr_url = len(argv) == 4 and re.fullmatch(r"https://github\.com/([^/]+/[^/]+)/pull/[1-9][0-9]*", argv[3])
    if len(argv) == 4 and not (pr_url and origin_slug() == pr_url.group(1) or re.fullmatch(r"[1-9][0-9]*", argv[3])):
        sys.stderr.write(USAGE)
        return 2
    if number in (blocker or []):
        sys.stderr.write("park-issue.sh: an issue cannot be blocked by itself\n")
        return 2
    try:
        labelled = github.gh_label_exists("parked")
    except github.NoAnswer:
        sys.stderr.write("park-issue.sh: no answer from gh reading the parked label\n")
        return 2
    if not labelled:
        sys.stderr.write("park-issue.sh: the repository has no `parked` label: create it (ready-check.sh reports it)\n")
        return 2
    pr = "PR: %s\n" % argv[3] if len(argv) == 4 else ""
    writes = [("Blocked by write", lambda: block_on(number, blocker))] if blocker else []
    writes += [
        ("label", lambda: (github.gh_issue_add_label(number, "parked"),
                           github.gh_issue_remove_label(number, "bailed"))),
        ("comment", lambda: github.gh_issue_comment(number, github.published(fit(github.PARKED_HEADING + "\nCause: %s\n%sUnblock: %s\n%s" % (cause, pr, unblock, "Blocked by: %s\n" % ", ".join("#" + b for b in blocker) if blocker else ""), question)))),
    ]
    if len(argv) == 4:
        writes.append(("PR write", lambda: github.gh_issue_add_label(argv[3].rsplit("/", 1)[-1], "parked")))
    for name, write in writes:
        try:
            write()
        except github.NoAnswer:
            sys.stderr.write("park-issue.sh: no answer from gh to the %s%s\n" % (name, "" if name.endswith("write") else " call"))
            return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
