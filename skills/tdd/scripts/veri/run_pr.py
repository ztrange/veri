"""run-pr.sh's computation, run in-process: the Draft PR step's stages in one call, stopping at its seams
(PRD 038.11)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import run_dir

USAGE = "usage: run-pr.sh <n>"
TITLE = "seam=pr-ready-wait code=1 reason=title next=DRAFT-PR.md#4. Draft PR\n"


BODY = "seam=done code=1 reason=body next=DRAFT-PR.md#4. Draft PR\n"


def ledger_sha(wt, n):
    try:
        return fused.run_script("git", "log", "-1", "--format=%H", "--", run_dir.ledger("", "%s") % n, cwd=wt)[1].strip()
    except Exception:
        return ""


def main(argv):
    if not argv:
        sys.stderr.write(USAGE + "\n")
        return 2
    n = argv[0]
    wt = fused_step.inputs("run-pr.sh", n)[1]
    record = fused.settled_file(wt, n, "run-pr")
    if os.path.exists(record):
        for stage in ("pr-ready-wait.sh", "pr-finish.sh"):
            _, out, _ = fused.call(fused.script(stage), n)
        sys.stdout.write("".join(out.splitlines(True)[-2:]))
        sys.stdout.write(BODY)
        return 1
    for stage in ("branch-gate.sh", "pr-prepare.sh", "pr-checks.sh"):
        fused.call(fused.script(stage), argv[0])
    with open(record, "w") as f:
        f.write("seam=title\nsha=%s\n" % ledger_sha(wt, n))
    sys.stdout.write(TITLE)
    return 1


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
