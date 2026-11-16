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


def fit(head, question):
    """<head> + <question>, the question cut in its middle when the whole would pass COMMENT_LIMIT, a line in place of
    the cut saying how many characters it removed: its opening (the question) and its end (the recommendation) stay."""
    if len(head) + len(question) <= COMMENT_LIMIT:
        return head + question
    cut = len(head) + len(question) - COMMENT_LIMIT
    while True:
        marker = ("\n[%d characters of the question file cut here: GitHub refuses a comment over %d characters]\n"
                  % (cut, COMMENT_LIMIT))
        if len(head) + len(question) - cut + len(marker) <= COMMENT_LIMIT:
            break
        cut += 1
    keep = (len(question) - cut) // 2
    return head + question[:keep] + marker + question[len(question) - (len(question) - cut - keep):]


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
    unfenced = [line for line, f in zip(question.splitlines(), markdown_sections.fenced_lines(question)) if not f]
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
    pr = "PR: %s\n" % argv[3] if len(argv) == 4 else ""
    writes = [("Blocked by write", lambda: block_on(number, blocker))] if blocker else []
    writes += [
        ("label", lambda: (github.gh_label_ensure("parked"), github.gh_issue_add_label(number, "parked"),
                           github.gh_issue_remove_label(number, "bailed"))),
        ("comment", lambda: github.gh_issue_comment(number, fit(github.PARKED_HEADING + "\nCause: %s\n%sUnblock: %s\n%s" % (cause, pr, unblock, "Blocked by: %s\n" % ", ".join("#" + b for b in blocker) if blocker else ""), question))),
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
