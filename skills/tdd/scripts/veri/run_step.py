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
from next_pending_refactor import refactor_pending

NAME = "run-step"
USAGE = "usage: run-step.sh <n> [--from <stage>] [--hand <stage>]…"
LEDGER = run_dir.ledger("", "%s")
RED = "SKILL.md#Red — one failing test (developer leaf), then verify-red (blind)"
GREEN = "SKILL.md#Green — minimum implementation (developer leaf), then verify-green (blind)"
REFACTOR = "SKILL.md#Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"

# The stages in the order they run -> the heading anchor (`<file>#<heading>`, under the skill's directory) of the
# section whose prose takes over at a stop there (S4).
STAGES = {"red-half": RED, "green-half": GREEN, "refactor-half": REFACTOR, "step-close": REFACTOR}


def parse(argv):
    """(n, the --from stage or None, the --hand stages); None for arguments it does not take."""
    if not argv or not argv[0].isdigit():
        return None
    start, hand, rest = None, set(), list(argv[1:])
    while rest:
        option, value = rest.pop(0), rest.pop(0) if rest else None
        if option not in ("--from", "--hand") or value not in STAGES or option == "--from" and start is not None:
            return None
        if option == "--hand":
            hand.add(value)
        else:
            start = value
    return argv[0], start, hand


def main(argv):
    parsed = parse(argv)
    if parsed is None:
        sys.stderr.write(USAGE + "\n")
        return 2
    n, start_at, hand = parsed
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    wt = given[1]
    pending = fused_step.first_step(wt, n, refactor_pending)
    step = pending if pending is not None else fused_step.first_step(wt, n, ledger.handed_out)
    if step is None:
        sys.stderr.write("run-step.sh: no open step in %s\n" % (LEDGER % n))
        return 3
    order = list(STAGES)
    if start_at is not None:
        start = order.index(start_at)
    else:
        start = max(order.index("refactor-half" if pending is not None else "red-half"), resumed(wt, n, step, order))
    out = ""
    for stage in order[start:]:
        if stage in hand:
            record(wt, n, stage, step)
            sys.stdout.write("seam=%s code=1 reason=hand next=%s\n" % (stage, STAGES[stage]))
            return 1
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
