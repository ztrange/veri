"""pr-finish.sh's computation, run in-process: DRAFT-PR.md sub-step 2's second block up to the refactor-owed render on
its clean path, after the first wait-ci.sh exited 0, made in one call (PRD 027.11). The PR's title and body stay the
conductor's."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import sys

import fused
import fused_step
import ledger
import plan_publish
import pr_ready_wait
import run_dir

NAME = "pr-finish"
LEDGER = run_dir.ledger("", "%s")
WHERE = "2"
FULL_SUITE = "⟦full-suite⟧"


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    tick_full_suite(wt, n)
    return 0


def tick_full_suite(wt, n):
    """MC1: under `ci`, with an unchecked ⟦full-suite⟧ line and a first wait that did not say `has no checks`, each
    such line ticked with tick-ledger.sh until it exits 3, each line's issue criterion ticked, and the ledger
    committed as `plan: the full suite is green on CI`; nothing otherwise."""
    if fused.checked(WHERE, fused.script("branch-suite.sh"), cwd=wt).strip() != "ci":
        return
    lines = [r.text for r in ledger.ledger_steps(ledger.read_ledger(run_dir.ledger(wt, n)))
             if r.state == "open" and FULL_SUITE in r.text]
    if not lines or pr_ready_wait.NO_CHECKS in pr_ready_wait.said(wt, ".tdd/wait-ci.err"):
        return
    tick = (fused.script("tick-ledger.sh"), LEDGER % n, FULL_SUITE)
    while (code := fused.call(*tick, cwd=wt)[0]) != 3:
        if code != 0:
            raise fused.Stop(WHERE, fused.shown(*tick) + " exit %d" % code, code)
    for k in [k for line in lines for k in re.findall(r"⟦criterion (\d+)⟧", line)]:
        body = plan_publish.gh(WHERE, "api", "repos/{owner}/{repo}/issues/%s" % n, "-q", ".body", wt=wt)
        criterion = fused.checked(WHERE, fused.script("ledger-steps.sh"), "criterion", k, cwd=wt, stdin=body).strip()
        fused.checked(WHERE, fused.script("tick-issue-criterion.sh"), n, criterion, cwd=wt, ok=(0, 3))
    fused.checked(WHERE, "git", "add", LEDGER % n, cwd=wt)
    fused.checked(WHERE, "git", "commit", "-m", "plan: the full suite is green on CI (#%s)" % n, cwd=wt)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
