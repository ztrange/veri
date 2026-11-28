"""pr-prepare.sh's computation, run in-process: the Draft PR step's sub-step 1 up to the structural pass's skip (the
two questions, the rebase, the regrade block, the rebased tip's suite when owed, the pinned-lease push, the
refactor-owed list), made in one call (PRD 027.9, amended: it stops after RB7)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import run_dir
import tunables

NAME = "pr-prepare"
USAGE = "usage: pr-prepare.sh <n>"
LEDGER = run_dir.ledger("", "%s")
REGRADE = "regrade-%s"  # the regrade block's detach-command.sh name
RUN = "rebased-full-%s"  # the rebased tip's detach-command.sh name: .tdd/rebased-full-<n>.out and .exit
DETACH = fused.script("detach-command.sh")
SUBJECT = "docs: regrade the prose the branch signed (#%s)"  # the regrade commit's one subject (PRG1)

# The $S/ scripts this call makes, in the order each is first made (git aside; grade-prose.sh here is only its
# `--signed` listing, the grading being the detached regrade block's); unit/test_pr_prepare.py fails when one is a
# script DRAFT-PR.md's sub-step 1 does not name (FC19).
CALLS = ("next-pending-refactor.sh", "rebase-onto-default.sh", "grade-prose.sh", "detach-command.sh",
         "rebased-tip-suite.sh", "detect-test-command.sh", "push-branch.sh", "refactor-owed.sh", "event.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    resumed = fused.load_wait(wt, n, NAME)
    if resumed is None:
        at, values = REGRADE % n, rebase(wt, n)
    else:
        at, values = resumed
    if at == REGRADE % n:
        values = regraded(wt, n, values)
    if values["rebased"] == "1":
        if values["rebased_tip_suite"] == "local":
            code = fused.call(DETACH, "wait", RUN % n, cwd=wt)[0]
            if code == 3:
                raise fused.Waiting(RUN % n)
            os.remove(fused.wait_record(wt, n, NAME))
            if code != 0:
                raise fused.Stop("1", "detach-command.sh wait %s exit %d" % (RUN % n, code), code)
        push(wt, values["rebased_from"])
    skip(wt, n)
    return fused.settle(wt, n, NAME, ["%s=%s" % (key, values[key]) for key in
                                      ("rebased", "rebased_from", "rebased_tip_suite")])


def rebase(wt, n):
    """The two questions, the rebase and the regrade block started detached (RB1-RB3): the values settled so far, the
    regrade's wait recorded so a second call only waits again (FC6)."""
    questions(wt, n)
    code, said, _ = fused.call(fused.script("rebase-onto-default.sh"), cwd=wt)
    if code not in (0, 3):
        raise fused.Stop("1", "rebase-onto-default.sh exit %d" % code, code)
    values = {"rebased": "0", "rebased_from": "", "rebased_tip_suite": "none", "before": regrade(wt, n)}
    if code == 0:
        values.update(rebased="1", rebased_from=(said.splitlines() or [""])[0].strip())
    fused.save_wait(wt, n, NAME, REGRADE % n, values)
    return values


def regraded(wt, n, values):
    """The regrade block's wait, its commit (PRG1, PRG2) and, after a rebase, the rebased tip's suite started (RB3-RB4);
    the block's highest exit 1 or 2 stops it. The local run's wait recorded so a second call only waits again (FC6)."""
    code, said, _ = fused.call(DETACH, "wait", REGRADE % n, cwd=wt)
    if code == 3:
        raise fused.Waiting(REGRADE % n)
    os.remove(fused.wait_record(wt, n, NAME))
    if code == 1:
        highest = int((said.split() or ["1"])[-1])
        raise fused.Stop("1", "regrade block exit %d" % highest, highest)
    if code != 0:
        raise fused.Stop("1", "detach-command.sh wait %s exit %d" % (REGRADE % n, code), 2)
    before = set(values.pop("before"))
    regraded = [line[3:] for line in porcelain(wt) if line not in before and line[:2] in (" M", "M ")
                and os.path.basename(line[3:]) == "GRADED"]
    commit(wt, n, regraded)
    if values["rebased"] == "1":
        values["rebased_tip_suite"] = tip_suite(wt, n)
        if values["rebased_tip_suite"] == "local":
            fused.save_wait(wt, n, NAME, RUN % n, values)
    return values


def default_branch(wt):
    """The default branch the regrade block names as `origin/<default>`, read without the network."""
    import git
    return git.default_branch(cwd=wt, remote=False)


