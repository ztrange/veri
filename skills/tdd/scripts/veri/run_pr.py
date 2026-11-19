"""run-pr.sh's computation, run in-process: the Draft PR step's stages in one call, stopping at its seams
(PRD 038.11)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import run_dir

USAGE = "usage: run-pr.sh <n>"
ANCHOR = "DRAFT-PR.md#4. Draft PR"
TITLE = "seam=pr-ready-wait code=1 reason=title next=%s\n" % ANCHOR
STACKED = "seam=pr-ready-wait code=1 reason=stacked next=%s\n" % ANCHOR
BODY = "seam=done code=1 reason=body next=%s\n" % ANCHOR
EARLY = ("branch-gate.sh", "pr-prepare.sh", "pr-checks.sh")
LATE = ("pr-ready-wait.sh", "pr-finish.sh")
CALLS = EARLY + LATE


def ledger_sha(wt, n):
    try:
        return fused.run_script("git", "log", "-1", "--format=%H", "--", run_dir.ledger("", "%s") % n, cwd=wt)[1].strip()
    except Exception:
        return ""


def stacked(wt, n):
    return os.path.exists(os.path.join(wt, ".tdd", "issue-%s-base" % n))


def run_late(n, wt, first):
    for stage in LATE[LATE.index(first) if first else 0:]:
        code, out, _ = fused.call(fused.script(stage), n)
        sys.stdout.write("%s %s exit %d\n" % (stage, n, code))
    sys.stdout.write("".join(out.splitlines(True)[-2:]))
    with open(fused.settled_file(wt, n, "run-pr"), "w") as f:
        f.write("seam=body\nsha=%s\n" % ledger_sha(wt, n))
    sys.stdout.write(BODY)
    return 1


def run_early(n, wt, first, hands):
    for stage in () if first in LATE else EARLY[EARLY.index(first) if first else 0:]:
        if stage in hands:
            sys.stdout.write("seam=%s code=1 reason=hand next=%s\n" % (stage[:-3], ANCHOR))
            return 1
        code, out, _ = fused.call(fused.script(stage), n)
        sys.stdout.write("%s %s exit %d\n" % (stage, n, code))
        if code not in (0, 1, 2, 3):
            sys.stderr.write("run-pr.sh: %s exited %d\n" % (stage[:-3], code))
            return 2
        if code in (1, 2, 3):
            sys.stdout.write(out)
            sys.stdout.write("seam=%s code=%d next=%s\n" % (stage[:-3], code, "run-pr.sh %s" % n if code == 3 else ANCHOR))
            return code
    with open(fused.settled_file(wt, n, "run-pr"), "w") as f:
        f.write("seam=title\nsha=%s\n" % ledger_sha(wt, n))
    sys.stdout.write(STACKED if stacked(wt, n) else TITLE)
    return 1


def main(argv):
    if not argv:
        sys.stderr.write(USAGE + "\n")
        return 2
    n = argv[0]
    stages = EARLY + LATE
    rest = argv[1:]
    while rest:
        if rest[0] not in ("--from", "--hand") or "".join(rest[1:2]) + ".sh" not in stages:
            sys.stderr.write(USAGE + "\n")
            return 2
        rest = rest[2:]
    first = argv[argv.index("--from") + 1] + ".sh" if "--from" in argv else None
    hands = [argv[i + 1] + ".sh" for i, a in enumerate(argv) if a == "--hand"]
    wt = fused_step.inputs("run-pr.sh", n)[1]
    record = fused.settled_file(wt, n, "run-pr")
    held = open(record).read() if os.path.exists(record) else ""
    if first is None and "sha=%s\n" % ledger_sha(wt, n) in held and "seam=body\n" in held:
        return 0
    if not stacked(wt, n) and (first in LATE or (first is None and "sha=%s\n" % ledger_sha(wt, n) in held)):
        return run_late(n, wt, first)
    return run_early(n, wt, first, hands)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
