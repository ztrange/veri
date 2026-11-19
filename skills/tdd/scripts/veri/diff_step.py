"""diff-step.sh's computation, run in-process: a ⟦diff-checked⟧ step's clean path (DIFF-CHECKED.md), sliced like the
fused halves of a step, ending on step-tick.sh (PRD 038.3)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step
import run_dir
from ledger import handed_out

NAME = "diff-step"
USAGE = "usage: diff-step.sh <n>"
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = run_dir.ledger("", "%s")
KIND = "⟦diff-checked⟧"

# The $S/ scripts this call makes, in the order each is first made (git aside).
CALLS = ("build-develop-prompt.sh", "stop-requested.sh", "detach-leaf.sh", "supervise.sh", "run-leaf.sh",
         "wait-leaf.sh", "suite-reported.sh", "diff-leaf-deviation.sh", "run-verdict.sh", "pin-recheck.sh",
         "step-tick.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER, SPEC)
    if given is None:
        return 2
    settled, wt = given
    step = fused_step.first_step(wt, n, handed_out)
    if step is None or KIND not in step:
        sys.stderr.write("diff-step.sh: no open %s step in %s\n" % (KIND, LEDGER % n))
        return 2
    resumed = fused.load_wait(wt, n, NAME)
    at, values = resumed if resumed is not None else develop(n, wt, settled, step)
    if at == "develop-diff":
        code = fused.wait(wt, n, NAME, "develop-diff")
        if code != 0:
            raise fused.Stop("develop", "wait-leaf.sh develop-diff exit %d" % code, code)
        at = verify(n, wt, settled, step, values)
    if at == "verdict-diff":
        code = fused.wait(wt, n, NAME, "verdict-diff", rejected_step=step)
        if code != 0:
            raise fused.Stop("verify", "wait-leaf.sh verdict-diff exit %d" % code, code)
    return finish(n, wt, values)


def develop(n, wt, settled, step):
    """The step base sha, a committed fact (the ledger's last commit, DIFF-CHECKED.md), then the develop-diff leaf's
    launch. (at, values) for the wait."""
    base = fused.checked("develop", "git", "log", "-1", "--format=%H", "--", LEDGER % n, cwd=wt).strip()
    fast = settled["fast_cmd"]
    fused.checked("develop", fused.script("build-develop-prompt.sh"), "diff", SPEC % n, step, fast, fast, cwd=wt,
                  out=".tdd/develop-diff.prompt")
    fused.launch("develop", wt, "develop-diff", "run-leaf.sh", ".tdd/develop-diff.prompt", "--permission-mode",
                 "bypassPermissions", env=fused.step_env(n, step, VERI_TEST_CMD=fast), out=".tdd/develop-diff.out",
                 err=".tdd/develop-diff.err")
    values = {"step_base": base, "leaf": "develop-diff"}
    fused.save_wait(wt, n, NAME, "develop-diff", values)
    return "develop-diff", values


def verify(n, wt, settled, step, values):
    """The leaf's checks, then the verifier: suite-reported.sh (its 2, no SUITE: line, stops for the conductor's
    adjudication), diff-leaf-deviation.sh (0 a deviation recorded, 3 none, both going on), then verdict-diff."""
    leaf = values["leaf"]
    fused.checked("develop", fused.script("suite-reported.sh"), leaf, cwd=wt, err=".tdd/suite-reported.err")
    fused.checked("develop", fused.script("diff-leaf-deviation.sh"), leaf, values["step_base"], LEDGER % n, cwd=wt,
                  ok=(0, 3))
    launch_verdict("verify", n, wt, settled, step, values)
    fused.save_wait(wt, n, NAME, "verdict-diff", values)
    return "verdict-diff"


def launch_verdict(where, n, wt, settled, step, values):
    """verdict-diff's launch, stopping at <where>: the one set of run-verdict.sh arguments diff-step.sh and revise.sh's
    re-verify share, against the step base taken before the develop-diff leaf ran (REVISE.md *The diff phase*)."""
    fast = settled["fast_cmd"]
    fused.launch(where, wt, "verdict-diff", "run-verdict.sh", "--step", step, "--fast-cmd", fast,
                 "--branch-base", fused_step.branch_base(where, wt, n), "diff", SPEC % n, values["step_base"],
                 env=fused.step_env(n, step, VERI_TEST_CMD=fast), out=".tdd/verify-diff.reason",
                 err=".tdd/verify-diff.err")


def finish(n, wt, values):
    """The PASS branch: pin-recheck.sh over the step's range (0 or 3 leave the receipt the tick needs), then
    step-tick.sh, whose lines end this call's."""
    fused.checked("pin", fused.script("pin-recheck.sh"), "--branch-base", fused_step.branch_base("pin", wt, n),
                  values["step_base"], cwd=wt, ok=(0, 3))
    fused.checked("tick", fused.script("step-tick.sh"), n, cwd=wt)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
