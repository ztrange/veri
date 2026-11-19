"""reroute.sh's computation, run in-process: wrong-test-route.sh's answer for the open step run through the rerouted
red leaf, verify-red and the frozen-test re-record (SKILL.md *Green*), sliced like the fused halves of a step
(PRD 038.10)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step
import run_dir
from ledger import handed_out

NAME = "reroute"
USAGE = "usage: reroute.sh <n> <report>"
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = run_dir.ledger("", "%s")

# The $S/ scripts this call makes, in the order each is first made.
CALLS = ("wrong-test-route.sh", "event.sh", "build-develop-prompt.sh", "stop-requested.sh", "detach-leaf.sh",
         "supervise.sh", "run-leaf.sh", "wait-leaf.sh")
# The answers this stage runs (S12) -> the rerouted red's prompt phase, its leaf being `develop-<phase>`.
RUNS = {"red": "red-contradicted"}


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
        at, values = launch(n, wt, settled, step, report, own)
    else:
        at, values = resumed
    fused.wait(wt, n, NAME, at)
    return 0


def launch(n, wt, settled, step, report, own):
    """The route, then the rerouted red: the `reroute` event, its prompt and its leaf launched (RRT2). (at, values)."""
    shown = fused.label("wrong-test-route.sh", "--spec", SPEC % n, report, own)
    code, said, _ = fused.call(fused.script("wrong-test-route.sh"), "--spec", SPEC % n, report, own, cwd=wt,
                               env=fused.step_env(n, step))
    kind, _, rest = said.strip().partition(" ")
    if code != 0 or kind not in RUNS:
        raise fused.Stop("route", shown + " exit %d" % code, 2)
    fused.mark("route", wt, n, step, "reroute", "kind=" + kind, "case=" + rest)
    phase = RUNS[kind]
    leaf = "develop-" + phase
    fast = settled["fast_cmd"]
    fused.checked("launch", fused.script("build-develop-prompt.sh"), phase, SPEC % n, step, fast, *rest.split(),
                  cwd=wt, out=".tdd/%s.prompt" % leaf)
    fused.launch("launch", wt, leaf, "run-leaf.sh", ".tdd/%s.prompt" % leaf, "--permission-mode", "bypassPermissions",
                 env=fused.step_env(n, step, VERI_TEST_CMD=fast), out=".tdd/%s.out" % leaf, err=".tdd/%s.err" % leaf)
    values = {"kind": kind, "cases": rest.split(), "report": report, "own": own, "leaf": leaf}
    fused.save_wait(wt, n, NAME, leaf, values)
    return leaf, values


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
