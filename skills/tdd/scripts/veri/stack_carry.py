"""stack-carry.sh's logic, run in-process: carries the stack onto the new default branch after a slice landed
(PRD 034.4b)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import shutil
import sys
import tempfile

import entry
import git
import stack_branch
import stack_fix

USAGE = "usage: stack-carry.sh <old-cut>"
PREFIX = "stack-carry: "


class _Stop(Exception):
    """The carry-over ends with <code>, <line> said on stderr."""

    def __init__(self, code, line):
        super().__init__(line)
        self.code = code


def _run(*args, cwd="."):
    """`git <args>` in <cwd>, text captured: its CompletedProcess."""
    return git.git(*args, cwd=cwd, capture_output=True, text=True)


def _unanswered(what, run):
    """_Stop(2) saying <what> got no answer from git, with <run>'s exit and stderr."""
    return _Stop(2, "%s got no answer from git (exit %d): %s; nothing rebased or pushed"
                 % (what, run.returncode, " ".join((run.stderr or "").split())[:300]))


def _rev(name, what):
    """The commit <name> (said as <what>) resolves to; _Stop(2) when it resolves to none, or git gives no answer."""
    run = _run("rev-parse", "--verify", "--quiet", "--end-of-options", name + "^{commit}")
    if run.returncode == 1:
        raise _Stop(2, "%s does not resolve to a commit; nothing rebased or pushed" % what)
    if run.returncode or not run.stdout.strip():
        raise _unanswered("reading " + what, run)
    return run.stdout.strip()


def _ancestor(older, newer):
    """Whether <older> is an ancestor of <newer>; _Stop(2) when git gives no answer, never read as "no"."""
    run = _run("merge-base", "--is-ancestor", older, newer)
    if run.returncode not in (0, 1):
        raise _unanswered("git merge-base --is-ancestor %s %s" % (older, newer), run)
    return run.returncode == 0


def _tree_of(name):
    """The tree <name> names; _Stop(2) when git gives no answer."""
    run = _run("rev-parse", "--verify", "--end-of-options", name + "^{tree}")
    if run.returncode or not run.stdout.strip():
        raise _unanswered("reading the tree of " + name, run)
    return run.stdout.strip()


def _landed(default, cut):
    """Whether origin/<default> has landed <cut>: merging <cut> into it changes nothing (a content check, since a
    rebase-merge rewrites every sha); _Stop(2) when git gives no answer."""
    run = _run("merge-tree", "--write-tree", "origin/" + default, cut)
    if run.returncode not in (0, 1):
        raise _unanswered("git merge-tree --write-tree origin/%s %s" % (default, cut), run)
    return run.returncode == 0 and run.stdout.split("\n", 1)[0].strip() == _tree_of("origin/" + default)


def _top():
    """The working tree stack-carry.sh runs in; _Stop(2) when git gives no answer."""
    run = _run("rev-parse", "--show-toplevel")
    if run.returncode or not run.stdout.strip():
        raise _unanswered("git rev-parse --show-toplevel", run)
    return run.stdout.strip()


def _rebased(default, cut, tip):
    """<tip> rebased with `git rebase --onto origin/<default> <cut> <tip>` in a detached worktree of its own under
    .tdd/, removed after on every exit: (the new tip, its tree)."""
    state = os.path.join(_top(), ".tdd")
    os.makedirs(state, exist_ok=True)
    parent = tempfile.mkdtemp(prefix="stack-carry-", dir=state)
    tree = os.path.join(parent, "stack")
    try:
        added = _run("worktree", "add", "--detach", tree, tip)
        if added.returncode:
            raise _unanswered("git worktree add --detach " + tree, added)
        rebase = _run("rebase", "--onto", "origin/" + default, cut, tip, cwd=tree)
        if rebase.returncode:
            unmerged = _run("diff", "--name-only", "--diff-filter=U", cwd=tree).stdout.split()
            _run("rebase", "--abort", cwd=tree)
            if unmerged:
                raise _Stop(1, "the rebase of %s..%s onto origin/%s conflicts in %s; aborted, nothing pushed or"
                            " rewritten" % (cut, tip, default, " ".join(unmerged[:5])))
            raise _unanswered("git rebase --onto origin/%s %s %s" % (default, cut, tip), rebase)
        head = _run("rev-parse", "HEAD", "HEAD^{tree}", cwd=tree)
        if head.returncode or len(head.stdout.split()) != 2:
            raise _unanswered("reading the rebased tip", head)
        return tuple(head.stdout.split())
    finally:
        _run("worktree", "remove", "--force", tree)
        shutil.rmtree(parent, ignore_errors=True)


