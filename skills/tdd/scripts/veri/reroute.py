"""reroute.sh's computation, run in-process: wrong-test-route.sh's answer for the open step run through the rerouted
red leaf, verify-red and the frozen-test re-record (SKILL.md *Green*), sliced like the fused halves of a step
(PRD 038.10)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step
import red_half
import run_dir
from ledger import handed_out

NAME = "reroute"
USAGE = "usage: reroute.sh <n> <report>"
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = run_dir.ledger("", "%s")

# The $S/ scripts this call makes, in the order each is first made.
CALLS = ("wrong-test-route.sh", "event.sh", "build-develop-prompt.sh", "stop-requested.sh", "detach-leaf.sh",
         "supervise.sh", "run-leaf.sh", "wait-leaf.sh", "step-cost.sh", "step-budget.sh", "extract-result.sh",
         "run-verdict.sh", "tests-frozen.sh")
# The answers this stage runs (S12) -> the rerouted red's prompt phase, its leaf being `develop-<phase>`.
RUNS = {"red": "red-contradicted", "repair": "red-repair", "supersede": "red-supersede", "missing": "red-missing"}

# The answers it stops on with exit 1, naming them (RRT4, S11, S12): plan growth (`prep`, `later`, `fixture`), the
# `diff` verifier over a stash snapshot (`supersede-diff`), and the two exhaustions, whose bail is the conductor's.
STOPS = ("prep", "later", "fixture", "supersede-diff", "missing-exhausted", "repair-exhausted")


def main(argv):
    if len(argv) != 2 or not argv[0].isdigit():
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


def run(n, report):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER, SPEC)
    if given is None:
        return 2
    settled, wt = given
    step = fused_step.first_step(wt, n, handed_out)
    red = fused_step.record(NAME, wt, n, step)
    if red is None:
        return 1
    own = fused_step.red_test_id(red["test_path"], red["target_test"])
    resumed = fused.load_wait(wt, n, NAME)
    if resumed is None:
        at, values = launch(n, wt, settled, step, report, own, red["test_path"])
    else:
        at, values = resumed
    if at == values["leaf"]:
        waited(wt, n, "leaf", at)
        fused_step.cost_check(wt, step)
        values.update(edited(wt, values))
        at = verify(n, wt, settled, step, values)
    while at == "verdict-red":
        waited(wt, n, "verify", at)
        values["verify"] = values["verify"][1:]
        at = verify(n, wt, settled, step, values) if values["verify"] else None
    return finish(wt, step, values)


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
    if got["AGAINST_UNMODIFIED"] in ("PASSES", "UNTESTABLE"):  # a pin is verify-pin's, by hand (PIN.md)
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


def verify(n, wt, settled, step, values):
    """verdict-red over the edited case, launched by red-half's own launch, so it takes exactly the red phase's
    run-verdict.sh arguments (RRT10). The leaf launched."""
    path, target = values["verify"][0]
    red_half.launch_verdict("verify", n, wt, settled, step, {"test_path": path, "target_test": target})
    fused.save_wait(wt, n, NAME, "verdict-red", values)
    return "verdict-red"


def finish(wt, step, values):
    """The step's frozen tests re-recorded over every test path, the step's own Red case checked (RRT2)."""
    fused.checked("record", fused.script("tests-frozen.sh"), "record", "--step", step, "--red-case", values["own"],
                  *values["paths"], cwd=wt, out=".tdd/verify-red.reason")
    return 0


def launch(n, wt, settled, step, report, own, own_path):
    """The route, then the rerouted red: the `reroute` event, its prompt and its leaf launched (RRT2). (at, values)."""
    shown = fused.label("wrong-test-route.sh", "--spec", SPEC % n, report, own)
    code, said, _ = fused.call(fused.script("wrong-test-route.sh"), "--spec", SPEC % n, report, own, cwd=wt,
                               env=fused.step_env(n, step))
    kind, _, rest = said.strip().partition(" ")
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
    fused.launch("launch", wt, leaf, "run-leaf.sh", ".tdd/%s.prompt" % leaf, "--permission-mode", "bypassPermissions",
                 env=fused.step_env(n, step, VERI_TEST_CMD=fast), out=".tdd/%s.out" % leaf, err=".tdd/%s.err" % leaf)
    values = {"kind": kind, "cases": rest.split(), "report": report, "own": own, "own_path": own_path, "leaf": leaf}
    fused.save_wait(wt, n, NAME, leaf, values)
    return leaf, values


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
