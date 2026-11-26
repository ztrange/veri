"""stack-recover.sh's logic, run in-process: once a GitHub outage ends, pushes each offline join's commit to its run's
branch and then the stack, so each joined draft pull request reads merged (PRD 033.3)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import os
import re
import subprocess
import sys

import entry
import git
import github
import merge_common
import run_dir
import run_records
import stack_branch
import stack_fix

USAGE = "usage: stack-recover.sh"
# The trailer an offline join leaves on the stack commit it made: the run's pull request url and its branch.
TRAILER = re.compile(r"(https://[^/\s]+/[^\s]+/pull/\d+) (\S+)")
# A push refused because origin's ref is not what the lease expected.
LEASE = re.compile(r"stale info|\[rejected\]")
# A pull request url a TRAILER matched: its repository and its number.
PULL = re.compile(r"https://[^/]+/(.+)/pull/(\d+)")


def _refuse(line):
    """Say <line> on stderr, behind this script's prefix: no answer (exit 2)."""
    return entry.refuse(line, prefix="stack-recover: ")


def _rev(ref):
    """The commit <ref> names, or None when it names none."""
    try:
        return git.out("rev-parse", "--verify", "--quiet", ref, cwd=".")
    except git.GitFailed:
        return None


def _ancestor(older, newer):
    """Whether commit <older> is <newer> or one of its ancestors."""
    return git.ok("merge-base", "--is-ancestor", older, newer, cwd=".")


class _Garbled(Exception):
    """A commit's Veri-Joined trailer is not `<pull request url> <branch>`; the message names the commit."""


def _joins(stack):
    """The offline joins of origin/<stack>..<stack>, oldest first: (commit, pull request url, branch) for each commit
    carrying a Veri-Joined trailer; a commit without one is a stack commit of its own and skipped. _Garbled naming the
    first commit whose trailer is anything else; git.GitFailed when git cannot read the range."""
    joins = []
    for sha in git.out("log", "--reverse", "--format=%H", "origin/%s..%s" % (stack, stack), cwd=".").split():
        said = git.out("show", "-s", "--format=%(trailers:key=Veri-Joined,valueonly,unfold)", sha, cwd=".")
        lines = [line.strip() for line in said.splitlines() if line.strip()]
        if not lines:
            continue
        found = TRAILER.fullmatch(lines[0]) if len(lines) == 1 else None
        if not found:
            raise _Garbled("the commit %s carries a Veri-Joined trailer that is not '<pull request url> <branch>': %r"
                           % (sha, " | ".join(lines)[:200]))
        joins.append((sha, found[1], found[2]))
    return joins


def _pull(pr):
    """GitHub's record of the pull request <pr>, read as stack-land.sh reads it; None when GitHub gave no answer or the
    answer is not a JSON object, so the settle window reads again."""
    repo, number = PULL.fullmatch(pr).groups()
    try:
        pull = json.loads(github.gh_api("repos/%s/pulls/%s" % (repo, number), stderr=subprocess.PIPE).stdout)
    except (github.NoAnswer, ValueError):
        return None
    return pull if isinstance(pull, dict) else None


def _leased(sha, branch, lease, kept):
    """Push <sha> to origin's <branch> under a lease on <lease>, its sha as fetched ("" for none): None once pushed, else
    the exit code, said on stderr with <kept>: 1 for a refused lease, 2 for any other failure."""
    push = git.network("push", "--force-with-lease=%s:%s" % (branch, lease), "origin",
                       "%s:refs/heads/%s" % (sha, branch), cwd=".")
    said = " ".join((push.stderr or "").split())
    if push.returncode and LEASE.search(said):
        print("stack-recover: the leased push of %s to %s was refused: origin's %s is not %s as fetched (%s); %s"
              % (sha, branch, branch, lease or "absent", said, kept), file=sys.stderr)
        return 1
    if push.returncode:
        return _refuse("the push of %s to %s failed (exit %d): %s; %s" % (sha, branch, push.returncode, said, kept))
    return None


