"""go-red-step.sh's computation, run in-process: a ⟦go-red⟧ step's one stage, a mutation probe on the case the step
names, recorded in the run's mutation record, then step-tick.sh (#4443)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step
import ledger
import run_dir
import tunables
from ledger import handed_out

NAME = "go-red-step"
USAGE = "usage: go-red-step.sh <n>"
LEDGER = run_dir.ledger("", "%s")
RECORD = ".tdd/issue-%s-mutations.md"

# The $S/ scripts this call makes, in the order each is first made.
CALLS = ("detect-test-command.sh", "mutation-probe.sh", "step-tick.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    step = fused_step.first_step(wt, n, handed_out)
    if step is None or not ledger.is_go_red(step):
        sys.stderr.write("go-red-step.sh: no open %s step in %s\n" % (ledger.GO_RED_MARK, LEDGER % n))
        return 2
    probe = ledger.go_red_probe(step)
    if probe is None:
        sys.stderr.write("go-red-step.sh: the open %s step names no probe `<file>` `<old>` → `<new>` on `<case>`\n"
                         % ledger.GO_RED_MARK)
        return 2
    path, old, new, case = probe
    fused.call(fused.script("mutation-probe.sh"), path, old, new, "--", *command(wt, case), cwd=wt,
               env=tunables.with_values(VERI_MUTATION_RECORD=RECORD % n), out=".tdd/go-red-probe.out")
    fused.checked("tick", fused.script("step-tick.sh"), n, cwd=wt)
    return 0


def command(wt, case):
    """The probe's command: the `veri: one test file:` command on <case>, else the all-tier one; a
    detect-test-command.sh exit but 0 or 3 stops with exit 2."""
    code, alone, _ = fused.call(fused.script("detect-test-command.sh"), "--tier", "one test file", cwd=wt)
    if code == 0:
        return ("sh", "-c", alone.strip(), "sh", case)
    if code == 3:
        return ("sh", "-c", fused.checked("probe", fused.script("detect-test-command.sh"), "--tier", "all",
                                          cwd=wt).strip())
    raise fused.Stop("probe", "detect-test-command.sh --tier one test file exit %d" % code, 2)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
