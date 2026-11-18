"""pr-finish.sh's computation, run in-process: DRAFT-PR.md sub-step 2's second block up to the refactor-owed render on
its clean path, after the first wait-ci.sh exited 0, made in one call (PRD 027.11): the PR url and the render. The run's
record (the ⟦full-suite⟧ ticks, the done mark, the metrics commit and their push) is closed by `close`, which
pr-ready-wait.sh calls before readying, so no records-only push follows the ready PR (#4332). The PR's title and body
stay the conductor's."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import fused
import fused_step
import ledger
import pr_ready_wait
import run_dir
import tunables

NAME = "pr-finish"
USAGE = "usage: pr-finish.sh <n>"
LEDGER = run_dir.ledger("", "%s")
WHERE = "2"
FULL_SUITE = "⟦full-suite⟧"
REFACTOR_OWED = ".tdd/issue-%s-refactor-owed.md"
RENDER = ".tdd/issue-%s-refactor-owed-render"
METRICS = ".tdd/issue-%s-metrics.md"

# The $S/ scripts this call makes, in the order each is first made (git and gh aside); unit/test_pr_finish.py fails
# when one is a script DRAFT-PR.md sub-step 2's second block does not name (FC19).
CALLS = ("refactor-owed.sh",)


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n)
    if given is None:
        return 2
    _, wt = given
    if pr_ready_wait.stacked(NAME, wt, n):
        return 2
    url = pr_ready_wait.pr_url(wt)
    render(wt, n)
    return fused.settle(wt, n, NAME, ["pr_url=" + url, "refactor_owed_render=" + RENDER % n])


def close(wt, n, url):
    """The run's record, closed for PR <url> before it is readied: the ⟦full-suite⟧ ticks, the done mark and the
    metrics, the tree check (MC5, D10) and the push (MC4); metrics.sh's exit code."""
    tick_full_suite(wt, n)
    metrics = record(wt, n, url)
    # A failed render may leave its file behind, half written or over the one an earlier call committed: that file is
    # carried as metrics=<code>, not committed, so it is no dirt; every other path still is.
    left = {METRICS % n} if metrics else set()
    if pr_ready_wait.dirty(WHERE, wt, left):
        raise fused.Stop(WHERE, "tree-check", 1)
    fused.checked(WHERE, fused.script("push-branch.sh"), cwd=wt)
    return metrics


def record(wt, n, url):
    """MC2, MC3: the `done` mark, then metrics.sh into .tdd/issue-<n>-metrics.md, committed as `metrics:` on exit 0;
    metrics.sh's exit code, which any other exit carries rather than stops on."""
    fused.checked(WHERE, fused.script("event.sh"), "done", "pr=" + url, cwd=wt,
                  env=tunables.with_values(VERI_ISSUE=n, VERI_ACTOR="conductor"))
    metrics = METRICS % n
    code = fused.call(fused.script("metrics.sh"), n, cwd=wt, out=metrics)[0]
    if code == 0:
        pr_ready_wait.answered(WHERE, "git", "add", metrics, cwd=wt)
        pr_ready_wait.answered(WHERE, "git", "commit", "-m", "metrics: what solving #%s cost (#%s)" % (n, n), cwd=wt)
    return code


def render(wt, n):
    """MC6: refactor-owed.sh render's output written to .tdd/issue-<n>-refactor-owed-render; exit 3 an empty file."""
    code, out, _ = fused.call(fused.script("refactor-owed.sh"), "render", REFACTOR_OWED % n, cwd=wt)
    if code not in (0, 3):
        raise fused.Stop(WHERE, fused.label("refactor-owed.sh", "render", REFACTOR_OWED % n) + " exit %d" % code, code)
    with open(os.path.join(wt, RENDER % n), "w") as f:
        f.write(out if code == 0 else "")


def tick_full_suite(wt, n):
    """MC1: under `ci`, with an unchecked ⟦full-suite⟧ line, each such line ticked with tick-ledger.sh until it exits
    3, each line's issue criterion ticked, and the ledger committed as `plan: the full suite is owed to CI`; nothing
    otherwise. It runs before readying, so no CI wait has spoken yet and none is read (#4332)."""
    if fused.checked(WHERE, fused.script("branch-suite.sh"), cwd=wt).strip() != "ci":
        return
    lines = [r.text for r in ledger.ledger_steps(ledger.read_ledger(run_dir.ledger(wt, n)))
             if r.state == "open" and FULL_SUITE in r.text]
    if not lines:
        return
    tick = (fused.script("tick-ledger.sh"), LEDGER % n, FULL_SUITE)
    while (code := fused.call(*tick, cwd=wt)[0]) != 3:
        if code != 0:
            raise fused.Stop(WHERE, fused.shown(*tick) + " exit %d" % code, code)
    for k in [k for line in lines for k in re.findall(r"⟦criterion (\d+)⟧", line)]:
        body = pr_ready_wait.gh_answered(WHERE, "api", "repos/{owner}/{repo}/issues/%s" % n, "-q", ".body", wt=wt)
        criterion = fused.checked(WHERE, fused.script("ledger-steps.sh"), "criterion", k, cwd=wt, stdin=body).strip()
        fused.checked(WHERE, fused.script("tick-issue-criterion.sh"), n, criterion, cwd=wt, ok=(0, 3))
    pr_ready_wait.answered(WHERE, "git", "add", LEDGER % n, cwd=wt)
    pr_ready_wait.answered(WHERE, "git", "commit", "-m", "plan: the full suite is owed to CI (#%s)" % n, cwd=wt)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
