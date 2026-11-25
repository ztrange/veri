"""revise.sh's computation, run in-process: REVISE.md's revise loop for one rejected phase (sub-steps 1-5), sliced
like the fused halves of a step (PRD 038.9)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import os
import shutil
import sys

import diff_step
import event_log
import fused
import fused_step
import green_half
import red_half
import refactor_half
import replaces_case
import ledger
import run_dir
import tunables
import wrong_test_route
from ledger import handed_out
from next_pending_refactor import refactor_pending

NAME = "revise"
USAGE = "usage: revise.sh <n> <phase>  (phase: red, green, refactor or diff)"
PHASES = ("red", "green", "refactor", "diff")
LAUNCH = {"red": red_half.launch_verdict, "green": green_half.launch_verdict,
          "refactor": refactor_half.launch_verdict, "diff": diff_step.launch_verdict}
SKIPPED = "skipped"  # a re-verify the run switched off
STAGES = {"red": "red-half", "green": "green-half", "refactor": "refactor-half", "diff": "diff-step"}
# The verifier line naming a case renamed and changed (#2594): the plan split is the conductor's, never an attempt.
RENAMED = "step renamed and changed test cases, so the step must be split"
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = run_dir.ledger("", "%s")

# The $S/ scripts this call makes, in the order each is first made.
CALLS = ("build-develop-prompt.sh", "comment.sh", "event.sh", "stop-requested.sh", "detach-leaf.sh", "supervise.sh",
         "run-leaf.sh", "wait-leaf.sh", "step-cost.sh", "step-budget.sh", "tests-frozen.sh", "run-verdict.sh",
         "pin-reject-route.sh", "same-reject.sh", "restore-production.sh", "extract-result.sh", "red-divergence.sh",
         "preserve-attempt.sh", "red-setup.sh")


def main(argv):
    if len(argv) != 2 or not argv[0].isdigit() or argv[1] not in PHASES:
        sys.stderr.write(USAGE + "\n")
        return 2
    try:
        with fused.quiet():
            return run(*argv)
    except fused.Stop as stop:
        return fused.stopped(stop)
    except fused.Waiting as waiting:
        sys.stdout.write("waiting on %s\n" % waiting.name)
        return 3


def run(n, phase):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER, SPEC)
    if given is None:
        return 2
    settled, wt = given
    step = fused_step.first_step(wt, n, refactor_pending if phase == "refactor" else handed_out)
    resumed = fused.load_wait(wt, n, NAME)
    if resumed is None:
        k = spent(wt, step, phase) + 1
        judged = start(n, wt, step, phase, k)
        if judged is None:
            return 1
        values = dict(judged, phase=phase, k=k)
        at = attempt(n, wt, settled, step, values)
    else:
        at, values = resumed
    while True:
        if at.startswith("revise-"):
            code = fused.wait(wt, n, NAME, at)
            if code != 0:
                raise fused.Stop("3", "wait-leaf.sh %s exit %d" % (at, code), code)
            if values["phase"] not in ("refactor", "diff"):  # REVISE.md *The diff phase*: no step-cost line
                fused_step.cost_check(wt, step)
            at = checks(n, wt, settled, step, values)
        if at is not None:
            code = 0 if at == SKIPPED else fused.wait(wt, n, NAME, at)
            if code not in (0, 1):
                raise fused.Stop("5", "wait-leaf.sh %s exit %d" % (at, code), code)
            if code == 0 and recorded(n, wt, step, values):
                return finish(n, wt, step, values, at)
            if code == 1 and at == "verdict-pin":
                route_pin_reject(n, wt, step, values)
        values = dict(values, k=values["k"] + 1)
        at = attempt(n, wt, settled, step, values)


def route_pin_reject(n, wt, step, values):
    """REVISE.md sub-step 5, a red revise's verify-pin REJECT: pin-reject-route.sh's exit 0 retires the step (Stop,
    exit 1), any code but 1 bails (Stop, its code); on 1 the pin's reason becomes the one attempt k+1 compares and
    revises. A step reached by a `missing` reroute passes `--missing-reroute` (PIN.md)."""
    with contextlib.chdir(wt):
        missing = ("--missing-reroute",) if wrong_test_route.missing_reroutes(step) else ()
    route = fused.call(fused.script("pin-reject-route.sh"), *missing, ".tdd/verify-pin.reason", LEDGER % n, step,
                       values["target_test"], cwd=wt)[0]
    if route == 0:
        raise fused.Stop("5", "pin-reject-route.sh exit 0: the step retired", 1)
    if route != 1:
        raise fused.Stop("5", "pin-reject-route.sh exit %d" % route, route)
    shutil.copyfile(os.path.join(wt, ".tdd", "verify-pin.reason"), os.path.join(wt, ".tdd", "verify-red.reason"))

def start(n, wt, step, phase, k):
    """The values the rejected verifier judged: red's from the report it judged (`.tdd/develop-red.out`, at every
    attempt: the revise report names neither key), since red-half writes its record only after a PASS; green's from red-half's record,
    and refactor's from refactor-half's rejected record, the only place its wait values survive (exit 2 without one).
    Green and refactor return None, the seam line printed, when no red-half record names the step (PRD 038.1 SC4)."""
    if phase == "red":
        return judged(wt, ".tdd/develop-red.out")
    if phase == "diff":
        return rejected_values(wt, n, phase, step)
    red = fused_step.record(NAME, wt, n, step)
    if red is None:
        return None
    if phase == "refactor":
        return rejected_values(wt, n, phase, step)
    return {"test_path": red["test_path"], "target_test": red["target_test"]}


def rejected_values(wt, n, phase, step):
    """The values the phase stage saved before its verifier's REJECT, from its rejected record naming <step>: the only
    place refactor's wait values and diff's step base survive; exit 2 without one."""
    rejected = fused_step.rejected(wt, n, STAGES[phase], step)
    if rejected is None:
        raise fused.Stop("1", "no " + os.path.relpath(fused.wait_record(wt, n, STAGES[phase] + "-rejected"), wt), 2)
    return rejected[1]


def judged(wt, report):
    got = fused.report("1", wt, report, "TEST_PATH", "TARGET_TEST")
    return {"test_path": got["TEST_PATH"], "target_test": got["TARGET_TEST"]}


def spent(wt, step, phase):
    """The attempts already spent on <phase> in the open step: the conductor's `revise` marks naming both."""
    marks = 0
    for e in event_log.events(wt, "revise", "step-split", skip_unreadable=True):
        if e.get("event") == "step-split":
            if ledger.same_step(e.get("anchor", ""), step):
                marks = 0
        elif (e.get("actor") == "conductor" and e.get("phase") == phase
              and ledger.same_step(e.get("step", ""), step)):
            marks += 1
    return marks


