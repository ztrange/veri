"""pr-ready-wait.sh's computation, run in-process: DRAFT-PR.md sub-step 2's first block on its clean path, the PR
url read, the run's record closed and pushed (pr_finish.close, #4332), readying the PR and its first CI wait, made in
one call (PRD 027.10)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import plan_publish
import pr_finish

NAME = "pr-ready-wait"
USAGE = "usage: pr-ready-wait.sh <n>"
WHERE = "2"
NO_CHECKS = "has no checks"
WAIT = "wait-ci.sh"  # the `waiting on` name of the CI wait

# The $S/ scripts this call makes, in the order each is first made (git and gh aside); unit/test_pr_ready_wait.py fails
# when one is a script DRAFT-PR.md sub-step 2's first block does not name (FC19).
CALLS = ("branch-suite.sh", "tick-ledger.sh", "ledger-steps.sh", "tick-issue-criterion.sh", "event.sh", "metrics.sh",
         "push-branch.sh", "pr-ready.sh", "wait-ci.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, pr_finish.LEDGER)
    if given is None:
        return 2
    _, wt = given
    if stacked(NAME, wt, n):
        return 2
    resumed = fused.load_wait(wt, n, NAME)
    if resumed is not None:
        values = resumed[1]
    else:
        values = ready(wt, n)
        fused.save_wait(wt, n, NAME, WAIT, values)
    ci_wait(wt, n, NAME, values["pr_url"])
    lines = ["pr_url=" + values["pr_url"], "pr_number=" + values["pr_number"], "ci=green"]
    lines += ["metrics=%d" % values["metrics"]] if values["metrics"] else []
    return fused.settle(wt, n, NAME, lines + (["no_checks=1"] if NO_CHECKS in said(wt, ".tdd/wait-ci.err") else []))


def stacked(name, wt, n):
    """True, named on stderr, when the worktree holds .tdd/issue-<n>-base: a stacked run's sub-step 2 runs neither of
    its blocks (DRAFT-PR.md *A stacked run*), so neither fused call of them may run there."""
    base = ".tdd/issue-%s-base" % n
    if not os.path.exists(os.path.join(wt, base)):
        return False
    sys.stderr.write("%s.sh: a stacked run (%s exists) runs neither block of sub-step 2\n" % (name, base))
    return True


def ci_wait(wt, n, owner, url):
    """`wait-ci.sh <pr-url> 540 "" <head>` into .tdd/wait-ci.out and .tdd/wait-ci.err (RC3, MC4): exit 3 raises
    Waiting, <owner>'s wait record kept; else the record is removed, 1 and 2 stop it, and an exit 0 with a non-empty
    .tdd/ci-flake.out stops it with exit 1, so the block writes the `ci-flake` event."""
    head = answered(WHERE, "git", "rev-parse", "HEAD", cwd=wt).strip()
    waited = (fused.script("wait-ci.sh"), url, "540", "", head)
    files = {"out": ".tdd/wait-ci.out", "err": ".tdd/wait-ci.err"}
    code = fused.call(*waited, cwd=wt, **files)[0]
    if code == 3:
        raise fused.Waiting(WAIT)
    os.remove(fused.wait_record(wt, n, owner))
    if code != 0:
        raise fused.Stop(WHERE, fused.shown(*waited, **files) + " exit %d" % code, code)
    if said(wt, ".tdd/ci-flake.out").strip():
        raise fused.Stop(WHERE, "wait-ci.sh exit 0 with .tdd/ci-flake.out non-empty", 1)


def pr_url(wt):
    """The PR url read as sub-step 2 reads it (RC1); an empty answer stops it with exit 2."""
    branch = answered(WHERE, "git", "branch", "--show-current", cwd=wt).strip()
    url = gh_answered(WHERE, "api", "repos/{owner}/{repo}/pulls?head={owner}:%s" % branch, "-q",
                      ".[0].html_url // empty", wt=wt).strip()
    if not url:
        raise fused.Stop(WHERE, "no PR for " + branch, 2)
    return url


def ready(wt, n):
    """The PR url (RC1), the run's record closed and pushed with its tree check (pr_finish.close; RC4, D10), then
    pr-ready.sh on the head (RC2): {"pr_url", "pr_number", "metrics"}."""
    url = pr_url(wt)
    metrics = pr_finish.close(wt, n, url)
    number = url.rstrip("/").rsplit("/", 1)[-1]
    head = answered(WHERE, "git", "rev-parse", "HEAD", cwd=wt).strip()
    fused.checked(WHERE, fused.script("pr-ready.sh"), number, head, cwd=wt, err=".tdd/pr-ready.err")
    return {"pr_url": url, "pr_number": number, "metrics": metrics}


def answered(where, *args, **kw):
    """fused.checked, a nonzero exit stopping it with exit 2: a git call that fails gave no answer, never a clean
    negative (pr_prepare.answered's rule)."""
    try:
        return fused.checked(where, *args, **kw)
    except fused.Stop as stop:
        raise fused.Stop(stop.where, stop.what, 2)


def gh_answered(where, *args, wt):
    """plan_publish.gh, any failing exit (1, 4, a timeout's 124) stopping it with exit 2: GitHub gave no answer."""
    try:
        return plan_publish.gh(where, *args, wt=wt)
    except fused.Stop as stop:
        raise fused.Stop(stop.where, stop.what, 2)


def dirty(where, wt, left=()):
    """The paths `git status --porcelain --untracked-files=all` lists but <left>; a failing status is exit 2."""
    try:
        listed = fused.changed_paths(where, wt)
    except fused.Stop as stop:
        raise fused.Stop(stop.where, stop.what, 2)
    return set(listed) - set(left)


def said(wt, path, absent=""):
    """The text of <path> under the worktree; <absent> when it cannot be read."""
    try:
        with open(os.path.join(wt, path), encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return absent


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
