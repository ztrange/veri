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


def main(argv):
    if len(argv) not in (2, 3) or not argv[0].isdigit() or argv[1] not in MODES or argv[2:] not in ([], ["--drop"]):
        sys.stderr.write(USAGE + "\n")
        return 2
    given = fused_step.inputs(NAME + ".sh", argv[0])
    if given is None:
        return 2
    try:
        return run(argv[0], argv[1], given[1])
    except fused.Stop as stop:
        return fused.stopped(stop)


def run(n, mode, wt):
    for name in live_leaves(wt):
        fused.call(fused.script("wait-leaf.sh"), name, cwd=wt)
    for name in ("rebase-merge", "rebase-apply"):
        fused.call("git", "rev-parse", "--git-path", name, cwd=wt)
    fused.call("git", "rev-parse", "-q", "--verify", "MERGE_HEAD", cwd=wt)
    fused.checked("2", "git", "status", "--porcelain", cwd=wt)
    fused.checked("2", "git", "reset", "--hard", "HEAD", cwd=wt)
    fused.call(fused.script("push-branch.sh"), cwd=wt)
    steps = ledger_steps(committed_ledger(n, wt))
    step = current_or_last_done_record(steps)
    fused.mark("4", wt, n, step.text if step else "", "stop", "mode=" + mode, "at=planned")
    fused.checked("5", fused.script("comment.sh"), n, "stopped", cwd=wt)
    fused.checked("6", fused.script("stop-requested.sh"), "--clear", cwd=wt)
    return 0


def live_leaves(wt):
    """The names of the `.tdd/<name>.pid` files whose process still runs `supervise.sh <name>` (step 1)."""
    tdd = os.path.join(wt, ".tdd")
    names = sorted(f[:-len(".pid")] for f in os.listdir(tdd) if f.endswith(".pid") and f != "conductor.pid")
    return [name for name in names if live(os.path.join(tdd, name + ".pid"), name)]


def live(path, name):
    pid = pid_file.number_in(path)
    return pid is not None and pid_file.supervising(pid, name)


def committed_ledger(n, wt):
    """The ledger HEAD holds; "" when HEAD holds none. Only the line naming the call is printed, never the ledger."""
    path = ".tdd/issue-%s.md" % n
    code, out, _ = fused.run_script("git", "show", "HEAD:" + path, cwd=wt)
    sys.stdout.write(fused.label("git", "show", "HEAD:" + path) + " exit %d\n" % code)
    return out if code == 0 else ""


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
