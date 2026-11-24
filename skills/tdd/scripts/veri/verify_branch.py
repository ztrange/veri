"""verify-branch.sh's computation: the blind whole-branch verifier stage of the Draft PR step (PRD 040.1)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import add_ledger_step
import fused
import fused_step
import run_dir
import tunables
from ledger import STEP_RE, added_file, has_kind, read_ledger

LEAF = "verdict-branch"
OWNER = "verify-branch"
REASON = ".tdd/verify-branch.reason"
USAGE = "usage: verify-branch.sh <n>"
# parse_verdict's leniency (leading whitespace, any case; ASCII \s is its SPACE set) plus a list bullet and an
# opening backtick.
MISSING_TEST_RE = re.compile(r"^\s*(?:[-*]\s+)?`?missing_test:", re.IGNORECASE | re.ASCII)


def main(argv):
    if not argv:
        sys.stderr.write(USAGE + "\n")
        return 2
    n = argv[0]
    got = fused_step.inputs("verify-branch", n, ".tdd/issue-%s-spec.md")
    if got is None:
        return 2
    settled, wt = got
    if fused_step.verify_switched_off(wt, n, "branch"):
        fused.mark("1", wt, n, "", "verify-branch-skipped", "reason=switched-off")
        with open(os.path.join(wt, ".tdd/verdict-branch.exit"), "w") as f:
            f.write("skipped\n")
        return 0
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
    if sum(has_kind(line, "⟦branch-repair⟧") for line in steps) >= int(tunables.get("VERI_BRANCH_REPAIRS")):
        fused.call(fused.script("bail.sh"), n, "branch-rejected", "verify-branch", "--note-file",
                   REASON, cwd=wt)
        return 1
    try:
        with open(os.path.join(wt, REASON), encoding="utf-8", errors="replace") as f:
            reason = f.read()
    except OSError:
        reason = ""
    missing = any(MISSING_TEST_RE.match(line) for line in reason.split("\n"))
    reason = " ".join(reason.replace("⟦", "[").replace("⟧", "]").replace("⟂", "").split())
    step = "fix what verify-branch rejected: %s%s ⟦branch-repair⟧" % (
        reason or "see .tdd/verify-branch.reason", "" if missing else " ⟦diff-checked⟧")
    code = add_ledger_step.add(ledger, "after", steps[-1], [step])
    if code != 0:
        return code
    paths = [ledger, added_file(ledger)]
    fused.checked("1", "git", "add", "--", *paths, cwd=wt)
    fused.checked("1", "git", "commit", "-q", "-m", "plan: verify-branch repair step", "--", *paths, cwd=wt)
    return 1


def launch(n, wt, settled):
    base = fused_step.branch_base("1", wt, n)
    fused.launch("1", wt, LEAF, "run-verdict.sh", "--fast-cmd", settled["fast_cmd"], "--branch-base",
                 base, "branch", ".tdd/issue-%s-spec.md" % n,
                 env=tunables.with_values(VERI_TEST_CMD=settled["fast_cmd"], VERI_ISSUE=n),
                 out=REASON, err=".tdd/verify-branch.err")


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
