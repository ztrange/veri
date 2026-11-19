"""revise.sh's computation, run in-process: REVISE.md's revise loop for one rejected phase (sub-steps 1-5), sliced
like the fused halves of a step (PRD 038.9)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import shutil
import sys

import fused
import fused_step
import run_dir
import tunables
from ledger import handed_out

NAME = "revise"
USAGE = "usage: revise.sh <n> <phase>  (phase: red, green or refactor)"
PHASES = ("red", "green", "refactor")
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = run_dir.ledger("", "%s")

# The $S/ scripts this call makes, in the order each is first made.
CALLS = ("build-develop-prompt.sh", "comment.sh", "event.sh", "stop-requested.sh", "detach-leaf.sh", "supervise.sh",
         "run-leaf.sh", "wait-leaf.sh", "step-cost.sh", "step-budget.sh", "tests-frozen.sh", "run-verdict.sh")


def main(argv):
    if len(argv) != 2 or not argv[0].isdigit() or argv[1] not in PHASES:
        sys.stderr.write(USAGE + "\n")
        return 2
    try:
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
    step = fused_step.first_step(wt, n, handed_out)
    red = fused_step.record(NAME, wt, n, step)
    if red is None:
        return 1
    resumed = fused.load_wait(wt, n, NAME)
    if resumed is None:
        values = {"phase": phase, "k": 1, "test_path": red["test_path"], "target_test": red["target_test"]}
        at = attempt(n, wt, settled, step, values)
    else:
        at, values = resumed
    if at.startswith("revise-"):
        code = fused.wait(wt, n, NAME, at)
        if code != 0:
            raise fused.Stop("3", "wait-leaf.sh %s exit %d" % (at, code), code)
        fused_step.cost_check(wt, step)
        fused.checked("4", fused.script("tests-frozen.sh"), "check", "--step", step, cwd=wt)
        at = verify(n, wt, settled, step, values)
    fused.wait(wt, n, NAME, at)


def attempt(n, wt, settled, step, values):
    """REVISE.md sub-steps 2 and 3 for attempt k: the reason kept as `.tdd/verify-<phase>-<k>.reason`, the revise
    prompt, the Revise comment, the `revise` mark and the revise leaf's launch. The leaf launched."""
    phase, k = values["phase"], values["k"]
    shutil.copyfile(os.path.join(wt, ".tdd", "verify-%s.reason" % phase),
                    os.path.join(wt, ".tdd", "verify-%s-%d.reason" % (phase, k)))
    fast = settled["fast_cmd"]
    leaf = "revise-%s-%d" % (phase, k)
    fused.checked("2", fused.script("build-develop-prompt.sh"), "revise", phase, SPEC % n, step, fast,
                  ".tdd/verify-%s.reason" % phase, fast, cwd=wt, out=".tdd/%s.prompt" % leaf)
    fused.checked("2", fused.script("comment.sh"), n, "revise", phase, str(k), cwd=wt)
    fused.mark("2", wt, n, step, "revise", "budget=" + tunables.get("REVISE_BUDGET", unless_empty=True),
               VERI_PHASE=phase, VERI_ATTEMPT=str(k))
    fused.launch("3", wt, leaf, "run-leaf.sh", ".tdd/%s.prompt" % leaf, "--permission-mode", "bypassPermissions",
                 env=fused.step_env(n, step, VERI_TEST_CMD=fast), out=".tdd/%s.out" % leaf, err=".tdd/%s.err" % leaf,
                 clear=(".tdd/red-prediction.md", ".tdd/red-run-output.txt"))
    fused.save_wait(wt, n, NAME, leaf, values)
    return leaf


def verify(n, wt, settled, step, values):
    """REVISE.md sub-step 5's re-verify: verdict-<phase> with exactly the phase stage's run-verdict.sh arguments and
    the run's recorded branch base. The leaf launched."""
    phase, fast = values["phase"], settled["fast_cmd"]
    fused.launch("5", wt, "verdict-" + phase, "run-verdict.sh", "--step", step, "--fast-cmd", fast,
                 "--branch-base", fused_step.branch_base("5", wt, n), phase, SPEC % n,
                 values["test_path"], values["target_test"], env=fused.step_env(n, step, VERI_TEST_CMD=fast),
                 out=".tdd/verify-%s.reason" % phase, err=".tdd/verify-%s.err" % phase)
    fused.save_wait(wt, n, NAME, "verdict-" + phase, values)
    return "verdict-" + phase


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