def attempt(n, wt, settled, step, values):
    """REVISE.md sub-steps 2 and 3 for attempt k: the reason kept as `.tdd/verify-<phase>-<k>.reason`, the revise
    prompt, the Revise comment, the `revise` mark and the revise leaf's launch. The leaf launched."""
    phase, k = values["phase"], values["k"]
    if phase == "diff" and RENAMED in read(wt, ".tdd/verify-diff.reason"):
        raise fused.Stop("1", RENAMED, 1)
    shutil.copyfile(os.path.join(wt, ".tdd", "verify-%s.reason" % phase),
                    os.path.join(wt, ".tdd", "verify-%s-%d.reason" % (phase, k)))
    if k > 1:
        fused.checked("1", fused.script("same-reject.sh"), ".tdd/verify-%s-%d.reason" % (phase, k - 1),
                      ".tdd/verify-%s.reason" % phase, cwd=wt, ok=(1, 2))
    budget = tunables.get("REVISE_BUDGET", unless_empty=True)
    if k > int(budget):
        raise fused.Stop("budget", "REVISE_BUDGET=%s attempts spent" % budget, 1)
    fast = settled["fast_cmd"]
    leaf = "revise-%s-%d" % (phase, k)
    fused.checked("2", fused.script("build-develop-prompt.sh"), "revise", phase, SPEC % n, step, fast,
                  ".tdd/verify-%s.reason" % phase, fast, cwd=wt, env=fused.step_env(n, step),
                  out=".tdd/%s.prompt" % leaf)
    fused.checked("2", fused.script("comment.sh"), n, "revise", phase, str(k), cwd=wt)
    fused.mark("2", wt, n, step, "revise", "budget=" + budget,
               VERI_PHASE=phase, VERI_ATTEMPT=str(k))
    if phase == "red":
        rerouted = rerouted_red(wt, n, step)  # a rerouted case's revise keeps every path the reroute edited
        kept = list(dict.fromkeys((rerouted or {}).get("rerouted", []) + [values["test_path"]]))
        fused.checked("3", fused.script("restore-production.sh"), *kept, cwd=wt)
    fused.launch("3", wt, leaf, "run-leaf.sh", ".tdd/%s.prompt" % leaf, "--permission-mode", "bypassPermissions",
                 env=fused.step_env(n, step, VERI_TEST_CMD=fast), out=".tdd/%s.out" % leaf, err=".tdd/%s.err" % leaf,
                 clear=(".tdd/red-prediction.md", ".tdd/red-run-output.txt"))
    fused.save_wait(wt, n, NAME, leaf, values)
    return leaf


