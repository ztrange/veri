"""stack-land.sh's logic, run in-process: lands the stack's tested cut on the default branch (PRD 034.4a)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import re
import subprocess
import sys

import entry
import event
import git
import github
import pid_file
import stack_branch
import stack_fix
import tunables

USAGE = "usage: stack-land.sh [--now]"


def _pulls_onto(stack):
    """The urls of the open pull requests whose base is <stack>, kept only when the answer itself names <stack> as the
    base ref and the pull request's head is in this repository (Pull.cross_repository): a fork's, which anyone can open,
    keeps nothing live."""
    run = github.gh_api("repos/{owner}/{repo}/pulls?state=open&base=%s&per_page=100" % stack, stderr=subprocess.PIPE)
    raws = json.loads(run.stdout)
    return [pr.html_url for raw, pr in zip(raws, github.pulls_in(run.stdout))
            if (raw.get("base") or {}).get("ref") == stack and not pr.cross_repository]


def _living_conductors():
    """The runs (`#<n>`) whose journal's last conductor-start names a living conductor, as status.sh's Running section
    reads them."""
    lives = []
    for path, events in event.journals("stack-land.sh"):
        starts = [e for e in events if e.get("event") == "conductor-start"]
        if starts and pid_file.conductor_alive(starts[-1]):
            lives.append(event.run_name(path))
    return lives


def _live(stack):
    """What keeps <stack> live, said in a few words: the open pull requests onto it, else the living conductors; None
    when it is idle."""
    pulls = _pulls_onto(stack)
    if pulls:
        return "open pull requests onto %s: %s" % (stack, " ".join(pulls))
    conductors = _living_conductors()
    return "living conductors: %s" % " ".join(conductors) if conductors else None


def _closes(stack, default, cut):
    """The slice body's `Closes #<n>` lines: one per issue a subject in origin/<default>..<cut> ends with `(#<n>)` for,
    in the range's order, kept only when a pull request merged into <stack> carries `Closes #<n>`; an issue named only by
    subjects is said on stderr."""
    joined = _read("reading the pull requests merged into %s" % stack, github.joined_issues, stack)
    span = "origin/%s..%s" % (default, cut)
    named = re.findall(r"\(#(\d+)\)$", _read("git log of " + span, git.out, "log", "--format=%s", span), re.M)
    issues = list(dict.fromkeys(named))
    only = [n for n in issues if int(n) not in joined]
    if only:
        print("stack-land: issues named only by commit subjects in origin/%s..%s, given no Closes line: %s"
              % (default, cut, " ".join("#" + n for n in only)), file=sys.stderr)
    return "".join("Closes #%s\n" % n for n in issues if int(n) in joined)


class _Unanswered(Exception):
    """A read after the merge lock was taken got no answer; the message names the read."""


def _read(what, call, *args):
    """<call>(*<args>)'s answer; _Unanswered naming <what> when GitHub gave none (NoAnswer, or an answer that is not
    JSON) or git failed."""
    try:
        return call(*args)
    except (github.NoAnswer, ValueError, git.GitFailed) as failed:
        detail = failed.detail if isinstance(failed, github.NoAnswer) else str(failed)
        raise _Unanswered("%s got no answer: %s" % (what, " ".join(detail.split()))) from None


def _freed(line):
    """Free the merge lock this process holds, then refuse with <line> (exit 2)."""
    stack_fix.script("merge-lock.sh", "release", "--pid", str(os.getpid()))
    return entry.refuse(line, prefix="stack-land: ")


def main(argv):
    if argv not in ([], ["--now"]):
        return entry.refuse(usage=USAGE)
    size = tunables.get("VERI_SLICE_COMMITS")
    if not (size.isascii() and size.isdigit() and int(size) >= 1):
        return entry.refuse("VERI_SLICE_COMMITS must be a whole number of 1 or more: %r" % size, prefix="stack-land: ")
    try:
        stack = stack_branch.named(".")
    except stack_branch.Refused as refused:
        return entry.refuse("stack-branch.sh exits 2: %s" % refused, prefix="stack-land: ")
    if stack is None:
        return entry.refuse("stack-branch.sh exits 3: the repository's CLAUDE.md names no stack branch",
                            prefix="stack-land: ")
    code, said = stack_fix.script("stack-red.sh", limit=stack_fix.NETWORK)
    if code == 0:
        red, url = (said.split() + ["", ""])[:2]
        print("stack-land: the stack is red: CI failed on %s (%s); nothing cut or merged" % (red, url), file=sys.stderr)
        return 1
    if code == 2:
        return entry.refuse("stack-red.sh exits 2: no answer on the stack's CI; nothing cut or merged",
                            prefix="stack-land: ")
    code, said = stack_fix.script("stack-green.sh", limit=stack_fix.NETWORK)
    if code == 3:
        print("stack-land: stack-green.sh exits 3: no tested issue end to cut at; nothing to land", file=sys.stderr)
        return 3
    if code == 2:
        return entry.refuse("stack-green.sh exits 2: no answer on the stack's tested cut; nothing cut or merged",
                            prefix="stack-land: ")
    cut = said.split()[0]
    default = git.default_branch(cwd=".")
    ahead = int(git.out("rev-list", "--count", "origin/%s..%s" % (default, cut)))
    if argv != ["--now"] and ahead < int(size):
        live = _live(stack)
        if live:
            print("stack-land: the cut %s is %d commits ahead of origin/%s, fewer than VERI_SLICE_COMMITS (%s), and the"
                  " stack is live: %s; nothing landed" % (cut, ahead, default, size, live), file=sys.stderr)
            return 3
    code, _ = stack_fix.script("merge-lock.sh", "take", "--pid", str(os.getpid()))
    if code != 0:
        return entry.refuse("merge-lock.sh take exits %d: the merge lock not taken; nothing fetched, pushed or opened"
                            % code, prefix="stack-land: ")
    try:
        fetch = git.network("fetch", "--prune", "origin", cwd=".")
        if fetch.returncode:
            return _freed("git fetch origin failed (exit %d): %s; the merge lock freed, nothing pushed or opened"
                          % (fetch.returncode, fetch.stderr.strip()))
        slice_branch = "%s-slice-%s" % (stack, cut[:10])
        listed = git.network("ls-remote", "--heads", "origin", "refs/heads/%s" % slice_branch, cwd=".").stdout.split()
        if listed and listed[0] != cut:
            return _freed("the slice branch %s is already on origin at another commit, %s; the merge lock freed,"
                          " nothing pushed" % (slice_branch, listed[0]))
        push = git.network("push", "origin", "%s:refs/heads/%s" % (cut, slice_branch), cwd=".")
        if push.returncode:
            return _freed("git push of the slice branch %s failed (exit %d): %s; the merge lock freed, nothing opened"
                          " or merged" % (slice_branch, push.returncode, push.stderr.strip()))
        if not _read("listing the open pull requests from " + slice_branch, github.stack_pulls, slice_branch, default):
            _read("opening the pull request from %s to %s" % (slice_branch, default), github.pr_open, slice_branch,
                  default, "Land %s at %s" % (stack, cut[:10]), _closes(stack, default, cut))
    except _Unanswered as unanswered:
        return _freed("%s; the merge lock freed, nothing merged" % unanswered)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
