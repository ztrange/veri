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
CALLS = ("wrong-test-route.sh",)


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
    code, said, _ = fused.call(fused.script("wrong-test-route.sh"), "--spec", SPEC % n, report, own, cwd=wt,
                               env=fused.step_env(n, step))
    raise fused.Stop("route", fused.label("wrong-test-route.sh", "--spec", SPEC % n, report, own)
                     + " exit %d" % code, 2)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
