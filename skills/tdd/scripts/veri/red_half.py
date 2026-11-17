"""red-half.sh's computation, run in-process: a step's Red half on the FAILS path (SKILL.md *Red*, sub-steps 1-3),
made in one call (PRD 027.4)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
from ledger import handed_out

NAME = "red-half"
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = ".tdd/issue-%s.md"
# The step kinds whose Red is not this one (RH1): they run from their own files or need a route's --except.
REFUSED = ("⟦diff-checked⟧", "⟦phases:", "⟦skill-edit⟧", "⟦fixture-repair⟧")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused.inputs(NAME + ".sh", n, LEDGER, SPEC)
    if given is None:
        return 2
    settled, wt = given
    step = fused.first_step(wt, n, handed_out)
    if step is None or any(kind in step for kind in REFUSED):
        sys.stderr.write("red-half.sh: %s\n" % ("no open step" if step is None else "a step its prose runs: " + step))
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
