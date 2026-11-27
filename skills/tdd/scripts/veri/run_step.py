"""run-step.sh's computation, run in-process: a cycle step's four fused stages in one call, stopping at the first seam
(PRD 038.2)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import os
import re
import sys

import fused
import fused_step
import ledger
import red_half
import replaces_case
import reroute as reroute_stage
import revise as revise_stage
import run_dir
from next_pending_refactor import refactor_pending

NAME = "run-step"
USAGE = "usage: run-step.sh <n> [--from <stage>] [--hand <stage>]…"
LEDGER = run_dir.ledger("", "%s")
RED = "SKILL.md#Red — one failing test (developer leaf), then verify-red (blind)"
GREEN = "SKILL.md#Green — minimum implementation (developer leaf), then verify-green (blind)"
REVISE = "REVISE.md#Revising on a REJECT"
REFACTOR = "SKILL.md#Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"
DIFF = "DIFF-CHECKED.md#A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)"
GO_RED = "GO-RED.md#A `⟦go-red⟧` step — a mutation probe on its named case"
# A refactor-kind run's procedure: the whole file, which has no heading of its own (#4621).
REFACTOR_KIND = "REFACTOR-KIND.md"
SPEC = ".tdd/issue-%s-spec.md"

# The stages in the order they run -> (the heading anchor, `<file>#<heading>` under the skill's directory, of the
# section whose prose takes over at a stop there (S4); the marks of the step kinds it does not handle (S3, RN6): it
# stops before such a stage without calling it). green-half's reason is specs/prd-027.md GH1.
STAGES = {"red-half": (RED, ()), "green-half": (GREEN, ("⟦ci-repair⟧", "⟦replaces-case⟧")),
          "refactor-half": (REFACTOR, ()), "step-close": (REFACTOR, ()), "revise": (REVISE, ()),
          "diff-step": (DIFF, ()), "reroute": (GREEN, ()), "go-red-step": (GO_RED, ()),
          "skill-edit-half": ("SKILL-EDIT.md#The skill-edit step", ())}
# The stages run in series; revise runs only on a half's REJECT and reroute only on a Green route, each a stage only
# so `--hand` can name it; diff-step and go-red-step each run a kind's step in place of the series.
SERIES = tuple(stage for stage in STAGES
               if stage not in ("revise", "diff-step", "reroute", "go-red-step", "skill-edit-half"))
# The phase stages -> the phase a verifier judges: a REJECT there (`.tdd/verdict-<phase>.exit` holding 1)
# is revise.sh's.
PHASES = {"red-half": "red", "green-half": "green", "refactor-half": "refactor", "diff-step": "diff"}
# A green-half stop on a report line wrong-test-route.sh answers (two of green_half.ROUTES; SPLIT and TIDY_FIRST keep
# their seam), and the green report reroute.sh is then handed (PRD 038.10 RRT8).
ROUTED = re.compile(r"stopped at \d+ (WRONG_TEST|SUPERSEDED): ")
GREEN_REPORT = ".tdd/develop-green.out"
# The reason a verify-green REJECT leaves, which reroute.sh routes before any revise (PRD 038.9 RVS9).
VERIFY_GREEN_REASON = ".tdd/verify-green.reason"
REVISE_GREEN_REPORT = ".tdd/revise-green-%d.out"
# reroute()'s answer that sends the step back to red-half (a verify-red REJECT of a rerouted case, PRD 038.10 RRT5).
RESTART = ("restart",)
# The scripts a `next=` it prints may name, every other `next=` being an anchor above (S4, RN10): itself, called again
# on a stage's 3, and seam-settle.sh, which a stage's own record seam names.
NEXT_SCRIPTS = ("run-step.sh", "seam-settle.sh")
# The line fused_step.record prints for a stage whose record is missing or names another step (PRD 038.1 SC4).
RECORD_SEAM = "seam=%s code=1 reason=record next="
# The $S/ scripts this call makes, in order: the stages, each of which launches its own leaves through supervise.sh;
# it launches none itself (RN12).
CALLS = tuple(stage + ".sh" for stage in SERIES)
# The kinds that are not a cycle step, red_half.REFUSED's (RN7) -> (the anchor of the prose that runs them, the stage
# that runs them as the step's one stage in place of the series, or None): a step of a kind no stage runs stops
# before any stage on `seam=none` (038.3 DST8; 038.4 adds ⟦skill-edit⟧'s).
KINDS = {"⟦diff-checked⟧": (DIFF, "diff-step"), ledger.GO_RED_MARK: (GO_RED, "go-red-step"),
         "⟦phases:": ("SKILL.md#A `⟦phases: …⟧` step — each listed phase, a developer leaf then a blind verifier",
                      None),
         "⟦skill-edit⟧": ("SKILL-EDIT.md#The skill-edit step", "skill-edit-half"), "⟦fixture-repair⟧": (RED, None)}
# The stages a kind runs in place of the series.
KIND_STAGES = tuple(stage for _, stage in KINDS.values() if stage)


REFUSAL = re.compile(
    r"Requirements heading names no existing unit: "
    r"|rows for .* are not under ## Requirements"
    r"|a ## Requirements row is under no ### unit heading"
    r"|## Requirements has no ### heading for unit: "
    r"|## Requirements table for .* lacks its header: "
    r"|Requirement row .* splits into \d+ cells, not ID, Requirement and Why"
    r"|Requirement row .*<reword> states the full text the unit already holds under "
    r"|skill-edit-guard.sh: ")


def refactor_kind(wt, n):
    """Whether the run's spec carries the `## Refactor` section capture-spec.sh writes for the `refactor` label."""
    try:
        with open(os.path.join(wt, SPEC % n), encoding="utf-8", errors="surrogateescape") as f:
            return re.search(r"^## Refactor$", f.read(), re.M) is not None
    except FileNotFoundError:
        return False


