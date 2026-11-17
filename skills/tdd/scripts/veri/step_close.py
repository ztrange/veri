"""step-close.sh's computation, run in-process: a step's close-out after a passing or skipped verify-refactor
(SKILL.md *Refactor loop*, sub-step 6's PASS branch), made in one call after a clean refactor-half.sh (PRD 027.8)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import run_dir
from next_pending_refactor import refactor_pending

NAME = "step-close"
USAGE = "usage: step-close.sh <n>"
LEDGER = run_dir.ledger("", "%s")
REFACTOR_HALF = ".tdd/issue-%s-refactor-half"


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER, REFACTOR_HALF)
    if given is None:
        return 2
    _, wt = given
    step = fused_step.first_step(wt, n, refactor_pending)
    half = read_half(wt, n)
    if step is None or half.get("step", [None])[0] != step:
        sys.stderr.write("step-close.sh: %s\n" % ("no refactor-pending step" if step is None else
                                                 ".tdd/issue-%s-refactor-half names another step" % n))
        return 2
    for uncovered in half.get("uncovered_spec", []):
        raise fused.Stop("6", "uncovered_spec=" + uncovered, 1)
    return 0


def read_half(wt, n):
    """{key: [its values, in order]} of .tdd/issue-<n>-refactor-half, which may hold a key more than once."""
    values = {}
    with open(os.path.join(wt, REFACTOR_HALF % n), encoding="utf-8", errors="surrogateescape") as f:
        for line in f.read().splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values.setdefault(key, []).append(value)
    return values


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
