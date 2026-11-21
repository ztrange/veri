"""refactor-half.sh's computation, run in-process: a step's first refactor pass (SKILL.md *Refactor loop*, sub-steps
1, 2, 5 and 6 up to its PASS branch), made in one call (PRD 027.6)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys
import time

import fused
import fused_step
import run_dir
import tunables
from fused_step import detail, kind
from ledger import ledger_steps, read_ledger
from next_pending_refactor import refactor_pending
from wrong_test_route import IDENTIFIER, later_owner, later_owner_by_id

NAME = "refactor-half"
USAGE = "usage: refactor-half.sh <n>"
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = run_dir.ledger("", "%s")

# The $S/ scripts this call makes, in the order each is first made (git aside); unit/test_refactor_half.py fails when
# one is a script SKILL.md's Refactor loop section does not name, save one it exempts by name (FC19).
CALLS = ("event.sh", "refactor-budget.sh", "refactor-touched.sh", "build-develop-prompt.sh", "stop-requested.sh",
         "detach-leaf.sh", "supervise.sh", "run-leaf.sh", "wait-leaf.sh", "extract-result.sh", "refactor-triage.sh",
         "run-verdict.sh", "comment.sh", "refactor-owed.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER, SPEC)
    if given is None:
        return 2
    settled, wt = given
    step = fused_step.first_step(wt, n, refactor_pending)
    if step is None:
        sys.stderr.write("refactor-half.sh: no refactor-pending step\n")
        return 2
    green = fused_step.record(NAME, wt, n, step)
    if green is None:
        return 1
    resumed = fused.load_wait(wt, n, NAME)
    at, values = resumed if resumed is not None else develop(n, wt, settled, step, green["test_path"])
    if at == "develop-refactor":
        code = fused.wait(wt, n, NAME, "develop-refactor")
        if code != 0:
            raise fused.Stop("1", "wait-leaf.sh develop-refactor exit %d" % code, code)
        at = None
    if at is None:
        values.update(check(wt, dict(values, n=n, step=step, after=open_after(wt, n, step))))
        at = verify(n, wt, settled, step, values)
    if at == "verdict-refactor":
        code = fused.wait(wt, n, NAME, "verdict-refactor", rejected_step=step)
        if code != 0:
            raise fused.Stop("5", "wait-leaf.sh verdict-refactor exit %d" % code, code)
        values["verdict_flags"] = fused.report("5", wt, ".tdd/verify-refactor.log", "FLAGS", every=True)["FLAGS"]
    return finish(n, wt, step, values)


def develop(n, wt, settled, step, test_path):
    """The stage's start and Refactor 1 (RL2): the budget asked with a count of 0; exit 0 launches develop-refactor
    over the green commit's touched files, exit 3 launches nothing. (at, values) for the wait."""
    fused.checked("1", fused.script("event.sh"), "stage-start", "stage=refactor-loop", cwd=wt,
                  env=tunables.with_values(VERI_ISSUE=n))
    with open(os.path.join(wt, ".tdd", "stage-rl.t"), "w") as f:
        f.write("%d\n" % int(time.time()))
    # The span starts at the ledger's last commit, past a re-pin step's commits; the files the leaf may tidy are those
    # of the step's own green tick, which a re-pin step's tick after it is not (#4510), and so is verify-refactor's
    # BASE_SHA (#4544); a wait record saved before #4544 has no step_green and falls back to green_sha.
    green_sha = fused.checked("1", "git", "log", "-1", "--format=%H", "--", LEDGER % n, cwd=wt).strip()
    step_green = fused_step.green_tick("1", wt, n, "HEAD")
    if step_green is None:
        raise fused.Stop("1", "no green tick in " + LEDGER % n, 2)
    if fused_step.read_by(NAME, wt, n, step) == "green-half":
        fused_step.refresh(NAME, wt, n, "green-half", {"green_sha": green_sha})
    code, said, _ = fused.call(fused.script("refactor-budget.sh"), "0", cwd=wt)
    if code not in (0, 3):
        raise fused.Stop("1", "refactor-budget.sh 0 exit %d" % code, code)
    found = re.search(r"refactor \d+/(\d+)", said)
    if found is None:
        raise fused.Stop("1", "refactor-budget.sh 0 printed no budget", 2)
    touched = fused.checked("1", fused.script("refactor-touched.sh"), step_green, cwd=wt, ok=(0, 3)).strip()
    values = {"green_sha": green_sha, "step_green": step_green, "budget": int(found.group(1)), "touched": touched,
              "test_path": test_path, "ran": code == 0}
    if code == 3:
        return None, values
    fast = settled["fast_cmd"]
    fused.checked("1", fused.script("build-develop-prompt.sh"), "refactor", SPEC % n, step, fast, touched, cwd=wt,
                  out=".tdd/develop-refactor.prompt")
    fused.launch("1", wt, "develop-refactor", "run-leaf.sh", ".tdd/develop-refactor.prompt", "--permission-mode",
                 "bypassPermissions", env=fused.step_env(n, step, VERI_TEST_CMD=fast), out=".tdd/develop-refactor.out",
                 err=".tdd/develop-refactor.err")
    fused.save_wait(wt, n, NAME, "develop-refactor", values)
    return "develop-refactor", values


