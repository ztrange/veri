"""run-pr.sh's computation, run in-process: the Draft PR step's stages in one call, stopping at its seams
(PRD 038.11)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused

USAGE = "usage: run-pr.sh <n>"
TITLE = "seam=pr-ready-wait code=1 reason=title next=DRAFT-PR.md#4. Draft PR\n"


def main(argv):
    if not argv:
        sys.stderr.write(USAGE + "\n")
        return 2
    for stage in ("branch-gate.sh", "pr-prepare.sh", "pr-checks.sh"):
        fused.call(fused.script(stage), argv[0])
    sys.stdout.write(TITLE)
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
