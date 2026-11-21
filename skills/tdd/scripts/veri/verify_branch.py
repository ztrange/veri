"""verify-branch.sh's computation: the blind whole-branch verifier stage of the Draft PR step (PRD 040.1)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import add_ledger_step
import fused
import fused_step
import run_dir
import tunables
from ledger import STEP_RE, carries_mark, read_ledger

LEAF = "verdict-branch"
OWNER = "verify-branch"
REASON = ".tdd/verify-branch.reason"
USAGE = "usage: verify-branch.sh <n>"


def main(argv):
    if not argv:
        sys.stderr.write(USAGE + "\n")
        return 2
    n = argv[0]
    got = fused_step.inputs("verify-branch", n, ".tdd/issue-%s-spec.md")
    if got is None:
        return 2
    settled, wt = got
    tip = fused.checked("1", "git", "rev-parse", "HEAD", cwd=wt).strip()
    marker = os.path.join(wt, ".tdd/issue-%s-branch-verified" % n)
    if os.path.exists(marker) and open(marker).read().strip() == tip:
        return 0
    try:
        if fused.load_wait(wt, n, OWNER) is None:
            launch(n, wt, settled)
            fused.save_wait(wt, n, OWNER, "1", [])
        code = fused.wait(wt, n, OWNER, LEAF)
    except fused.Stop as stop:
        return fused.stopped(stop)
    except fused.Waiting as waiting:
        sys.stdout.write("waiting on %s\n" % waiting.name)
        return 3
    if code == 1:
        return repair(n, wt)
    if code != 0:
        return code
    tip = fused.checked("1", "git", "rev-parse", "HEAD", cwd=wt).strip()
    with open(marker, "w") as f:
        f.write(tip + "\n")
    return 0


def repair(n, wt):
    ledger = run_dir.ledger(wt, n)
    steps = [line for line in read_ledger(ledger).split("\n") if STEP_RE.fullmatch(line)]
    if sum(carries_mark(line, "branch-repair") for line in steps) >= int(tunables.get("VERI_BRANCH_REPAIRS")):
        fused.call(fused.script("bail.sh"), n, "branch-rejected", "verify-branch", "--note-file",
                   REASON, cwd=wt)
        return 1
    try:
        with open(os.path.join(wt, REASON), encoding="utf-8", errors="replace") as f:
            reason = f.read()
    except OSError:
        reason = ""
    reason = " ".join(reason.replace("⟦", "[").replace("⟧", "]").replace("⟂", "").split())
    step = "fix what verify-branch rejected: %s ⟦diff-checked⟧ ⟦branch-repair⟧" % (reason or "see .tdd/verify-branch.reason")
    return add_ledger_step.add(ledger, "after", steps[-1], [step])


def launch(n, wt, settled):
    base = fused_step.branch_base("1", wt, n)
    fused.launch("1", wt, LEAF, "run-verdict.sh", "--fast-cmd", settled["fast_cmd"], "--branch-base",
                 base, "branch", ".tdd/issue-%s-spec.md" % n,
                 env=tunables.with_values(VERI_TEST_CMD=settled["fast_cmd"], VERI_ISSUE=n),
                 out=REASON, err=".tdd/verify-branch.err")


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