def check(wt, values):
    """Refactor 2's checks, asked of git (RL3), then the report's flags and candidates (RL4) and why the tidying
    stopped (RL5): a dirty tree, an off-route subject, an overfit flag or an in-step candidate stops it with exit 1,
    resetting nothing."""
    span = values["green_sha"] + "..HEAD"
    if fused.changed_paths("2", wt):
        raise fused.Stop("2", "tree-check", 1)
    subjects = fused.checked("2", "git", "log", "--format=%s", span, cwd=wt).splitlines()
    off = [s for s in subjects if s.strip() and not s.startswith("refactor:")]
    if off:
        raise fused.Stop("2", "subject " + off[0], 1)
    count = int(fused.checked("2", "git", "rev-list", "--count", span, cwd=wt).strip() or 0)
    got = {"RESULT": [], "CANDIDATES": [], "FLAGS": []}
    if values["ran"]:
        got = fused.report("2", wt, ".tdd/develop-refactor.out", "RESULT", "CANDIDATES", "FLAGS", every=True)
    owed = []
    for line in got["FLAGS"]:
        if kind(line) == "overfit":
            owner = deferred_to(detail(line, last=True), os.path.join(wt, SPEC % values["n"]), values["step"],
                                values["after"])
            if not owner:
                raise fused.Stop("3", "FLAGS: " + line, 1)
            owed.append("%s (owed by %s)" % (line, owner))
    for line in got["CANDIDATES"]:
        if kind(line) == "in-step":
            raise fused.Stop("6", "CANDIDATES: " + line, 1)
    if count >= values["budget"]:
        stopped = "budget"
    elif got["RESULT"] == ["nothing left to tidy"]:
        stopped = "nothing-left"
    else:
        triage = fused.call(fused.script("refactor-triage.sh"), cwd=wt, stdin=read(wt, ".tdd/develop-refactor.out"))[0]
        stopped = {0: "structural-owed", 3: "nothing-structural"}.get(triage, "malformed")
    return {"count": count, "stopped": stopped, "candidates": got["CANDIDATES"], "flags": got["FLAGS"], "owed": owed}


def deferred_to(case, spec, step, after):
    """The later unchecked step of <after> an overfit flag's <case> is owed by, or None when it is triangulated (#4438):
    an empty case, or one naming an identifier the current <step> carries, is never deferred; a case that is only an
    identifier token is matched by identifier alone, never by the text route's substring."""
    if not case or later_owner_by_id(case, spec, [step]):
        return None
    by_text = None if IDENTIFIER.fullmatch(case) else later_owner(case, spec, after)
    return by_text or later_owner_by_id(case, spec, after)


def open_after(wt, n, step):
    """The unchecked ledger steps after <step>, whose criteria an overfit flag's case may be (#4438)."""
    steps = ledger_steps(read_ledger(run_dir.ledger(wt, n)))
    names = [s.text for s in steps]
    return [s.text for s in steps[names.index(step) + 1:] if s.state == "open"] if step in names else []


def verify(n, wt, settled, step, values):
    """Refactor 5 (RL6): either skip marks it and writes `skipped` to verdict-refactor.exit, replacing an earlier
    step's verdict (#4555); nothing landed posts the skipped comment, `refactor` switched off posts verify-refactor
    once; otherwise verdict-refactor is launched. The leaf launched, or None."""
    if values["count"] == 0 or fused_step.verify_switched_off(wt, n, "refactor"):
        reason = "nothing-landed" if values["count"] == 0 else "switched-off"
        fused.mark("5", wt, n, step, "verify-refactor-skipped", "reason=" + reason)
        with open(os.path.join(wt, ".tdd", "verdict-refactor.exit"), "w") as f:
            f.write("skipped\n")
        tree_check(wt)
        fused.checked("5", fused.script("comment.sh"), n, "verify-refactor",
                      *(("--skipped",) if reason == "nothing-landed" else ()), cwd=wt)
        values["posted"] = True
        return None
    launch_verdict("5", n, wt, settled, step, values)
    fused.save_wait(wt, n, NAME, "verdict-refactor", values)
    return "verdict-refactor"


