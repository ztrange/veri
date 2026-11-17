"""pr-ready-wait.sh's computation, run in-process: DRAFT-PR.md sub-step 2's first block on its clean path, the PR
url read, readying the PR and its first CI wait, made in one call (PRD 027.10)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import plan_publish

NAME = "pr-ready-wait"
WHERE = "2"
NO_CHECKS = "has no checks"
WAIT = "wait-ci.sh"  # the `waiting on` name of the CI wait


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n)
    if given is None:
        return 2
    _, wt = given
    resumed = fused.load_wait(wt, n, NAME)
    if resumed is not None:
        values = resumed[1]
    else:
        values = ready(wt)
        fused.save_wait(wt, n, NAME, WAIT, values)
    head = fused.checked(WHERE, "git", "rev-parse", "HEAD", cwd=wt).strip()
    code = fused.call(fused.script("wait-ci.sh"), values["pr_url"], "540", "", head, cwd=wt,
                      out=".tdd/wait-ci.out", err=".tdd/wait-ci.err")[0]
    if code == 3:
        raise fused.Waiting(WAIT)
    os.remove(fused.wait_record(wt, n, NAME))
    if code != 0:
        raise fused.Stop(WHERE, fused.shown(fused.script("wait-ci.sh"), values["pr_url"], "540", "", head,
                                            out=".tdd/wait-ci.out", err=".tdd/wait-ci.err") + " exit %d" % code, code)
    if said(wt, ".tdd/ci-flake.out").strip():
        raise fused.Stop(WHERE, "wait-ci.sh exit 0 with .tdd/ci-flake.out non-empty", 1)
    lines = ["pr_url=" + values["pr_url"], "pr_number=" + values["pr_number"], "ci=green"]
    return fused.settle(wt, n, NAME, lines + (["no_checks=1"] if NO_CHECKS in said(wt, ".tdd/wait-ci.err") else []))


def ready(wt):
    """The PR url read as sub-step 2 reads it (RC1), the tree check (RC4, D10), then pr-ready.sh on the head (RC2):
    {"pr_url", "pr_number"}."""
    branch = fused.checked(WHERE, "git", "branch", "--show-current", cwd=wt).strip()
    url = plan_publish.gh(WHERE, "api", "repos/{owner}/{repo}/pulls?head={owner}:%s" % branch, "-q",
                          ".[0].html_url // empty", wt=wt).strip()
    if not url:
        raise fused.Stop(WHERE, "no PR for " + branch, 2)
    if fused.changed_paths(WHERE, wt):
        raise fused.Stop(WHERE, "tree-check", 1)
    number = url.rstrip("/").rsplit("/", 1)[-1]
    head = fused.checked(WHERE, "git", "rev-parse", "HEAD", cwd=wt).strip()
    fused.checked(WHERE, fused.script("pr-ready.sh"), number, head, cwd=wt, err=".tdd/pr-ready.err")
    return {"pr_url": url, "pr_number": number}


def said(wt, path):
    """The text of <path> under the worktree; "" when it cannot be read."""
    try:
        with open(os.path.join(wt, path), encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