def checks(n, wt, settled, step, values):
    """REVISE.md sub-step 4: red's prediction gate, green's tests-frozen.sh check, before any verifier. A check that
    spends attempt k as a REJECT does leaves its reason in the reason file and launches no verifier (None); otherwise
    the re-verify is launched (its leaf, or SKIPPED)."""
    routed(wt, values)
    if values["phase"] == "red":
        if passes_unmodified(wt, values):
            return verify(n, wt, settled, step, values, "pin")
        return red_checks(n, wt, settled, step, values)
    if values["phase"] == "refactor":
        return verify(n, wt, settled, step, values)
    if values["phase"] == "diff":
        return diff_checks(n, wt, settled, step, values)
    code, said, _ = fused.call(fused.script("tests-frozen.sh"), "check", "--step", step, cwd=wt)
    if code not in (0, 1):
        raise fused.Stop("4", fused.label("tests-frozen.sh", "check", "--step", step) + " exit %d" % code, code)
    if code == 1:
        with open(os.path.join(wt, ".tdd", "verify-%s.reason" % values["phase"]), "w") as f:
            f.write("REASON: the revise changed a frozen test file: %s\n" % " ".join(said.split()))
        return None
    check_earlier(n, wt, step, list(dict.fromkeys(green_half.rerouted_cases(wt, step)
                                                  + (replaces_case.parse(step) or ([], ""))[0])))
    return verify(n, wt, settled, step, values)


def passes_unmodified(wt, values):
    """A revised red whose report says `AGAINST_UNMODIFIED: PASSES`, bare or followed by its why, is a pin."""
    got = fused.report("4", wt, ".tdd/revise-red-%d.out" % values["k"], "AGAINST_UNMODIFIED")["AGAINST_UNMODIFIED"]
    return got is not None and (got == "PASSES" or got.startswith("PASSES" + WHY))


def check_earlier(n, wt, step, excepted):
    fused.checked("4", fused.script("tests-frozen.sh"), "check-earlier", LEDGER % n, "--step", step,
                  *[arg for case in excepted for arg in ("--except", case)], cwd=wt)


def diff_checks(n, wt, settled, step, values):
    """The diff phase's sub-step 4 (REVISE.md *The diff phase*): the revise leaf's SUITE: line (exit 2 stops for the
    conductor's adjudication) and its deviation recorded (0 or 3 go on), then the re-verify."""
    leaf = "revise-diff-%d" % values["k"]
    fused.checked("4", fused.script("suite-reported.sh"), leaf, cwd=wt, err=".tdd/suite-reported.err")
    fused.checked("4", fused.script("diff-leaf-deviation.sh"), leaf, values["step_base"], LEDGER % n, cwd=wt,
                  ok=(0, 3))
    return verify(n, wt, settled, step, values)


