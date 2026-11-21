"""verify-branch.sh's computation: the blind whole-branch verifier stage of the Draft PR step (PRD 040.1)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step
import tunables

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
    base = fused_step.branch_base("1", wt, n)
    try:
        fused.launch("1", wt, "verdict-branch", "run-verdict.sh", "--fast-cmd", settled["fast_cmd"], "--branch-base",
                     base, "branch", ".tdd/issue-%s-spec.md" % n,
                     env=tunables.with_values(VERI_TEST_CMD=settled["fast_cmd"], VERI_ISSUE=n),
                     out=".tdd/verify-branch.reason", err=".tdd/verify-branch.err")
    except fused.Stop as stop:
        return fused.stopped(stop)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
