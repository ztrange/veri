"""run-step.sh's computation, run in-process: a cycle step's four fused stages in one call, stopping at the first seam
(PRD 038.2)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step
import run_dir

NAME = "run-step"
USAGE = "usage: run-step.sh <n> [--from <stage>] [--hand <stage>]…"
LEDGER = run_dir.ledger("", "%s")
RED = "SKILL.md#Red — one failing test (developer leaf), then verify-red (blind)"
GREEN = "SKILL.md#Green — minimum implementation (developer leaf), then verify-green (blind)"
REFACTOR = "SKILL.md#Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"

# The stages in the order they run -> the heading anchor (`<file>#<heading>`, under the skill's directory) of the
# section whose prose takes over at a stop there (S4).
STAGES = {"red-half": RED, "green-half": GREEN, "refactor-half": REFACTOR, "step-close": REFACTOR}


def main(argv):
    if len(argv) != 1 or not argv[0].isdigit():
        sys.stderr.write(USAGE + "\n")
        return 2
    n = argv[0]
    if fused_step.inputs(NAME + ".sh", n, LEDGER) is None:
        return 2
    out = ""
    for stage, anchor in STAGES.items():
        code, out, _ = fused.call(fused.script(stage + ".sh"), n)
        if code != 0:
            sys.stdout.write("seam=%s code=%d next=%s\n" % (stage, code, "run-step.sh " + n if code == 3 else anchor))
            return code
    sys.stdout.write([line for line in out.splitlines() if line.startswith("next=")][-1] + "\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