# The revise report's answers that route it elsewhere (RVS7), per phase: the conductor's routes, never an attempt.
ROUTES = {"red": (("OUTCOME", "IMPOSSIBLE"),),
          "green": (("OUTCOME", "IMPOSSIBLE"), ("WRONG_TEST", None), ("SUPERSEDED", None)),
          "refactor": (("OUTCOME", "IMPOSSIBLE"),), "diff": (("OUTCOME", "IMPOSSIBLE"),)}


# The revise prompts ask for `OUTCOME: REWRITTEN | IMPOSSIBLE — <why>` (develop-revise.md,
# develop-revise-diff.md) and, with a MISSING_TEST: line, the bare `OUTCOME: IMPOSSIBLE`: an OUTCOME route
# matches its value alone or followed by this.
WHY = " — "


def routed(wt, values):
    """REVISE.md sub-step 3's answers that end the loop: stop with exit 1 naming the report line."""
    routes = ROUTES[values["phase"]]
    got = fused.report("3", wt, ".tdd/revise-%s-%d.out" % (values["phase"], values["k"]), *dict(routes))
    for key, value in routes:
        if got[key] is not None and (value in (None, got[key])
                                     or key == "OUTCOME" and got[key].startswith(value + WHY)):
            raise fused.Stop("3", "%s: %s" % (key, got[key]), 1)


# Red's prediction gate (red-divergence.sh): the reason the exits that are not a match leave; exit 0's is the script's.
UNMATCHED = {1: "REASON: prediction not written before the run\n",
             2: "REASON: the revised red carries no readable PREDICTION: line\n"}


def red_checks(n, wt, settled, step, values):
    """Red's sub-step 4: the revised report's prediction gated, the test kept from `.tdd/develop-red.out` (the revise
    report names neither key); exit 3 (matched) re-verifies, any other exit spends the attempt, exit 0 or 2 (a
    divergence, or no readable prediction) marked `prediction-diverged` with its tree preserved, best-effort (RVS4)."""
    out = ".tdd/revise-red-%d.out" % values["k"]
    gate = fused.call(fused.script("red-divergence.sh"), ".tdd/red-prediction.md", ".tdd/red-run-output.txt", cwd=wt,
                      stdin=read(wt, out), out=".tdd/verify-red.reason")[0]
    if gate == 3:
        rerouted = rerouted_red(wt, n, step) or {}
        excepted = list(dict.fromkeys(rerouted.get("cases", []) + (replaces_case.parse(step) or ([], ""))[0]))
        check_earlier(n, wt, step, excepted)
        return verify(n, wt, settled, step, values)
    if gate in UNMATCHED:
        with open(os.path.join(wt, ".tdd", "verify-red.reason"), "w") as f:
            f.write(UNMATCHED[gate])
    if gate in (0, 2):
        fused.mark("4", wt, n, step, "prediction-diverged")
        fused.call(fused.script("preserve-attempt.sh"), n, step, "revise-red", str(values["k"]),
                   "prediction-diverged", cwd=wt)
    return None


def read(wt, path):
    with open(os.path.join(wt, path), encoding="utf-8", errors="replace") as f:
        return f.read()


def launch_pin(where, n, wt, settled, step, values):
    fused.launch(where, wt, "verdict-pin", "run-verdict.sh", "--step", step, "--fast-cmd", settled["fast_cmd"],
                 "--branch-base", fused_step.branch_base(where, wt, n), "pin",
                 SPEC % n, values["test_path"], values["target_test"],
                 env=fused.step_env(n, step, VERI_TEST_CMD=settled["fast_cmd"]), out=".tdd/verify-pin.reason",
                 err=".tdd/verify-pin.err")


