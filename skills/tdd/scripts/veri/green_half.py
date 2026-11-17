"""green-half.sh's computation, run in-process: a step's Green half on the PASS path (SKILL.md *Green*, sub-steps
1-3), made in one call after a clean red-half.sh (PRD 027.5)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import replaces_case
from ledger import handed_out

NAME = "green-half"
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
    step = fused.first_step(wt, n, handed_out)
    if step is None or red.get("step") != step:
        sys.stderr.write("green-half.sh: .tdd/issue-%s-red-half names another step than the open one\n" % n)
        return 2
    if replaces_case.is_replaces_case_step(step) or "⟦ci-repair⟧" in step:
        sys.stderr.write("green-half.sh: a step its prose runs: %s\n" % step)
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
