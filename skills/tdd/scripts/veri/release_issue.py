"""release-issue.sh's work, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import github
import tunables

USAGE = "usage: release-issue.sh <issue-number>\n"
MARKERS = ("parked", "bailed")


def _preflight_refused(number, labels, opt_in):
    if opt_in in labels or not any(name.startswith("taken:") for name in labels):
        return False
    try:
        return "### ⛔ Preflight refused" in github.gh_issue_view(number, "comments")
    except github.NoAnswer:
        return False


def main(argv):
    if len(argv) != 1 or not re.fullmatch(r"[1-9][0-9]*", argv[0]):
        sys.stderr.write(USAGE)
        return 2
    number = argv[0]
    opt_in = tunables.read("VERI_LABEL", "ready-for-agent")
    taken = tunables.taken_label(opt_in)
    try:
        labels = github.gh_issue_view(number, "labels").split("\n")
    except github.NoAnswer:
        sys.stderr.write("release-issue.sh: no answer from gh reading the labels of #%s\n" % number)
        return 2
    marked = any(marker in labels for marker in MARKERS)
    if not marked and not _preflight_refused(number, labels, opt_in):
        sys.stderr.write("release-issue.sh: #%s is neither parked nor bailed; nothing to release\n" % number)
        return 3
    foreign = [name for name in labels if name.startswith("taken:") and name != taken]
    if foreign:
        sys.stderr.write("release-issue.sh: #%s carries %s, another lane's claim; not released\n" % (number, ", ".join(foreign)))
        return 2
    # The marker comes off last: a write that gets no answer leaves the issue parked or bailed, so a
    # re-run finds it again, and every earlier write is safe to repeat.
    writes = [
        lambda: github.gh_label_ensure(opt_in),
        lambda: github.gh_issue_add_label(number, opt_in),
        lambda: github.gh_issue_remove_label(number, taken),
    ]
    if not marked:
        writes[1:3] = writes[2:0:-1]
    writes += [lambda marker=marker: github.gh_issue_remove_label(number, marker) for marker in MARKERS]
    for write in writes:
        try:
            write()
        except github.NoAnswer:
            sys.stderr.write("release-issue.sh: no answer from gh releasing #%s; re-run it\n" % number)
            return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
