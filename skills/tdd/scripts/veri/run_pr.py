"""run-pr.sh's computation, run in-process: the Draft PR step's stages in one call, stopping at its seams
(PRD 038.11)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import run_dir

USAGE = "usage: run-pr.sh <n> [--from <stage>] [--hand <stage>]..."
ANCHOR = "DRAFT-PR.md#4. Draft PR"
TITLE = "seam=pr-ready-wait code=1 reason=title next=%s\n" % ANCHOR
STACKED = "seam=pr-ready-wait code=1 reason=stacked next=%s\n" % ANCHOR
BODY = "seam=done code=1 reason=body next=%s\n" % ANCHOR
EARLY = ("branch-gate.sh", "pr-prepare.sh", "pr-checks.sh", "verify-branch.sh")
LATE = ("pr-ready-wait.sh", "pr-finish.sh")
CALLS = EARLY + LATE


def ledger_sha(wt, n):
    """The sha of the ledger's last commit; "" when git fails or names none, which no record ever matches."""
    try:
        return fused.run_script("git", "log", "-1", "--format=%H", "--", run_dir.ledger("", "%s") % n, cwd=wt)[1].strip()
    except Exception:
        return ""


def stacked(wt, n):
    return os.path.exists(os.path.join(wt, ".tdd", "issue-%s-base" % n))


def record(wt, n, seam):
    with open(fused.settled_file(wt, n, "run-pr"), "w") as f:
        f.write("seam=%s\nsha=%s\n" % (seam, ledger_sha(wt, n)))


def run_stages(n, wt, stages, hands):
    """Call <stages> in order, stopping before one in <hands> and at the first non-zero exit (RPR3, RPR5): None when
    every one exited 0, else the call's exit code. A 3 records its stage, so the next call resumes there. fused.call prints each call's line and its stdout, so nothing here prints them again (RPR10)."""
    for stage in stages:
        if stage in hands:
            sys.stdout.write("seam=%s code=1 reason=hand next=%s\n" % (stage[:-3], ANCHOR))
            return 1
        code = fused.call(fused.script(stage), n)[0]
        if code not in (0, 1, 2, 3):
            sys.stderr.write("run-pr.sh: %s exited %d\n" % (stage[:-3], code))
            return 2
        if code:
            if code == 3:
                record(wt, n, stage[:-3])
            sys.stdout.write("seam=%s code=%d next=%s\n" % (stage[:-3], code, "run-pr.sh %s" % n if code == 3 else ANCHOR))
            return code
    return None


def run_late(n, wt, first, hands):
    code = run_stages(n, wt, LATE[LATE.index(first) if first else 0:], hands)
    if code is not None:
        return code
    record(wt, n, "body")
    sys.stdout.write(BODY)
    return 1


def run_early(n, wt, first, hands):
    code = run_stages(n, wt, () if first in LATE else EARLY[EARLY.index(first) if first else 0:], hands)
    if code is not None:
        return code
    record(wt, n, "title")
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
    found = fused_step.inputs("run-pr.sh", n, run_dir.ledger("", "%s"))
    if found is None:
        return 2
    wt = found[1]
    path = fused.settled_file(wt, n, "run-pr")
    held = open(path).read() if os.path.exists(path) else ""
    seam = next((l[5:] for l in held.splitlines() if l.startswith("seam=")), "")
    sha = ledger_sha(wt, n)
    if first is None and sha and "sha=%s\n" % sha in held:
        if seam == "body":
            return 0
        # A stage's 3 resumes at that stage, the title seam at pr-ready-wait: in a stacked run that is the stacked stop
        # again, no stage called (RPR4, RPR6).
        first = seam + ".sh" if seam + ".sh" in CALLS else LATE[0] if seam == "title" else None
    if not stacked(wt, n) and first in LATE:
        return run_late(n, wt, first, hands)
    return run_early(n, wt, first, hands)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
