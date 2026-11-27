"""reroute.sh's computation, run in-process: wrong-test-route.sh's answer for the open step run through the rerouted
red leaf, verify-red and the frozen-test re-record (SKILL.md *Green*), sliced like the fused halves of a step
(PRD 038.10)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import json
import os
import shutil
import sys

import fused
import fused_step
import ledger
import red_half
import run_dir
from ledger import handed_out

NAME = "reroute"
USAGE = "usage: reroute.sh <n> <report>"
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = run_dir.ledger("", "%s")
REASON = ".tdd/verify-%s.reason"

# The $S/ scripts this call makes, in the order each is first made.
CALLS = ("wrong-test-route.sh", "event.sh", "build-develop-prompt.sh", "restore-production.sh", "stop-requested.sh",
         "detach-leaf.sh", "supervise.sh", "run-leaf.sh", "wait-leaf.sh", "step-cost.sh", "step-budget.sh",
         "extract-result.sh", "run-verdict.sh", "tests-frozen.sh")
# The answers this stage runs (S12) -> the rerouted red's prompt phase, its leaf being `develop-<phase>`.
RUNS = {"red": "red-contradicted", "repair": "red-repair", "supersede": "red-supersede", "missing": "red-missing"}

# The answers it stops on with exit 1, naming them (RRT4, S11, S12): plan growth (`prep`, `later`, `fixture`), the
# `diff` verifier over a stash snapshot (`supersede-diff`), and the two exhaustions, whose bail is the conductor's.
STOPS = ("prep", "later", "fixture", "supersede-diff", "missing-exhausted", "repair-exhausted")


class Revise(Exception):
    """The answer is a revise of <phase> (RRT5): exit 1, never 3, which means "call again"."""

    def __init__(self, phase):
        super().__init__(phase)
        self.phase = phase


def main(argv):
    if len(argv) != 2 or not argv[0].isdigit():
        sys.stderr.write(USAGE + "\n")
        return 2
    try:
        with fused.quiet():
            return run(*argv)
    except fused.Stop as stop:
        return fused.stopped(stop)
    except Revise as revise:
        sys.stdout.write("route=revise phase=%s\n" % revise.phase)
        return 1
    except fused.Waiting as waiting:
        sys.stdout.write("waiting on %s\n" % waiting.name)
        return 3


def run(n, report):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER, SPEC)
    if given is None:
        return 2
    settled, wt = given
    step = fused_step.first_step(wt, n, handed_out)
    step_at = (wt, n, step)
    red = fused_step.record(NAME, wt, n, step)
    if red is None:
        return 1
    own = fused_step.red_test_id(red["test_path"], red["target_test"])
    resumed = pending(wt, n, step)
    if resumed is None and report == REASON % "green" and fused_step.verify_switched_off(wt, n, "green"):
        raise fused.Stop("route", report + " with green switched off", 1)
    if resumed is None:
        at, values = launch(step_at, settled, report, own, red)
    else:
        at, values = resumed
    if at == values["leaf"]:
        waited(wt, n, "leaf", at)
        fused_step.cost_check(wt, step)
        values.update(edited(wt, values))
        at = verify(step_at, settled, values)
    while at == "verdict-red":
        code = fused.wait(wt, n, NAME, at)
        if code == 1:
            revise_red(step_at, red, values)
        if code != 0:
            raise fused.Stop("verify", "wait-leaf.sh %s exit %d" % (at, code), code)
        values["verify"] = values["verify"][1:]
        at = verify(step_at, settled, values) if values["verify"] else None
    return finish(step_at, values, red)


def revise_green(step_at, report, red):
    """wrong-test-route.sh's `revise` (exit 3): the attempt's outcome is a verify-green REJECT (SKILL.md *Green*), so
    revise.sh <n> green gets its reason, the green report when that is what was routed, and green-half's rejected
    record naming the step, which sends a sliced revise back to revise.sh; one already naming the step is kept."""
    wt = step_at[0]
    reason = os.path.join(wt, ".tdd", "verify-green.reason")
    if os.path.normpath(os.path.join(wt, report)) != reason:
        shutil.copyfile(os.path.join(wt, report), reason)
    reject(step_at, "green-half", "verdict-green", red)
    raise Revise("green")


def reject(step_at, stage, at, red, **more):
    """<stage>'s rejected record (fused.wait's on a verifier REJECT, PRD 038.9) naming <step>, written with red-half's
    values and <more> unless one already names the step."""
    wt, n, step = step_at
    if fused_step.rejected(wt, n, stage, step) is not None:
        return
    with open(fused.wait_record(wt, n, stage + "-rejected"), "w") as f:
        json.dump({"conductor": fused.conductor(wt), "at": at, "step": step,
                   "values": dict({"test_path": red["test_path"], "target_test": red["target_test"]}, **more)}, f)


def prompt(kind, cases, report):
    """build-develop-prompt.sh's arguments after <test-cmd> for the answer's red: `red <case>`, `repair <case>
    <superseded>…`, `supersede <case>…` and `missing <behaviour>`, the report being the brief of the last three."""
    if kind == "red":
        return cases[:1]
    if kind == "repair":
        return [cases[0], report] + cases[1:]
    if kind == "supersede":
        return [report] + cases
    return [report]


def waited(wt, n, where, name):
    """A leaf's wait; any exit but 0 stops at <where> with that code."""
    code = fused.wait(wt, n, NAME, name)
    if code != 0:
        raise fused.Stop(where, "wait-leaf.sh %s exit %d" % (name, code), code)


