"""park-issue.sh's work, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys
import tempfile

import blocked_by
import github

USAGE = "usage: park-issue.sh <issue-number> <cause> <unblock> [<pr-number|PR-URL>] [--blocked-by <issue-number>]\n"


def origin_slug():
    url = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True).stdout
    return "/".join(re.split(r"[/:]", url.strip().removesuffix(".git"))[-2:])


def split_blocker(argv):
    """(argv without `--blocked-by <n>`, <n> or None); None for argv when the flag is malformed or repeated."""
    if "--blocked-by" not in argv:
        return argv, None
    at = argv.index("--blocked-by")
    rest = argv[:at] + argv[at + 2:]
    if at + 1 >= len(argv) or "--blocked-by" in rest or not re.fullmatch(r"[1-9][0-9]*", argv[at + 1]):
        return None, None
    return rest, argv[at + 1]


def block_on(number, blocker):
    """List #<blocker> under <number>'s `## Blocked by`, so selection waits on it and it inherits <number>'s band."""
    body = github.gh_issue_view(number, "body").rstrip("\n")
    if int(blocker) in blocked_by.blockers(body, ""):
        return
    fd, tmp = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as f:
            f.write(blocked_by.add(body, blocker) + "\n")
        github.gh_issue_edit(number, tmp)
    finally:
        os.remove(tmp)


def main(argv):
    argv, blocker = split_blocker(argv)
    if argv is None:
        sys.stderr.write("park-issue.sh: --blocked-by takes one issue number, once\n")
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
    if blocker == number:
        sys.stderr.write("park-issue.sh: an issue cannot be blocked by itself\n")
        return 2
    pr = "PR: %s\n" % argv[3] if len(argv) == 4 else ""
    writes = [("Blocked by write", lambda: block_on(number, blocker))] if blocker else []
    writes += [
        ("label", lambda: (github.gh_label_ensure("parked"), github.gh_issue_add_label(number, "parked"),
                           github.gh_issue_remove_label(number, "bailed"))),
        ("comment", lambda: github.gh_issue_comment(number, github.PARKED_HEADING + "\nCause: %s\n%sUnblock: %s\n%s" % (cause, pr, unblock, "Blocked by: #%s\n" % blocker if blocker else ""))),
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