def launch_verdict(where, n, wt, settled, step, values):
    """verdict-refactor's launch, stopping at <where>: the one set of run-verdict.sh arguments refactor-half.sh and
    revise.sh's re-verify share (PRD 038.9 RVS13)."""
    fast = settled["fast_cmd"]
    fused.launch(where, wt, "verdict-refactor", "run-verdict.sh", "--step", step, "--fast-cmd", fast,
                 "--branch-base", fused_step.branch_base(where, wt, n), "refactor",
                 SPEC % n, values["test_path"], values.get("step_green", values["green_sha"]),
                 env=fused.step_env(n, step, VERI_TEST_CMD=fast),
                 out=".tdd/verify-refactor.reason", err=".tdd/verify-refactor.err")


def finish(n, wt, step, values):
    """Refactor 6 up to its PASS branch (RL7-RL10): the noted Refactor comment, verify-refactor's unless the skip
    posted it, the `refactor` mark, the leftovers recorded, and the settled file."""
    if not values.get("posted"):
        tree_check(wt)
    note = ".tdd/refactor-half-note.md"
    verdict_flags = values.get("verdict_flags", [])
    with open(os.path.join(wt, note), "w") as f:
        f.write(narration(values, verdict_flags))
    fused.checked("6", fused.script("comment.sh"), n, "refactor", "--note-file", note, cwd=wt)
    if not values.get("posted") and not values.get("revised"):  # revise.sh posted verify-revised in its place
        fused.checked("6", fused.script("comment.sh"), n, "verify-refactor", cwd=wt)
    fused.mark("6", wt, n, step, "refactor", "transforms=%d" % values["count"], "budget=%d" % values["budget"],
               "stopped=" + values["stopped"], "pass=1", VERI_PHASE="refactor")
    fused.checked("6", fused.script("refactor-owed.sh"), "append", ".tdd/issue-%s-refactor-owed.md" % n, step,
                  values["touched"], cwd=wt, stdin=read(wt, ".tdd/develop-refactor.out") if values["ran"] else "")
    # The verdict's flags and the hash it is named by come from one read of the log (#4029); a skipped verify's log
    # is an earlier step's, so its flags are not this step's.
    verdict_log, verdict_uncovered = fused_step.verdict(wt)
    uncovered = [detail(line) for line in values["flags"] if kind(line) == "uncovered-spec"]
    uncovered += verdict_uncovered if "verdict_flags" in values else []
    return fused.settle(wt, n, NAME, ["step=" + step, "green_sha=" + values["green_sha"], "count=%d" % values["count"],
                                      "budget=%d" % values["budget"], "stopped=" + values["stopped"],
                                      "touched=" + values["touched"], "verdict_log=" + verdict_log]
                      + ["uncovered_spec=" + u for u in uncovered])


def tree_check(wt):
    """D10: the tree is clean immediately before the first comment (RL7)."""
    if fused.changed_paths("6", wt):
        raise fused.Stop("6", "tree-check", 1)


def narration(values, verdict_flags):
    """Refactor 6's note: the count against the budget (an overrun never clamped), why it stopped, the structural and
    cosmetic leftovers as two counted lists, and the follow-ups: the leaf's beyond-spec flags and the verifier's
    overfit and beyond-spec flags."""
    count, budget = values["count"], values["budget"]
    lines = ["refactor %d/%d%s" % (count, budget, " — overrun" if count > budget else ""),
             "Stopped: " + values["stopped"]]
    for title, cls in (("Structural", "structural"), ("Cosmetic", "cosmetic")):
        items = [detail(c, last=True) for c in values["candidates"] if kind(c) == cls]
        lines += ["%s (%d):" % (title, len(items))] + ["- " + item for item in items]
    follow = [f for f in values["flags"] if kind(f) == "beyond-spec"] + values.get("owed", [])
    follow += [f for f in verdict_flags if kind(f) in ("overfit", "beyond-spec")]
    if follow:
        lines += ["Follow-ups:"] + ["- " + f for f in follow]
    return "".join(line + "\n" for line in lines)


def read(wt, path):
    try:
        with open(os.path.join(wt, path), encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
