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
STAGES = ("red-half", "green-half", "refactor-half", "step-close")


def main(argv):
    if len(argv) != 1 or not argv[0].isdigit():
        sys.stderr.write(USAGE + "\n")
        return 2
    n = argv[0]
    if fused_step.inputs(NAME + ".sh", n, LEDGER) is None:
        return 2
    out = ""
    for stage in STAGES:
        _, out, _ = fused.call(fused.script(stage + ".sh"), n)
    sys.stdout.write([line for line in out.splitlines() if line.startswith("next=")][-1] + "\n")
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