def _refused(stack, tip, new, push):
    """Raise the _Stop a failed leased <push> of <new> to <stack> ends with: 1 when origin's stack is read at a commit
    other than the lease <tip> (it moved since the fetch, nothing lost), else 2."""
    said = " ".join((push.stderr or "").split())[:300]
    listed = git.network("ls-remote", "--heads", "origin", "refs/heads/" + stack, cwd=".")
    now = listed.stdout.split()[:1] if not listed.returncode else None
    if now is not None and now != [tip]:
        raise _Stop(1, "the leased push of %s to %s was refused: origin's %s moved since the fetch, to %s (%s); nothing"
                    " pushed or lost" % (new, stack, stack, now[0] if now else "no branch", said))
    raise _Stop(2, "the leased push of %s to %s failed (exit %d): %s%s; nothing pushed"
                % (new, stack, push.returncode, said, ""
                   if now is not None else "; reading origin's %s got no answer: %s"
                   % (stack, " ".join((listed.stderr or "").split())[:200])))


def _agrees(default, cut, tip, new, new_tree):
    """The guard on the work (D26): the old cut's changes up to the old tip, merged onto origin/<default> with the old
    cut as base, must be exactly the rebased tip <new>'s tree <new_tree>; _Stop(1) naming both trees otherwise, _Stop(2)
    when git gives no answer. "The tree is unchanged" is false whenever the default branch moved."""
    check = _run("merge-tree", "--write-tree", "--merge-base=" + cut, "origin/" + default, tip)
    if check.returncode not in (0, 1):
        raise _unanswered("git merge-tree --write-tree --merge-base=%s origin/%s %s" % (cut, default, tip), check)
    merged = check.stdout.split("\n", 1)[0].strip()
    if check.returncode or merged != new_tree:
        raise _Stop(1, "git merge-tree --write-tree --merge-base=%s origin/%s %s %s the tree %s, the rebased tip %s has"
                    " the tree %s; nothing pushed" % (cut, default, tip, "conflicts, printing" if check.returncode
                                                      else "prints", merged, new, new_tree))


def _carry(stack, name):
    """Carry <stack> with the merge lock held, never releasing it: the exit code, or _Stop."""
    fetch = git.network("fetch", "--prune", "origin", cwd=".")
    if fetch.returncode:
        raise _Stop(2, "git fetch origin failed (exit %d): %s; nothing rebased or pushed"
                    % (fetch.returncode, " ".join(fetch.stderr.split())))
    tip = _rev("refs/remotes/origin/" + stack, "origin/" + stack)
    cut = _rev(name, name)
    if not _ancestor(cut, tip):
        raise _Stop(2, "the old cut %s is not an ancestor of origin/%s at %s; nothing rebased or pushed"
                    % (cut, stack, tip))
    default = git.default_branch(cwd=".")
    if not default:
        raise _Stop(2, "origin's default branch cannot be told; nothing rebased or pushed")
    if not _landed(default, cut):
        raise _Stop(2, "origin/%s has not landed the old cut %s; nothing rebased or pushed" % (default, cut))
    if cut == tip:
        raise _Stop(3, "the old cut %s is origin/%s's tip: nothing to carry" % (cut, stack))
    new, new_tree = _rebased(default, cut, tip)
    _agrees(default, cut, tip, new, new_tree)
    push = git.network("push", "--force-with-lease=%s:%s" % (stack, tip), "origin", "%s:refs/heads/%s" % (new, stack),
                       cwd=".")
    if push.returncode:
        _refused(stack, tip, new, push)
    print(new)
    # The tracking pull request is reopened after a landing, so CI runs on the new tip (KT3).
    tracked, _ = stack_fix.script("stack-pr.sh", limit=stack_fix.NETWORK)
    if tracked not in (0, 3):
        raise _Stop(2, "origin's %s carried to %s, but stack-pr.sh exits %d: run stack-pr.sh" % (stack, new, tracked))
    return 0


def main(argv):
    if len(argv) != 1 or argv[0].startswith("-"):
        return entry.refuse(usage=USAGE)
    try:
        stack = stack_branch.named(".")
    except stack_branch.Refused as refused:
        return entry.refuse("stack-branch.sh exits 2: %s" % refused, prefix=PREFIX)
    if stack is None:
        return entry.refuse("stack-branch.sh exits 3: the repository's CLAUDE.md names no stack branch", prefix=PREFIX)
    pid = str(os.getpid())
    code, _ = stack_fix.script("merge-lock.sh", "take", "--pid", pid)
    if code:
        return entry.refuse("merge-lock.sh take exits %d: the merge lock not taken; nothing fetched or pushed" % code,
                            prefix=PREFIX)
    try:
        return _carry(stack, argv[0])
    except _Stop as stop:
        print(PREFIX + "%s; the merge lock freed" % stop, file=sys.stderr)
        return stop.code
    finally:
        # Every exit frees the lock, an unexpected error's included: merge-lock.sh never takes over a dead holder's
        # lock, so a held one would block every later merge.
        stack_fix.script("merge-lock.sh", "release", "--pid", pid)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
