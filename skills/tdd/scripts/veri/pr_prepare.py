"""pr-prepare.sh's computation, run in-process: the Draft PR step's sub-step 1 up to the structural pass's skip (the
two questions, the rebase, the regrade block, the rebased tip's suite when owed, the pinned-lease push, the
refactor-owed list), made in one call (PRD 027.9, amended: it stops after RB7)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import shlex
import sys

import fused
import fused_step
import run_dir
import tunables

NAME = "pr-prepare"
USAGE = "usage: pr-prepare.sh <n>"
LEDGER = run_dir.ledger("", "%s")
RUN = "rebased-full-%s"  # the rebased tip's detach-command.sh name: .tdd/rebased-full-<n>.out and .exit
DETACH = fused.script("detach-command.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    questions(wt, n)
    code, said, _ = fused.call(fused.script("rebase-onto-default.sh"), cwd=wt)
    if code not in (0, 3):
        raise fused.Stop("1", "rebase-onto-default.sh exit %d" % code, code)
    regrade(wt)
    values = {"rebased": "0", "rebased_from": "", "rebased_tip_suite": "none"}
    if code == 0:
        values.update(rebased="1", rebased_from=(said.splitlines() or [""])[0].strip())
        values["rebased_tip_suite"] = tip_suite(wt, n)
        push(wt, values["rebased_from"])
    skip(wt, n)
    return fused.settle(wt, n, NAME, ["%s=%s" % (key, values[key]) for key in
                                      ("rebased", "rebased_from", "rebased_tip_suite")])


def default_branch(wt):
    """The default branch the regrade block names as `origin/<default>`, read without the network."""
    import git
    return git.default_branch(cwd=wt, remote=False)


def regrade(wt):
    """Sub-step 1's regrade block (RB3): every unit the branch signed since its merge base with origin/<default>, then
    `grade-prose.sh --convert`; the block's highest exit 1 or 2 stops it once the block has run."""
    default = default_branch(wt)
    if not default:
        raise fused.Stop("1", "no default branch for the regrade block", 2)
    base = fused.checked("1", "git", "merge-base", "HEAD", "origin/" + default, cwd=wt).strip()
    diff = fused.checked("1", "git", "diff", base, "HEAD", "-U0", "--", ":(glob)**/GRADED", cwd=wt)
    units = [m.group(1) for m in (re.match(r"^\+([^+][^ ]*) ", line) for line in diff.splitlines()) if m]
    highest = 0
    for args in [(os.path.join(os.path.dirname(unit) or ".", "REQUIREMENTS.md"), unit) for unit in units] + [
            ("--convert",)]:
        highest = max(highest, fused.call(fused.script("grade-prose.sh"), *args, cwd=wt, stdin="")[0])
    if highest:
        raise fused.Stop("1", "regrade block exit %d" % highest, highest)


def tip_suite(wt, n):
    """The rebased tip's suite (RB4): `rebased-tip-suite.sh`, and under `local` the full command detached and waited
    on; a red wait stops it with the wait's code."""
    mode = fused.checked("1", fused.script("rebased-tip-suite.sh"), cwd=wt).strip()
    if mode not in ("ci", "local"):
        raise fused.Stop("1", "rebased-tip-suite.sh printed " + (mode or "nothing"), 2)
    if mode == "local":
        full = fused.checked("1", fused.script("detect-test-command.sh"), "--tier", "all", cwd=wt).strip()
        fused.checked("1", DETACH, "start", RUN % n, *shlex.split(full), cwd=wt)
        code = fused.call(DETACH, "wait", RUN % n, cwd=wt)[0]
        if code != 0:
            raise fused.Stop("1", "detach-command.sh wait %s exit %d" % (RUN % n, code), code)
    return mode


def push(wt, pre):
    """The tree check immediately before the push (RB6, D10), then the push under the lease pinned to the pre-rebase
    sha (RB5)."""
    if [path for path in fused.changed_paths("1", wt) if os.path.basename(path) != "GRADED"]:
        raise fused.Stop("1", "tree-check", 1)
    branch = fused.checked("1", "git", "branch", "--show-current", cwd=wt).strip()
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
    if fused.changed_paths("1", wt):
        raise fused.Stop("1", "tree-check", 1)
    code = fused.call(fused.script("next-pending-refactor.sh"), cwd=wt, stdin=ledger_text(wt, n))[0]
    if code != 3:
        raise fused.Stop("1", "next-pending-refactor.sh exit %d" % code, code)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
