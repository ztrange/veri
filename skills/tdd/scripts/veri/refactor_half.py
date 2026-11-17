"""refactor-half.sh's computation, run in-process: a step's first refactor pass (SKILL.md *Refactor loop*, sub-steps
1, 2, 5 and 6 up to its PASS branch), made in one call (PRD 027.6)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
from next_pending_refactor import refactor_pending

NAME = "refactor-half"
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = ".tdd/issue-%s.md"
RED_HALF = ".tdd/issue-%s-red-half"


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused.inputs(NAME + ".sh", n, LEDGER, SPEC, RED_HALF)
    if given is None:
        return 2
    settled, wt = given
    red = fused.read_settled(os.path.join(wt, RED_HALF % n))
    step = fused.first_step(wt, n, refactor_pending)
    if step is None or red.get("step") != step:
        sys.stderr.write("refactor-half.sh: %s\n" % ("no refactor-pending step" if step is None else
                                                     ".tdd/issue-%s-red-half names another step" % n))
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
