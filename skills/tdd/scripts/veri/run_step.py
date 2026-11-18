"""run-step.sh's computation, run in-process: a cycle step's four fused stages in one call, stopping at the first seam
(PRD 038.2)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import os
import sys

import fused
import fused_step
import ledger
import red_half
import run_dir
from next_pending_refactor import refactor_pending

NAME = "run-step"
USAGE = "usage: run-step.sh <n> [--from <stage>] [--hand <stage>]…"
LEDGER = run_dir.ledger("", "%s")
RED = "SKILL.md#Red — one failing test (developer leaf), then verify-red (blind)"
GREEN = "SKILL.md#Green — minimum implementation (developer leaf), then verify-green (blind)"
REFACTOR = "SKILL.md#Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"

# The stages in the order they run -> (the heading anchor, `<file>#<heading>` under the skill's directory, of the
# section whose prose takes over at a stop there (S4); the marks of the step kinds it does not handle (S3, RN6): it
# stops before such a stage without calling it). green-half's reason is specs/prd-027.md GH1.
STAGES = {"red-half": (RED, ()), "green-half": (GREEN, ("⟦ci-repair⟧", "⟦replaces-case⟧")),
          "refactor-half": (REFACTOR, ()), "step-close": (REFACTOR, ())}
# The scripts a `next=` it prints may name, every other `next=` being an anchor above (S4, RN10): itself, called again
# on a stage's 3, and seam-settle.sh, which a stage's own record seam names.
NEXT_SCRIPTS = ("run-step.sh", "seam-settle.sh")
# The line fused_step.record prints for a stage whose record is missing or names another step (PRD 038.1 SC4).
RECORD_SEAM = "seam=%s code=1 reason=record next="
# The kinds that are not a cycle step, red_half.REFUSED's (RN7) -> the anchor of the prose that runs them; a step of
# one stops before any stage on `seam=none`, until a stage for that kind exists (038.3, 038.4).
KINDS = {"⟦diff-checked⟧": "DIFF-CHECKED.md#A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)",
         "⟦phases:": "SKILL.md#A `⟦phases: …⟧` step — each listed phase, a developer leaf then a blind verifier",
         "⟦skill-edit⟧": "SKILL-EDIT.md#The skill-edit step", "⟦fixture-repair⟧": RED}


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
    for kind in red_half.REFUSED:
        if kind in step:
            sys.stdout.write("seam=none code=1 reason=kind next=%s\n" % KINDS[kind])
            return 1
    order = list(STAGES)
    if start_at is not None:
        start = order.index(start_at)
    else:
        start = max(order.index("refactor-half" if pending is not None else "red-half"), resumed(wt, n, step, order))
    out = ""
    for stage in order[start:]:
        anchor, unhandled = STAGES[stage]
        if stage in hand:
            return seam(wt, n, step, stage, 1, anchor, "hand")
        if any(mark in step for mark in unhandled):
            return seam(wt, n, step, stage, 1, anchor, "unmodelled")
        code, out, _ = fused.call(fused.script(stage + ".sh"), n)
        if code != 0:
            said = [line for line in out.splitlines() if line.startswith(RECORD_SEAM % stage)]
            if code == 1 and said:
                return seam(wt, n, step, stage, code, None, line=said[-1])
            return seam(wt, n, step, stage, code, NEXT_SCRIPTS[0] + " " + n if code == 3 else anchor)
    with contextlib.suppress(FileNotFoundError):
        os.remove(fused.settled_file(wt, n, "step"))
    sys.stdout.write([line for line in out.splitlines() if line.startswith("next=")][-1] + "\n")
    return 0


def seam(wt, n, step, stage, code, next_, reason=None, line=None):
    """A stop at <stage>: the seam recorded in .tdd/issue-<n>-step (RN3), then the last line, <line> when given (a
    stage's own record seam), else `seam=<stage> code=<code> [reason=<reason>] next=<next_>`; <code>, the exit."""
    with open(fused.settled_file(wt, n, "step"), "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write("stage=%s\nstep=%s\n" % (stage, step))
    if line is None:
        line = "seam=%s code=%d%s next=%s" % (stage, code, " reason=" + reason if reason else "", next_)
    sys.stdout.write(line + "\n")
    return code


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
