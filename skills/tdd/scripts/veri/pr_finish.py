"""pr-finish.sh's computation, run in-process: DRAFT-PR.md sub-step 2's second block up to the refactor-owed render on
its clean path, after the first wait-ci.sh exited 0, made in one call (PRD 027.11): the PR url, the done mark and the
render. The run's record (the ⟦full-suite⟧ ticks, the metrics-cut mark, the metrics commit and their push) is closed by
`close`, which pr-ready-wait.sh calls before readying, so no records-only push follows the ready PR, while the done
mark still waits for CI's green verdict (#4332). The PR's title and body stay the conductor's."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys

import fused
import fused_step
import ledger
import plan_publish
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
CALLS = ("event.sh", "refactor-owed.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n)
    if given is None:
        return 2
    _, wt = given
    if stacked(NAME, wt, n):
        return 2
    url = pr_url(wt)
    mark(wt, n, "done", url)
    render(wt, n)
    return fused.settle(wt, n, NAME, ["pr_url=" + url, "refactor_owed_render=" + RENDER % n])


def close(wt, n, url):
    """The run's record, closed for PR <url> before it is readied: the ⟦full-suite⟧ ticks, the metrics-cut mark and
    the metrics, the tree check (MC5, D10) and the push (MC4); metrics.sh's exit code."""
    tick_full_suite(wt, n)
    metrics = record(wt, n, url)
    # A failed render may leave its file behind, half written or over the one an earlier call committed: that file is
    # carried as metrics=<code>, not committed, so it is no dirt; every other path still is.
    left = {METRICS % n} if metrics else set()
    if dirty(WHERE, wt, left):
        raise fused.Stop(WHERE, "tree-check", 1)
    fused.checked(WHERE, fused.script("push-branch.sh"), cwd=wt)
    return metrics


def record(wt, n, url):
    """MC2, MC3: the `metrics-cut` mark, which metrics.sh reads as the run's end in place of the `done` mark written
    only after CI's green verdict, then metrics.sh into .tdd/issue-<n>-metrics.md, committed as `metrics:` on exit 0;
    metrics.sh's exit code, which any other exit carries rather than stops on."""
    mark(wt, n, "metrics-cut", url)
    metrics = METRICS % n
    code = fused.call(fused.script("metrics.sh"), n, cwd=wt, out=metrics)[0]
    if code == 0:
        answered(WHERE, "git", "add", metrics, cwd=wt)
        answered(WHERE, "git", "commit", "-m", "metrics: what solving #%s cost (#%s)" % (n, n), cwd=wt)
    return code


def mark(wt, n, event, url):
    """`event.sh <event> pr=<url>` as the conductor of issue <n>; a failing exit stops it with that code."""
    fused.checked(WHERE, fused.script("event.sh"), event, "pr=" + url, cwd=wt,
                  env=tunables.with_values(VERI_ISSUE=n, VERI_ACTOR="conductor"))


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
        body = gh_answered(WHERE, "api", "repos/{owner}/{repo}/issues/%s" % n, "-q", ".body", wt=wt)
        criterion = fused.checked(WHERE, fused.script("ledger-steps.sh"), "criterion", k, cwd=wt, stdin=body).strip()
        fused.checked(WHERE, fused.script("tick-issue-criterion.sh"), n, criterion, cwd=wt, ok=(0, 3))
    answered(WHERE, "git", "add", LEDGER % n, cwd=wt)
    answered(WHERE, "git", "commit", "-m", "plan: the full suite is owed to CI (#%s)" % n, cwd=wt)


def stacked(name, wt, n):
    """True, named on stderr, when the worktree holds .tdd/issue-<n>-base: a stacked run's sub-step 2 runs neither of
    its blocks (DRAFT-PR.md *A stacked run*), so neither fused call of them may run there."""
    base = ".tdd/issue-%s-base" % n
    if not os.path.exists(os.path.join(wt, base)):
        return False
    sys.stderr.write("%s.sh: a stacked run (%s exists) runs neither block of sub-step 2\n" % (name, base))
    return True


def pr_url(wt):
    """The PR url read as sub-step 2 reads it (RC1); an empty answer stops it with exit 2."""
    branch = answered(WHERE, "git", "branch", "--show-current", cwd=wt).strip()
    url = gh_answered(WHERE, "api", "repos/{owner}/{repo}/pulls?head={owner}:%s" % branch, "-q",
                      ".[0].html_url // empty", wt=wt).strip()
    if not url:
        raise fused.Stop(WHERE, "no PR for " + branch, 2)
    return url


def answered(where, *args, **kw):
    """fused.checked, a nonzero exit stopping it with exit 2: a git call that fails gave no answer, never a clean
    negative (pr_prepare.answered's rule)."""
    try:
        return fused.checked(where, *args, **kw)
    except fused.Stop as stop:
        raise fused.Stop(stop.where, stop.what, 2) from None


def gh_answered(where, *args, wt):
    """plan_publish.gh, any failing exit (1, 4, a timeout's 124) stopping it with exit 2: GitHub gave no answer."""
    try:
        return plan_publish.gh(where, *args, wt=wt)
    except fused.Stop as stop:
        raise fused.Stop(stop.where, stop.what, 2) from None


def dirty(where, wt, left=()):
    """The paths `git status --porcelain --untracked-files=all` lists but <left>; a failing status is exit 2."""
    try:
        listed = fused.changed_paths(where, wt)
    except fused.Stop as stop:
        raise fused.Stop(stop.where, stop.what, 2) from None
    return set(listed) - set(left)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