def edited(wt, values):
    """The rerouted red's report: the case it edited, to verify, and every test path the re-record covers."""
    got = fused.report("leaf", wt, ".tdd/%s.out" % values["leaf"], "TEST_PATH", "TARGET_TEST", "AGAINST_UNMODIFIED")
    if got["AGAINST_UNMODIFIED"] in ("PASSES", "UNTESTABLE", "HOLDS"):  # no failing test to verify: an answer
        raise fused.Stop("leaf", "AGAINST_UNMODIFIED: " + got["AGAINST_UNMODIFIED"], 1)
    for key in ("TEST_PATH", "TARGET_TEST", "AGAINST_UNMODIFIED"):
        if not got[key] or key == "AGAINST_UNMODIFIED" and got[key] != "FAILS":
            raise fused.Stop("leaf", "no %s: line" % key, 2)
    if values["kind"] == "supersede":  # one report for every named case: no single case is its target
        cases = [[case.partition("::")[0], case] for case in values["cases"]]
    else:
        cases = [[got["TEST_PATH"], got["TARGET_TEST"]]]
    paths = [values["own_path"]] + [path for path, _ in cases]
    return {"verify": cases, "paths": list(dict.fromkeys(paths))}


def verify(step_at, settled, values):
    """verdict-red over the edited case, launched by red-half's own launch, so it takes exactly the red phase's
    run-verdict.sh arguments (RRT10). The leaf launched; None with `red` switched off, the skip marked as Red's
    *Switched off* marks it (RRT7, ADR-0033)."""
    wt, n, step = step_at
    fused.checked("verify", fused.script("tests-frozen.sh"), "check-earlier", LEDGER % n, "--step", step,
                  *[arg for case in values["cases"] for arg in ("--except", case)], cwd=wt)
    if fused_step.verify_switched_off(wt, n, "red"):
        fused.mark("verify", wt, n, step, "verify-red-skipped", "reason=switched-off")
        with open(os.path.join(wt, ".tdd", "verdict-red.exit"), "w") as f:
            f.write("skipped\n")
        return None
    path, target = values["verify"][0]
    red_half.launch_verdict("verify", n, wt, settled, step, {"test_path": path, "target_test": target})
    fused.save_wait(wt, n, NAME, "verdict-red", values)
    return "verdict-red"


