"""stack-revert.sh's logic, run in-process: reverts every commit of an issue on the stack, its hand fix included, as one
commit on the tip, when the one fix attempt failed (PRD 034.3d)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import entry
import git
import github
import stack_branch
import stack_culprit
import stack_fix

USAGE = "usage: stack-revert.sh <n>"
JOIN_ATTEMPTS = 5  # the pushes tried while origin's stack keeps moving, as a join tries
SUBJECT = "revert: take issue %s's commits off the stack (#%s)"


class Nothing(Exception):
    """Nothing to revert (exit 3); str() says why."""


def _top():
    """The working tree the script was run in: its worktree is made under that tree's `.tdd/`."""
    return git.out("rev-parse", "--show-toplevel")


def _rev(ref):
    """The sha <ref> names, "" when it names none."""
    found = git.git("rev-parse", "--verify", "--quiet", ref + "^{commit}", capture_output=True, text=True)
    return found.stdout.strip() if found.returncode == 0 else ""


def _add_worktree(path, commit):
    """Whether `git worktree add --detach <path> <commit>` made the worktree."""
    return git.git("worktree", "add", "--detach", path, commit, capture_output=True, text=True).returncode == 0


def _checkout(path, commit):
    """Whether <path>, this script's own worktree, now has <commit> checked out, detached, its tree clean."""
    return git.git("-C", path, "checkout", "--detach", "--force", commit, capture_output=True, text=True).returncode == 0


def _remove_worktree(path):
    """Whether `git worktree remove --force <path>` removed this script's own worktree."""
    return git.git("worktree", "remove", "--force", path, capture_output=True, text=True).returncode == 0


def _revert(path, commits):
    """`git revert --no-commit <commits>` in <path>, in the order given: "ok", "conflict" (the revert stopped on a
    conflict, aborted), or "failed" (refused without a conflict)."""
    done = git.git("-C", path, "revert", "--no-commit", *commits, capture_output=True, text=True)
    if done.returncode == 0:
        return "ok"
    unmerged = git.git("-C", path, "diff", "--name-only", "--diff-filter=U", capture_output=True, text=True)
    git.git("-C", path, "revert", "--abort", capture_output=True, text=True)
    return "conflict" if unmerged.returncode == 0 and unmerged.stdout.strip() else "failed"


def _commit(path, subject, body):
    """Commit what the revert staged in <path> with <subject> and <body>: the new sha, "" when git refuses."""
    if git.git("-C", path, "commit", "-q", "-m", subject, "-m", body, capture_output=True, text=True).returncode:
        return ""
    found = git.git("-C", path, "rev-parse", "HEAD", capture_output=True, text=True)
    return found.stdout.strip() if found.returncode == 0 else ""


def _say(message):
    print("stack-revert: " + message, file=sys.stderr)


def _reverted(n, path, worktree):
    """Under the lock: revert issue <n>'s commits on a fresh fetch of the stack in the worktree <path> and push the
    revert, starting again from the fetch while origin's stack moves. (stack, default, revert sha, n's commits, the
    hand-fix commits among them). <worktree> is a one-item list set once the worktree is added."""
    for _ in range(JOIN_ATTEMPTS):
        try:
            found = stack_branch.ahead(".")
        except stack_branch.Refused as refused:
            raise stack_fix.NoAnswer(str(refused)) from None
        if found is None:
            raise stack_fix.NoAnswer("the repository's CLAUDE.md names no stack branch (stack-branch.sh exits 3)")
        stack, default, commits = found
        onto = _rev("refs/remotes/origin/" + stack)
        if not onto:
            raise stack_fix.NoAnswer("origin has no %s branch after the fetch; nothing pushed" % stack)
        owned = stack_culprit.owners([subject for _, subject in commits])
        mine = [(commit, subject) for (commit, subject), issues in zip(commits, owned) if n in issues]
        if not mine:
            raise Nothing("no commit of origin/%s..origin/%s belongs to issue %s; nothing reverted" % (default, stack, n))
        if worktree:
            if not _checkout(path, onto):
                raise stack_fix.NoAnswer("checking out %s in its own worktree failed; nothing pushed" % onto)
        elif _add_worktree(path, onto):
            worktree.append(path)
        else:
            raise stack_fix.NoAnswer("git worktree add --detach %s failed; nothing reverted or pushed" % path)
        newest_first = [commit for commit, _ in reversed(mine)]
        said = _revert(path, newest_first)
        if said == "conflict":
            raise stack_fix.Refused("reverting issue %s's commits conflicts on origin/%s at %s: a later commit depends on"
                                    " them, a human's call; nothing pushed" % (n, stack, onto))
        if said != "ok":
            raise stack_fix.NoAnswer("git revert of issue %s's commits was refused without a conflict; nothing pushed" % n)
        sha = _commit(path, SUBJECT % (n, n), "Reverts, newest first:\n%s" % "".join(
            "%s %s\n" % found for found in reversed(mine)))
        if not sha:
            raise stack_fix.NoAnswer("committing the revert failed; nothing pushed")
        stack_fix.tier_and_prose(path, "nothing pushed")
        try:
            stack_fix.pushed(sha, stack, onto)
        except stack_fix.Refused as moved:
            _say("%s; starting again from the fetch" % moved)
            continue
        return stack, default, sha
    raise stack_fix.NoAnswer("origin's stack moved on each of %d attempts; nothing more pushed" % JOIN_ATTEMPTS)


def main(argv):
    if len(argv) != 1 or not re.fullmatch(r"[1-9][0-9]*", argv[0]):
        return entry.refuse(usage=USAGE)
    n = argv[0]
    pid = str(os.getpid())
    code, _ = stack_fix.script("merge-lock.sh", "take", "--pid", pid)
    if code:
        return entry.refuse("taking the merge lock failed (exit %d); nothing reverted" % code, prefix="stack-revert: ")
    worktree = []
    try:
        code, said = stack_fix.script("stack-red.sh", limit=stack_fix.NETWORK)
        if code == 3:
            raise Nothing("stack-red.sh exits 3: the stack is not red; nothing reverted")
        if code != 0:
            raise stack_fix.NoAnswer("stack-red.sh exited %d, so whether the stack is red is not known" % code)
        stack, default, sha = _reverted(n, os.path.join(_top(), ".tdd", "stack-revert-%s" % pid), worktree)
    except (stack_fix.Refused, stack_fix.NoAnswer, Nothing) as stopped:
        _say(str(stopped))
        return {stack_fix.Refused: 1, stack_fix.NoAnswer: 2, Nothing: 3}[type(stopped)]
    finally:
        for path in worktree:
            if not _remove_worktree(path):
                _say("git worktree remove --force %s failed; its own worktree is left there" % path)
        released, _ = stack_fix.script("merge-lock.sh", "release", "--pid", pid)
        if released:
            _say("releasing the merge lock failed (exit %d)" % released)
    sys.stdout.write(sha + "\n")
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
