"""pr-prepare.sh's computation, run in-process: the Draft PR step's sub-step 1 up to the structural pass's skip (the
two questions, the rebase, the regrade block, the rebased tip's suite when owed, the pinned-lease push, the
refactor-owed list), made in one call (PRD 027.9, amended: it stops after RB7)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import run_dir

NAME = "pr-prepare"
USAGE = "usage: pr-prepare.sh <n>"
LEDGER = run_dir.ledger("", "%s")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    questions(wt, n)
    return 0


def ledger_text(wt, n):
    with open(os.path.join(wt, LEDGER % n), encoding="utf-8", errors="surrogateescape") as f:
        return f.read()


def questions(wt, n):
    """Sub-step 1's two questions (RB1): a dirty tree, or a step still only green, stops it with exit 1."""
    if fused.changed_paths("1", wt):
        raise fused.Stop("1", "tree-check", 1)
    code = fused.call(fused.script("next-pending-refactor.sh"), cwd=wt, stdin=ledger_text(wt, n))[0]
    if code != 3:
        raise fused.Stop("1", "next-pending-refactor.sh exit %d" % code, code)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