# The regrade block as one detached command: `sh -c BLOCK sh <$S> <requirements> <unit> …`, the highest exit of its
# grade-prose.sh calls its own (RB3).
BLOCK = ('S=$1; shift; rc=0; while [ "$#" -gt 1 ]; do "$S/grade-prose.sh" "$1" "$2" </dev/null || '
         '{ r=$?; [ "$r" -gt "$rc" ] && rc=$r; }; shift 2; done; '
         '"$S/grade-prose.sh" --convert </dev/null || { r=$?; [ "$r" -gt "$rc" ] && rc=$r; }; exit "$rc"')


def regrade(wt, n):
    """Sub-step 1's regrade block (RB3) started detached as `regrade-<n>`: every unit the branch signed since its merge
    base with origin/<default>, as `grade-prose.sh --signed` lists it (decoded, beside its REQUIREMENTS.md), then
    `grade-prose.sh --convert`. A failing git call or listing is no answer (exit 2), never its own code.
    Returns the porcelain before the block, against which the files it modified are read."""
    default = default_branch(wt)
    if not default:
        raise fused.Stop("1", "no default branch for the regrade block", 2)
    base = answered("git", "merge-base", "HEAD", "origin/" + default, cwd=wt).strip()
    listed = answered(fused.script("grade-prose.sh"), "--signed", base, cwd=wt)
    before = porcelain(wt)
    pairs = [arg for line in listed.splitlines() if line for arg in line.split("\t", 1)]
    scripts = os.path.dirname(fused.script("grade-prose.sh"))
    fused.checked("1", DETACH, "start", REGRADE % n, "sh", "-c", BLOCK, "sh", scripts, *pairs, cwd=wt)
    return before


def answered(*args, **kw):
    """fused.checked at sub-step 1, a nonzero exit stopping it with exit 2 (no answer could be obtained)."""
    try:
        return fused.checked("1", *args, **kw)
    except fused.Stop as stop:
        raise fused.Stop(stop.where, stop.what, 2) from None


def porcelain(wt):
    """The lines `git status --porcelain --untracked-files=all` prints; its failure is exit 2."""
    return [line for line in answered("git", "status", "--porcelain", "--untracked-files=all", cwd=wt).splitlines()
            if line.strip()]


def tip_suite(wt, n):
    """The rebased tip's suite (RB4): `rebased-tip-suite.sh`, and under `local` the full command started detached;
    the caller waits on it."""
    mode = fused.checked("1", fused.script("rebased-tip-suite.sh"), cwd=wt).strip()
    if mode not in ("ci", "local"):
        raise fused.Stop("1", "rebased-tip-suite.sh printed " + (mode or "nothing"), 2)
    if mode == "local":
        full = fused.checked("1", fused.script("detect-test-command.sh"), "--tier", "all", cwd=wt).strip()
        fused.checked("1", DETACH, "start", RUN % n, "sh", "-c", full, cwd=wt)
    return mode


def commit(wt, n, regraded):
    """The GRADED files the regrade block modified, and only those, committed under the one subject (PRG1); none,
    no commit. A failing commit is no answer (exit 2)."""
    if regraded:
        answered("git", "commit", "-q", "-m", SUBJECT % n, "--", *regraded, cwd=wt)


def push(wt, pre):
    """The tree check immediately before the push (RB6, D10), any path at all refusing it (the regrade commit left its
    GRADED files clean), then the push under the lease pinned to the pre-rebase sha (RB5)."""
    if porcelain(wt):
        raise fused.Stop("1", "tree-check", 1)
    branch = answered("git", "branch", "--show-current", cwd=wt).strip()
    fused.checked("1", fused.script("push-branch.sh"), "--force-with-lease=%s:%s" % (branch, pre), cwd=wt)


def skip(wt, n):
    """The refactor-owed list (RB7): a candidate stops it with exit 1 for STRUCTURAL.md; none marks the skip."""
    owed = ".tdd/issue-%s-refactor-owed.md" % n
    code = fused.call(fused.script("refactor-owed.sh"), "list", owed, cwd=wt)[0]
    if code != 3:
        raise fused.Stop("1", "refactor-owed.sh list %s exit %d" % (owed, code), code)
    fused.checked("1", fused.script("event.sh"), "structural-pass", "stopped=nothing-structural", cwd=wt,
                  env=tunables.with_values(VERI_ISSUE=n, VERI_ACTOR="conductor"))


def ledger_text(wt, n):
    with open(os.path.join(wt, LEDGER % n), encoding="utf-8", errors="surrogateescape") as f:
        return f.read()


def questions(wt, n):
    """Sub-step 1's two questions (RB1): a dirty tree, or a step still only green, stops it with exit 1."""
    if porcelain(wt):
        raise fused.Stop("1", "tree-check", 1)
    code = fused.call(fused.script("next-pending-refactor.sh"), cwd=wt, stdin=ledger_text(wt, n))[0]
    if code != 3:
        raise fused.Stop("1", "next-pending-refactor.sh exit %d" % code, code)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
