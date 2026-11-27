"""release-issue.sh's work, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import event
import github
import run_dir
import run_records
import tunables

USAGE = "usage: release-issue.sh <issue-number>\n"
MARKERS = ("parked", "bailed")


def _preflight_refused(number, labels, opt_in):
    """Whether the issue is preflight-refused: claimed, not opted in, and bearing veri's own refusal comment, one
    github.trusted_comment trusts (a running issue carries the same labels, so a stranger's comment cannot count)
    and the heading starts. None when the comments cannot be read (no answer, or an answer that is not a list)."""
    if opt_in in labels or not any(name.startswith("taken:") for name in labels):
        return False
    try:
        comments = github.issue_comments(number)
    except (github.NoAnswer, ValueError):
        return None
    if not isinstance(comments, list):
        return None
    return any(github.trusted_comment(c) and (c.get("body") or "").startswith("### ⛔ Preflight refused")
               for c in comments)


def accept_unwired(run, number):
    """The files an `unwired` bail recorded as pending become accepted: appended to the run's accepted record, which
    `unwired.sh --accepted` reads, and the pending record removed. Only a successful release calls it."""
    pending = run_dir.issue_file(run, number, "-unwired-pending")
    if not os.path.isfile(pending):
        return
    with open(pending, errors="surrogateescape") as listed:
        files = listed.read()
    with open(run_dir.issue_file(run, number, "-unwired-accepted"), "a", errors="surrogateescape") as accepted:
        accepted.write(files)
    os.unlink(pending)


def main(argv):
    if len(argv) != 1 or not re.fullmatch(r"[1-9][0-9]*", argv[0]):
        sys.stderr.write(USAGE)
        return 2
    return released(argv[0])


def released(number):
    """release(<number>) run as stage `release` carrying the issue: the exit code release-issue.sh <number> gives."""
    return event.stage("release", lambda: release(number), "",
                       event.context(tunables.with_values(VERI_ISSUE=number)))


def release(number):
    opt_in = tunables.get("VERI_LABEL")
    taken = tunables.taken_label(opt_in)
    try:
        labels = github.gh_issue_view(number, "labels").split("\n")
    except github.NoAnswer:
        sys.stderr.write("release-issue.sh: no answer from gh reading the labels of #%s\n" % number)
        return 2
    marked = any(marker in labels for marker in MARKERS)
    refused = False if marked else _preflight_refused(number, labels, opt_in)
    if refused is None:
        sys.stderr.write("release-issue.sh: no answer from gh reading the comments of #%s\n" % number)
        return 2
    if not marked and not refused:
        sys.stderr.write(
            "release-issue.sh: #%s is neither parked, bailed nor preflight-refused; nothing to release\n" % number)
        return 3
    foreign = [name for name in labels if name.startswith("taken:") and name != taken]
    if foreign:
        sys.stderr.write("release-issue.sh: #%s carries %s, another lane's claim; not released\n"
                         % (number, ", ".join(foreign)))
        return 2
    # The marker comes off last: a write that gets no answer leaves the issue parked or bailed, so a
    # re-run finds it again, and every earlier write is safe to repeat.
    def add_opt_in():
        return github.gh_issue_add_label(number, opt_in)
    def remove_claim():
        return github.gh_issue_remove_label(number, taken)
    writes = [lambda: github.gh_label_ensure(opt_in)]
    writes += [add_opt_in, remove_claim] if marked else [remove_claim, add_opt_in]
    writes +=[lambda marker=marker: github.gh_issue_remove_label(number, marker) for marker in MARKERS]
    for write in writes:
        try:
            write()
        except github.NoAnswer:
            sys.stderr.write("release-issue.sh: no answer from gh releasing #%s; re-run it\n" % number)
            return 2
    open(run_dir.issue_file(event.toplevel(), number, "-released"), "w").close()
    accept_unwired(run_dir.worktree(run_dir.main_tree_from_files(), number), number)
    # A released run's carried pin must not be honoured on another machine: its records go with the claim.
    failed = run_records.delete(number, event.toplevel() or ".")
    if failed:
        sys.stderr.write("release-issue.sh: %s not deleted on origin: %s\n" % (run_records.ref(number), failed))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