def refused(wt, n):
    """Whether .tdd/skill-edit-<n>.out holds a line starting with one of skill-edit-step.sh's refusals."""
    try:
        with open(os.path.join(wt, ".tdd", "skill-edit-%s.out" % n)) as f:
            return any(REFUSAL.match(line) for line in f)
    except FileNotFoundError:
        return False


def parse(argv):
    """(n, the --from stage or None, the --hand stages); None for arguments it does not take."""
    if not argv or not argv[0].isdigit():
        return None
    start, hand, rest = None, set(), list(argv[1:])
    while rest:
        option, value = rest.pop(0), rest.pop(0) if rest else None
        if option not in ("--from", "--hand") or value not in STAGES or option == "--from" and (
                start is not None or value not in SERIES + KIND_STAGES):
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
    step = fused_step.open_step(wt, n)
    if step is None:
        sys.stderr.write("run-step.sh: no open step in %s\n" % (LEDGER % n))
        return 3
    kinds = red_half.refused(step)
    if not kinds and refactor_kind(wt, n):
        # A refactor-kind run's step takes REFACTOR-KIND.md's Cover → Transform → Verify, never Red/Green (#4621);
        # a special kind keeps its own route there, ⟦diff-checked⟧'s diff-step included.
        sys.stdout.write("seam=none code=1 reason=kind next=%s\n" % REFACTOR_KIND)
        return 1
    for kind in kinds:
        if KINDS[kind][1] is None:
            sys.stdout.write("seam=none code=1 reason=kind next=%s\n" % KINDS[kind][0])
            return 1
    order = [KINDS[kinds[0]][1]] if kinds else list(SERIES)
    if start_at is not None and start_at not in order:
        sys.stderr.write("run-step.sh: --from %s: not a stage of this step\n" % start_at)
        return 2
    if start_at is not None:
        start = order.index(start_at)
    elif kinds:
        start = 0
    elif pending is None and fused_step.rejected(wt, n, "red-half", step) is not None:
        # A reroute's `route=revise phase=red` outside this call (#4613): red is revised first, whatever stage the
        # step seam recorded, and a green-half REJECT from before it is answered, so green-half then starts afresh.
        answered(wt, n)
        start = order.index("red-half")
    else:
        start = max(order.index("refactor-half" if pending is not None else "red-half"), resumed(wt, n, step, order))
    out, i, action = "", start, None
    while i < len(order):
        stage = order[i]
        script = stage + ".sh"
        anchor, unhandled = STAGES[stage]
        if action is None:
            if stage in hand:
                return seam(wt, n, step, stage, 1, anchor, "hand")
            if any(replaces_case.is_replaces_case_step(step) if mark == "⟦replaces-case⟧"
                   else ledger.has_kind(step, mark) for mark in unhandled):
                return seam(wt, n, step, stage, 1, anchor, "unmodelled")
            report = reroute_stage.pending(wt, n, step) if stage == "green-half" else None
            if report is not None:
                # A reroute under way (its 3 called run-step.sh again): back to it, on the report it was handed.
                action = ("reroute", report[1]["report"])
            elif stage in PHASES and fused_step.rejected(wt, n, stage, step) is not None:
                # A revise under way (its 3 called run-step.sh again): back to it, never to the half.
                action = ("revise",)
            else:
                action = ("stage",)
        (kind, *given), action = action, None
        if kind == "reroute":
            action = reroute(wt, n, step, hand, *given)
            if isinstance(action, int):
                return action
            if action is RESTART:
                i, action = order.index("red-half"), None
            continue
        if kind == "revise":
            action = revise(wt, n, step, stage, hand)
            if isinstance(action, int):
                return action
            continue
        code, out = run_stage(script, n)
        if code == 1 and stage == "green-half" and ROUTED.match((out.splitlines() or [""])[-1]):
            action = ("reroute", GREEN_REPORT)
            continue
        if code == 1 and stage in PHASES and (verdict(wt, PHASES[stage]) == "1" or stage in KIND_STAGES and
                                              fused_step.rejected(wt, n, stage, step) is not None):
            # diff-step's flip REJECT leaves its rejected record with the verifier's PASS in place.
            action = ("reroute", VERIFY_GREEN_REASON) if stage == "green-half" else ("revise",)
            continue
        if code != 0:
            said = [line for line in out.splitlines() if line.startswith(RECORD_SEAM % stage)]
            if code == 1 and said:
                return seam(wt, n, step, stage, code, None, line=said[-1])
            if code == 2 and stage == "skill-edit-half":
                sys.stdout.write("out=.tdd/skill-edit-%s.out refusal=%s\n" % (n, "yes" if refused(wt, n) else "no"))
            return seam(wt, n, step, stage, code, NEXT_SCRIPTS[0] + " " + n if code == 3 else anchor)
        i += 1
    said = [line for line in out.splitlines() if line.startswith("next=")]
    if not said:
        record(wt, n, order[-1], step)
        sys.stderr.write("run-step.sh: %s.sh exited 0 with no next= line\n" % order[-1])
        return 2
    with contextlib.suppress(FileNotFoundError):
        os.remove(fused.settled_file(wt, n, "step"))
    sys.stdout.write(said[-1] + "\n")
    return 0