def _held(stack, window):
    """The pushes of <stack>'s offline joins and of <stack>, with the merge lock held, never releasing it: an exit code
    when they stop short, else (the stack's pushed tip, the joins) once every joined pull request reads merged."""
    fetch = git.network("fetch", "--prune", "origin", cwd=".")
    if fetch.returncode:
        return _refuse("git fetch origin failed (exit %d): %s; nothing pushed" % (
            fetch.returncode, " ".join(fetch.stderr.split())))
    local, fetched = _rev("refs/heads/" + stack), _rev("refs/remotes/origin/" + stack)
    if local is None or (fetched and _ancestor(local, fetched)):
        print("stack-recover: the local %s is absent, at origin/%s or behind it: nothing joined offline, nothing to"
              " push" % (stack, stack), file=sys.stderr)
        return 3
    if fetched is None:
        print("stack-recover: origin/%s is gone after the fetch, while the local %s is at %s: the stack moved on GitHub,"
              " so what to push is the human's call; nothing pushed" % (stack, stack, local), file=sys.stderr)
        return 1
    if not _ancestor(fetched, local):
        print("stack-recover: origin/%s at %s is not an ancestor of the local %s at %s: the stack moved on GitHub, and"
              " rebasing it is the human's call; nothing pushed" % (stack, fetched, stack, local), file=sys.stderr)
        return 1
    try:
        joins = _joins(stack)
    except _Garbled as garbled:
        print("stack-recover: %s; nothing pushed" % garbled, file=sys.stderr)
        return 1
    except git.GitFailed as failed:
        return _refuse("reading origin/%s..%s failed: %s; nothing pushed" % (stack, stack, " ".join(str(failed).split())))
    # Each lease is origin's branch as fetched, read before anything is pushed.
    leases = [_rev("refs/remotes/origin/" + branch) or "" for _, _, branch in joins]
    for (sha, _, branch), lease in zip(joins, leases, strict=True):
        code = _leased(sha, branch, lease, "the stack not pushed")
        if code:
            return code
    # A compare-and-swap, never --force: the lease is origin's stack as fetched, and the local stack descends from it.
    code = _leased(local, stack, fetched, "the joined branches are pushed")
    if code:
        return code
    for _, pr, _ in joins:
        answers = merge_common.settle(lambda: _pull(pr), window)
        if not merge_common.merged(answers[-1]):
            last = answers[-1] or {}
            return _refuse("%s did not read merged by the end of the settle window (last read: state %s, merged %s);"
                           " the stack left as pushed, nothing deleted"
                           % (pr, repr(last.get("state"))[:40], repr(last.get("merged"))[:40]))
    return local, joins


def _cleaned(tip, joins):
    """After the pushes, the merge lock freed: delete each joined run's remote branch, leased on the commit pushed to it,
    and its records ref (a branch naming no run has none), then run stack-pr.sh and print the stack's pushed <tip> and
    its tracking pull request. A ref origin no longer has counts as deleted; a delete that failed is named, stack-pr.sh
    still runs, and the exit is 2."""
    failed = []
    for sha, _, branch in joins:
        run_issue = run_dir.branch_issue(branch)
        refs = [(branch, ["--force-with-lease=%s:%s" % (branch, sha)])]
        refs += [(run_records.ref(run_issue), [])] if run_issue else []
        for ref, lease in refs:
            run = git.network("push", *lease, "origin", "--delete", ref, cwd=".")
            if run.returncode and "remote ref does not exist" not in (run.stderr or ""):
                failed.append("the delete of origin's %s failed (exit %d): %s" % (
                    ref, run.returncode, " ".join((run.stderr or "").split())))
    code, said = stack_fix.script("stack-pr.sh", limit=stack_fix.NETWORK)
    for line in failed:
        print("stack-recover: the stack and the joined branches are pushed, but %s; owed: delete it" % line,
              file=sys.stderr)
    if code:
        return _refuse("stack-pr.sh exits %d: the stack and the joined branches are pushed%s, but no tracking pull"
                       " request url is known, so CI on the tip %s cannot be waited for"
                       % (code, "" if failed else " and cleaned up", tip))
    if failed:
        return 2
    print("%s %s" % (tip, said.strip()))
    return 0


def main(argv):
    if argv:
        return entry.refuse(usage=USAGE)
    try:
        outage = os.path.exists(os.path.join(run_dir.main_tree_from_files(), ".tdd", "github-outage"))
    except OSError as error:
        return _refuse("the main working tree cannot be read (%s), so whether GitHub is out is not known" % error)
    if outage:
        return _refuse(".tdd/github-outage exists, so recovery waits for the GitHub outage to end; nothing read, locked"
                       " or pushed")
    window, refusal = merge_common.settle_window()
    if refusal:
        return _refuse(refusal)
    try:
        stack = stack_branch.named(".")
    except stack_branch.Refused as refused:
        return _refuse("stack-branch.sh exits 2: %s" % refused)
    if stack is None:
        print("stack-recover: stack-branch.sh exits 3: the repository's CLAUDE.md names no stack branch, so nothing was"
              " joined offline", file=sys.stderr)
        return 3
    pid = str(os.getpid())
    code, _ = stack_fix.script("merge-lock.sh", "take", "--pid", pid)
    if code:
        return _refuse("merge-lock.sh take exits %d: the merge lock not taken; nothing fetched or pushed" % code)
    try:
        held = _held(stack, window)
    finally:
        # Every way out frees the lock, an interrupt among them: merge-lock.sh never takes over a dead holder's lock.
        stack_fix.script("merge-lock.sh", "release", "--pid", pid)
    return held if isinstance(held, int) else _cleaned(*held)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