def finish(step_at, values, red):
    """The step's frozen tests re-recorded over every test path, the step's own Red case checked (RRT2); exit 1, a
    deleted case named in `.tdd/verify-red.reason`, is a verify-red REJECT (RRT5)."""
    wt, n, step = step_at
    code = fused.call(fused.script("tests-frozen.sh"), "record", "--step", step, "--red-case", values["own"],
                      *values["paths"], cwd=wt, out=".tdd/verify-red.reason")[0]
    if code == 1:
        revise_red(step_at, red, values)
    if code != 0:
        raise fused.Stop("record", fused.label("tests-frozen.sh", "record", "--step", step) + " exit %d" % code, code)
    answered(wt, n)
    return 0


def answered(wt, n):
    """A verify-green REJECT a reroute answered: `.tdd/verdict-green.exit` and green-half's rejected record removed."""
    for path in (os.path.join(wt, ".tdd", "verdict-green.exit"), fused.wait_record(wt, n, "green-half-rejected")):
        with contextlib.suppress(FileNotFoundError):
            os.remove(path)


def revise_red(step_at, red, values):
    """A verify-red REJECT of the rerouted red (RRT5): its reason left in `.tdd/verify-red.reason`, red-half's rejected
    record naming the step, so run-step.sh sends it to revise.sh <n> red as it does red-half's own REJECT. The record
    carries `rerouted`, every test path the reroute's re-record covers, so the revised PASS keeps the step's own Red
    case and records the frozen tests over every path, as a reroute PASS does."""
    reject(step_at, "red-half", "verdict-red", red, rerouted=values["paths"])
    raise Revise("red")


def pending(wt, n, step):
    """(at, values) of this stage's wait record when it names <step> by ledger.same_step; else None, a record another
    step left removed (S1: a record is a cache)."""
    resumed = fused.load_wait(wt, n, NAME)
    if resumed is not None and not ledger.same_step(resumed[1].get("step", ""), step):
        os.remove(fused.wait_record(wt, n, NAME))
        return None
    return resumed


def launch(step_at, settled, report, own, red):
    """The route, then the rerouted red: the `reroute` event, its prompt and its leaf launched (RRT2). (at, values)."""
    wt, n, step = step_at
    shown = fused.label("wrong-test-route.sh", "--spec", SPEC % n, report, own)
    code, said, _ = fused.call(fused.script("wrong-test-route.sh"), "--spec", SPEC % n, report, own, cwd=wt,
                               env=fused.step_env(n, step))
    kind, _, rest = said.strip().partition(" ")
    if code == 3:
        revise_green(step_at, report, red)
    if code in (0, 1) and kind in STOPS:
        raise fused.Stop("route", said.strip(), 1)
    if code != 0 or kind not in RUNS:
        raise fused.Stop("route", shown + " exit %d" % code, 2)
    fused.mark("route", wt, n, step, "reroute", "kind=" + kind, "case=" + rest)
    phase = RUNS[kind]
    leaf = "develop-" + phase
    fast = settled["fast_cmd"]
    fused.checked("launch", fused.script("build-develop-prompt.sh"), phase, SPEC % n, step, fast,
                  *prompt(kind, rest.split(), report), cwd=wt, out=".tdd/%s.prompt" % leaf)
    if kind in ("red", "repair", "missing"):
        cases = [] if kind == "missing" else rest.split()
        fused.checked("launch", fused.script("restore-production.sh"), red["test_path"],
                      *dict.fromkeys(case.partition("::")[0] for case in cases), cwd=wt)
    fused.launch("launch", wt, leaf, "run-leaf.sh", ".tdd/%s.prompt" % leaf, "--permission-mode", "bypassPermissions",
                 env=fused.step_env(n, step, VERI_TEST_CMD=fast), out=".tdd/%s.out" % leaf, err=".tdd/%s.err" % leaf)
    values = {"step": step, "kind": kind, "cases": rest.split(), "report": report, "own": own,
              "own_path": red["test_path"], "leaf": leaf}
    fused.save_wait(wt, n, NAME, leaf, values)
    return leaf, values


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