def reroute(wt, n, step, hand, report):
    """reroute.sh <n> <report> for a Green route (PRD 038.10 RRT8): the next action, green-half again on its 0 (the
    answered REJECT's exit file and green-half's rejected record cleared, so the relaunched green is not read as a
    second REJECT), revise.sh <n> green on its `route=revise phase=green`; with `reroute` handed, the hand seam and 1,
    never calling it; else the seam's exit."""
    if "reroute" in hand:
        record(wt, n, "green-half", step)
        sys.stdout.write("seam=reroute code=1 reason=hand next=%s\n" % GREEN)
        return 1
    code, out = run_stage("reroute.sh", n, report)
    said = (out.splitlines() or [""])[-1]
    if code == 0:
        answered(wt, n)
        return ("stage",)
    if code == 1 and said == "route=revise phase=green":
        return ("revise",)
    if code == 1 and said == "route=revise phase=red":
        # A verify-red REJECT of the rerouted case: red-half's rejected record sends red-half to revise.sh <n> red,
        # and green-half then starts afresh.
        answered(wt, n)
        return RESTART
    record(wt, n, "green-half", step)
    sys.stdout.write("seam=reroute code=%d next=%s\n" % (code, NEXT_SCRIPTS[0] + " " + n if code == 3 else GREEN))
    return code