def verify(n, wt, settled, step, values, as_phase=None):
    """REVISE.md sub-step 5's re-verify: verdict-<phase> launched by the phase stage's own launch, so it takes exactly
    that stage's run-verdict.sh arguments and the run's recorded branch base (RVS13). The leaf launched, or SKIPPED
    with the phase switched off (ADR-0033): its skip marked and `skipped` written to its exit file, as the stage does."""
    phase = as_phase or values["phase"]
    if fused_step.verify_switched_off(wt, n, phase):
        fused.mark("5", wt, n, step, "verify-%s-skipped" % phase, "reason=switched-off")
        with open(os.path.join(wt, ".tdd", "verdict-%s.exit" % phase), "w") as f:
            f.write("skipped\n")
        return SKIPPED
    (launch_pin if as_phase else LAUNCH[phase])("5", n, wt, settled, step, values)
    fused.save_wait(wt, n, NAME, "verdict-" + phase, values)
    return "verdict-" + phase


def recorded(n, wt, step, values):
    """A revised red's PASS records the step's frozen tests and red-setup (REVISE.md sub-step 5); tests-frozen.sh exit
    1 is a REJECT that spends the attempt, its stdout the reason (False). True for every other phase."""
    if values["phase"] != "red":
        return True
    red_test_id = fused_step.red_test_id(values["test_path"], values["target_test"])
    paths = [values["test_path"]]
    rerouted = rerouted_red(wt, n, step)
    if rerouted is not None:  # a rerouted case's revise: the step's own Red case stays the one checked (PRD 038.10)
        red_test_id = fused_step.red_test_id(rerouted["test_path"], rerouted["target_test"])
        paths = list(dict.fromkeys(rerouted["rerouted"] + paths))
    code, said, _ = fused.call(fused.script("tests-frozen.sh"), "record", "--step", step, "--red-case", red_test_id,
                               *paths, cwd=wt)
    if code == 1:
        with open(os.path.join(wt, ".tdd", "verify-red.reason"), "w") as f:
            f.write(said)
        return False
    if code != 0:
        raise fused.Stop("5", fused.label("tests-frozen.sh", "record", "--step", step) + " exit %d" % code, code)
    fused.checked("5", fused.script("red-setup.sh"), "record", n, cwd=wt, ok=(0, 2, 3),
                  stdin=read(wt, ".tdd/revise-red-%d.out" % values["k"]))
    return True


def rerouted_red(wt, n, step):
    """red-half's rejected record when reroute.sh left it for a REJECT of a rerouted case (its `rerouted` test paths,
    PRD 038.10 RRT5): the step's own test_path and target_test, and those paths; else None."""
    rejected = fused_step.rejected(wt, n, "red-half", step)
    return rejected[1] if rejected is not None and "rerouted" in rejected[1] else None


def finish(n, wt, step, values, at):
    """REVISE.md sub-step 5 on a PASS: the revised verdict's comment, then the phase stage's wait record re-saved at
    <at>, so the stage called again finishes as after its own PASS: at its verdict, or at SKIPPED past a switched-off
    one with its verify comment `posted`, which no stage step names, so the stage goes straight to its finish. The
    values are the stage's rejected record's, red's and green's test replaced by the revised one; the rejected record
    is removed."""
    phase = values["phase"]
    stage = STAGES[phase]
    fused.checked("5", fused.script("comment.sh"), n, "verify-revised", phase, cwd=wt)
    rejected = fused_step.rejected(wt, n, stage, step)
    kept = dict(rejected[1] if rejected else {})
    if phase == "diff":
        kept["leaf"] = "revise-diff-%d" % values["k"]  # the leaf that made the step's last commit, for the flip
    elif phase != "refactor" and "rerouted" not in kept:  # a rerouted case's revise keeps the step's own Red case
        kept.update(test_path=values["test_path"], target_test=values["target_test"])
    kept["revised"] = True
    if at == SKIPPED:
        kept["posted"] = True
    fused.save_wait(wt, n, stage, at, kept, step)
    with contextlib.suppress(FileNotFoundError):
        os.remove(fused.wait_record(wt, n, stage + "-rejected"))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
