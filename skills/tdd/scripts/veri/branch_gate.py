"""branch-gate.sh's computation, run in-process: on entering the Draft PR step, whether CI stands in for the branch's
full run and, under `local`, that run and its recorded time (DRAFT-PR.md's opening paragraphs), made in one call
(PRD 027.7)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step
import run_dir
from ledger import handed_out

NAME = "branch-gate"
USAGE = "usage: branch-gate.sh <n>"
LEDGER = run_dir.ledger("", "%s")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    step = fused_step.first_step(wt, n, handed_out)
    if step is not None:
        sys.stderr.write("branch-gate.sh: an unchecked step is left, next-unchecked.sh would hand it out: %s\n" % step)
        return 2
    fused.checked("opening", fused.script("branch-suite.sh"), cwd=wt)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