def answered(wt, n):
    """A verify-green REJECT a reroute answered: `.tdd/verdict-green.exit` and green-half's rejected record removed."""
    for path in (os.path.join(wt, ".tdd", "verdict-green.exit"), fused.wait_record(wt, n, "green-half-rejected")):
        with contextlib.suppress(FileNotFoundError):
            os.remove(path)


def run_stage(script, n, *more):
    """(code, stdout) of one stage call; a code outside the API's four is no answer (2), named on stderr."""
    code, out, _ = fused.call(fused.script(script), n, *more)
    if code not in (0, 1, 2, 3):
        # The exit-code API has four codes: a 127, a signal's negative code or any other is no answer (2).
        sys.stderr.write("run-step.sh: %s exited %d\n" % (script, code))
        code = 2
    return code, out


def verdict(wt, phase):
    """What `.tdd/verdict-<phase>.exit` holds, stripped; "" without one."""
    try:
        with open(os.path.join(wt, ".tdd", "verdict-%s.exit" % phase)) as f:
            return f.read().strip()
    except OSError:
        return ""


def revise(wt, n, step, stage, hand):
    """revise.sh <n> <phase> for a REJECT of <stage> (PRD 038.9 criterion 9): the next action, the stage called
    again on its 0, reroute.sh on a revise-green route (PRD 038.10 RRT8); with `revise` handed, the hand seam and 1,
    never calling it; else the seam's exit, `next=run-step.sh <n>` on its 3 (the seam recorded at <stage>, whose
    rejected record sends the next call back here), REVISE.md's anchor on any other code."""
    if "revise" in hand:
        record(wt, n, stage, step)
        sys.stdout.write("seam=revise code=1 reason=hand next=%s\n" % REVISE)
        return 1
    code, out = run_stage("revise.sh", n, PHASES[stage])
    if code == 0:
        return ("stage",)
    if code == 1 and stage == "green-half" and ROUTED.match((out.splitlines() or [""])[-1]):
        # A revise-green route (PRD 038.9 RVS7) is reroute.sh's, on the report of the attempt that stopped.
        return ("reroute", REVISE_GREEN_REPORT % revise_stage.spent(wt, step, "green"))
    record(wt, n, stage, step)
    sys.stdout.write("seam=revise code=%d next=%s\n" % (code, NEXT_SCRIPTS[0] + " " + n if code == 3 else REVISE))
    return code


def seam(wt, n, step, stage, code, next_, reason=None, line=None):
    """A stop at <stage>: the seam recorded in .tdd/issue-<n>-step (RN3), then the last line, <line> when given (a
    stage's own record seam), else `seam=<stage> code=<code> [reason=<reason>] next=<next_>`; <code>, the exit."""
    record(wt, n, stage, step)
    if line is None:
        line = "seam=%s code=%d%s next=%s" % (stage, code, " reason=" + reason if reason else "", next_)
    sys.stdout.write(line + "\n")
    return code


def record(wt, n, stage, step):
    """The seam at <stage> of <step>, in .tdd/issue-<n>-step (RN3)."""
    with open(fused.settled_file(wt, n, "step"), "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write("stage=%s\nstep=%s\n" % (stage, step))


def resumed(wt, n, step, order):
    """The index in <order> of the stage .tdd/issue-<n>-step recorded, when it names <step> (ledger.same_step);
    else 0."""
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
