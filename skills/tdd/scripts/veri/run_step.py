"""run-step.sh's computation, run in-process: a cycle step's four fused stages in one call, stopping at the first seam
(PRD 038.2)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import os
import sys

import fused
import fused_step
import ledger
import run_dir

NAME = "run-step"
USAGE = "usage: run-step.sh <n> [--from <stage>] [--hand <stage>]…"
LEDGER = run_dir.ledger("", "%s")
RED = "SKILL.md#Red — one failing test (developer leaf), then verify-red (blind)"
GREEN = "SKILL.md#Green — minimum implementation (developer leaf), then verify-green (blind)"
REFACTOR = "SKILL.md#Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"

# The stages in the order they run -> the heading anchor (`<file>#<heading>`, under the skill's directory) of the
# section whose prose takes over at a stop there (S4).
STAGES = {"red-half": RED, "green-half": GREEN, "refactor-half": REFACTOR, "step-close": REFACTOR}


def main(argv):
    if len(argv) != 1 or not argv[0].isdigit():
        sys.stderr.write(USAGE + "\n")
        return 2
    n = argv[0]
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    wt = given[1]
    step = fused_step.first_step(wt, n, ledger.handed_out)
    if step is None:
        sys.stderr.write("run-step.sh: no open step in %s\n" % (LEDGER % n))
        return 3
    order = list(STAGES)
    start = resumed(wt, n, step, order)
    out = ""
    for stage in order[start:]:
        code, out, _ = fused.call(fused.script(stage + ".sh"), n)
        if code != 0:
            record(wt, n, stage, step)
            sys.stdout.write("seam=%s code=%d next=%s\n" % (stage, code, "run-step.sh " + n if code == 3 else STAGES[stage]))
            return code
    with contextlib.suppress(FileNotFoundError):
        os.remove(fused.settled_file(wt, n, "step"))
    sys.stdout.write([line for line in out.splitlines() if line.startswith("next=")][-1] + "\n")
    return 0


def record(wt, n, stage, step):
    """The seam it stopped at, in .tdd/issue-<n>-step (RN3)."""
    with open(fused.settled_file(wt, n, "step"), "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write("stage=%s\nstep=%s\n" % (stage, step))


def resumed(wt, n, step, order):
    """The index in <order> of the stage .tdd/issue-<n>-step recorded, when it names <step> (ledger.same_step); else 0."""
    try:
        seam = fused.read_settled(fused.settled_file(wt, n, "step"))
    except OSError:
        return 0
    if seam.get("stage") in order and ledger.same_step(seam.get("step", ""), step):
        return order.index(seam["stage"])
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
