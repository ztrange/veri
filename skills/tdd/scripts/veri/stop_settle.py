"""stop-settle.sh's computation, run in-process: a stop (STOPPING.md steps 1-6) settled in one call (PRD 038.5)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import pid_file
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


def run(n, mode, wt, drop=False):
    for name in live_leaves(wt):
        fused.call(fused.script("wait-leaf.sh"), name, cwd=wt)
    note = []
    interrupted = interrupted_by(wt)
    if interrupted:
        note.append("The tree holds an interrupted %s, left as it is: a human finishes it with %s." % interrupted)
    else:
        dirty = [line for line in fused.checked("2", "git", "status", "--porcelain", cwd=wt).splitlines() if line]
        if dirty and not drop:
            raise fused.Stop("2", "tree-check", 1)
        fused.checked("2", "git", "reset", "--hard", "HEAD", cwd=wt)
        note.extend(dropped(dirty))
        fused.call(fused.script("push-branch.sh"), cwd=wt)
    text = committed_ledger(n, wt)
    steps = ledger_steps(text or "")
    step = current_or_last_done_record(steps)
    at = "unsettled" if interrupted else boundary(text, steps)
    fused.mark("4", wt, n, step.text if step else "", "stop", "mode=" + mode, "at=" + at)
    fused.checked("5", fused.script("comment.sh"), n, "stopped", *noted(wt, note), cwd=wt)
    fused.checked("6", fused.script("stop-requested.sh"), "--clear", cwd=wt)
    return 0


def dropped(dirty):
    """What step 2's reset dropped, for the comment: each changed tracked path; an untracked one it leaves is named
    as left (`git reset --hard HEAD` is the only reach for the tree a stop has)."""
    tracked = [line[3:] for line in dirty if not line.startswith("??")]
    untracked = [line[3:] for line in dirty if line.startswith("??")]
    return (["Dropped by `git reset --hard HEAD`, the half-done step: " + ", ".join(tracked) + "."] if tracked else []) \
        + (["Left untracked: " + ", ".join(untracked) + "."] if untracked else [])


def interrupted_by(wt):
    """Step 2's check: (what, how a human finishes it) for an interrupted rebase or merge, else None."""
    for name in ("rebase-merge", "rebase-apply"):
        path = fused.call("git", "rev-parse", "--git-path", name, cwd=wt)[1].strip()
        if path and os.path.isdir(os.path.join(wt, path)):
            return "rebase", "`git rebase --continue` or `git rebase --abort`"
    if fused.call("git", "rev-parse", "-q", "--verify", "MERGE_HEAD", cwd=wt)[0] == 0:
        return "merge", "`git merge --continue` or `git merge --abort`"
    return None


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
    """The ledger HEAD holds; None when HEAD holds none. Only the line naming the call is printed, never the ledger."""
    path = ".tdd/issue-%s.md" % n
    code, out, _ = fused.run_script("git", "show", "HEAD:" + path, cwd=wt)
    sys.stdout.write(fused.label("git", "show", "HEAD:" + path) + " exit %d\n" % code)
    return out if code == 0 else None


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
