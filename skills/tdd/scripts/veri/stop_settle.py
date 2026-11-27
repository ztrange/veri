"""stop-settle.sh's computation, run in-process: a stop (STOPPING.md steps 1-6) settled in one call (PRD 038.5)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import fused
import fused_step
import pid_file
import run_dir
from ledger import ledger_steps
from ledger_steps import current_or_last_done_record

NAME = "stop-settle"
USAGE = "usage: stop-settle.sh <n> <mode> [--drop]"
MODES = ("at-ledger", "at-leaf", "now")
NOTE = ".tdd/stop-settle-note.md"


def main(argv):
    if len(argv) not in (2, 3) or not argv[0].isdigit() or argv[1] not in MODES or argv[2:] not in ([], ["--drop"]):
        sys.stderr.write(USAGE + "\n")
        return 2
    given = fused_step.inputs(NAME + ".sh", argv[0])
    if given is None:
        return 2
    try:
        return run(argv[0], argv[1], given[1], drop=argv[2:] == ["--drop"])
    except fused.Stop as stop:
        return fused.stopped(stop)
    except fused.Waiting as waiting:
        sys.stdout.write("waiting on %s\n" % waiting.name)
        return 3


def run(n, mode, wt, drop=False):
    """STOPPING.md steps 1-6 in order; 0 once the request is cleared."""
    for name in leaves(wt, n):
        fused.save_wait(wt, n, NAME, name, {})
        fused.wait(wt, n, NAME, name)
    interrupted = interrupted_by(wt)
    if interrupted:
        note = ["The tree holds an interrupted %s, left as it is: a human finishes it with %s." % interrupted]
    else:
        note = settle_tree(wt, drop) + pushed(wt)
    text = committed_ledger(n, wt)
    steps = ledger_steps(text or "")
    step = current_or_last_done_record(steps)
    at = "unsettled" if interrupted else boundary(text, steps)
    answered("4", fused.script("event.sh"), "stop", "mode=" + mode, "at=" + at, cwd=wt,
             env=fused.step_env(n, step.text if step else "", VERI_ACTOR="conductor"))
    answered("5", fused.script("comment.sh"), n, "stopped", *noted(wt, note), cwd=wt)
    answered("6", fused.script("stop-requested.sh"), "--clear", cwd=wt)
    return 0


def answered(where, *args, **kw):
    """fused.checked, a nonzero exit stopping it with exit 2: a call that fails gave no answer, never a clean negative
    (pr_finish.answered's rule)."""
    try:
        return fused.checked(where, *args, **kw)
    except fused.Stop as stop:
        raise fused.Stop(stop.where, stop.what, 2) from None


def leaves(wt, n):
    """Step 1's leaves: the one a wait record by this conductor names first, though its process may have ended since
    that wait ran out, then each still supervised (live_leaves); a record another conductor wrote is removed (FC7)."""
    resumed = fused.load_wait(wt, n, NAME)
    live = live_leaves(wt)
    return ([resumed[0]] if resumed and resumed[0] not in live else []) + live


def settle_tree(wt, drop):
    """Step 2 on a tree with no interrupted rebase or merge: a dirty one stops it unless <drop>, then the reset; the
    comment's lines on what it dropped."""
    dirty = [line for line in answered("2", "git", "status", "--porcelain", cwd=wt).splitlines() if line]
    if dirty and not drop:
        raise fused.Stop("2", "tree-check", 1)
    answered("2", "git", "reset", "--hard", "HEAD", cwd=wt)
    return dropped(dirty)


def pushed(wt):
    """Step 3: push-branch.sh, its exit 1 or 2 recorded, never fixed; the comment's `push=rejected` line, if any."""
    code, _, said = fused.call(fused.script("push-branch.sh"), cwd=wt)
    return [] if code == 0 else ["push=rejected sha=" + remote_sha(said)]


def dropped(dirty):
    """What step 2's reset dropped, for the comment: each changed tracked path; an untracked one it leaves is named
    as left (`git reset --hard HEAD` is the only reach for the tree a stop has)."""
    tracked = [line[3:] for line in dirty if not line.startswith("??")]
    untracked = [line[3:] for line in dirty if line.startswith("??")]
    return ((["Dropped by `git reset --hard HEAD`, the half-done step: " + ", ".join(tracked) + "."]
             if tracked else [])
            + (["Left untracked: " + ", ".join(untracked) + "."] if untracked else []))


def remote_sha(said):
    """The remote's sha push-branch.sh's stderr names (step 3), `unknown` when it names none."""
    found = re.search(r" is at ([0-9a-f]{7,40})\b", said)
    return found.group(1) if found else "unknown"


def interrupted_by(wt):
    """Step 2's check: (what, how a human finishes it) for an interrupted rebase or merge, else None. Each is read off
    the path `git rev-parse --git-path` names, so a git that fails is exit 2, never read as no rebase or merge."""
    for name in ("rebase-merge", "rebase-apply"):
        if os.path.isdir(git_path(wt, name)):
            return "rebase", "`git rebase --continue` or `git rebase --abort`"
    if os.path.isfile(git_path(wt, "MERGE_HEAD")):
        return "merge", "`git merge --continue` or `git merge --abort`"
    return None


def git_path(wt, name):
    path = answered("2", "git", "rev-parse", "--git-path", name, cwd=wt).strip()
    if not path:
        raise fused.Stop("2", "git rev-parse --git-path %s printed nothing" % name, 2)
    return os.path.join(wt, path)


def noted(wt, note):
    """The comment's `--note-file` arguments, the note written to it; none for an empty note."""
    if not note:
        return ()
    with open(os.path.join(wt, NOTE), "w") as f:
        f.write("".join(line + "\n" for line in note))
    return "--note-file", NOTE


def live_leaves(wt):
    """The names of the `.tdd/<name>.pid` files whose process still runs `supervise.sh <name>` (step 1)."""
    tdd = os.path.join(wt, ".tdd")
    names = sorted(f[:-len(".pid")] for f in os.listdir(tdd) if f.endswith(".pid") and f != "conductor.pid")
    return [name for name in names if live(os.path.join(tdd, name + ".pid"), name)]


def live(path, name):
    pid = pid_file.number_in(path)
    return pid is not None and pid_file.supervising(pid, name)


def committed_ledger(n, wt):
    """The ledger HEAD holds; None when `git ls-tree` finds none there. A git that fails is exit 2, never read as no
    ledger. Only the line naming the `git show` is printed, never the ledger."""
    path = run_dir.ledger("", n)
    if not answered("4", "git", "ls-tree", "--name-only", "HEAD", "--", path, cwd=wt).strip():
        return None
    code, out, _ = fused.run_script("git", "show", "HEAD:" + path, cwd=wt)
    sys.stdout.write(fused.label("git", "show", "HEAD:" + path) + " exit %d\n" % code)
    if code != 0:
        raise fused.Stop("4", "git show HEAD:%s exit %d" % (path, code), 2)
    return out


def boundary(text, steps):
    """Step 4's `at` for a tree it settled: `unplanned` with no committed ledger, `planned` with no step ticked,
    `green` while a ticked step still carries its refactor-pending mark, else `step-done`."""
    if text is None:
        return "unplanned"
    done = [s for s in steps if s.state == "done"]
    if not done:
        return "planned"
    return "green" if any(s.pending == "1" for s in done) else "step-done"


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
