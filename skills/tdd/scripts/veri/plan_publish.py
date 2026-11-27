"""plan-publish.sh's computation, run in-process: SKILL.md step 2's fixed tail once the plan is written (sub-steps 2-4,
step 2b, and step 2c up to its PASS branch), made in one call (PRD 027.3)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import json
import math
import os
import sys
import time

import fused
import fused_step
import github
import run_dir
import run_start
import tunables

USAGE = "usage: plan-publish.sh <n> <title-file>"

# The $S/ scripts this call makes, in the order each is first made (git and gh aside); unit/test_plan_publish.py fails
# when one is a script SKILL.md steps 2, 2b and 2c do not name, save two it exempts by name (FC19).
CALLS = ("scope-check.sh", "ledger-steps.sh", "push-branch.sh", "stack-branch.sh", "event.sh", "comment.sh",
         "refresh-spec.sh", "stop-requested.sh", "detach-leaf.sh", "supervise.sh", "run-verdict.sh", "wait-leaf.sh")


def inputs(n, title_file):
    """(settled preflight values, title) once every input file is readable; else None, each missing one named on
    stderr."""
    missing = []
    try:
        settled = fused.read_settled(run_start.preflight_file(n))
    except OSError:
        settled = None
        missing.append(".tdd/issue-%s-preflight" % n)
    if settled is not None and not os.path.exists(run_dir.ledger(settled.get("worktree", ""), n)):
        missing.append(os.path.relpath(run_dir.ledger(".", n)))
    try:
        with open(title_file) as f:
            title = f.read().strip()
    except OSError:
        title = None
        missing.append(title_file)
    for name in missing:
        sys.stderr.write("plan-publish.sh: no %s\n" % name)
    return None if missing else (settled, title)


def main(argv):
    if len(argv) != 2 or not argv[0].isdigit():
        sys.stderr.write(USAGE + "\n")
        return 2
    n, title_file = argv
    given = inputs(n, title_file)
    if given is None:
        return 2
    settled, title = given
    try:
        return run(n, settled, title)
    except fused.Stop as stop:
        return fused.stopped(stop)


def gh_call(*args, wt):
    """One gh call, printed, bounded by VERI_GH_TIMEOUT and redacted as every gh call of veri's is: (code, stdout, the
    call's label)."""
    code, out, _ = fused.call("gh", *args, cwd=wt, run=github.bounded)
    return code, out, fused.label("gh", *args)


def gh(where, *args, wt):
    """gh_call, raising a Stop at <where> on any exit but 0; its stdout otherwise."""
    code, out, shown = gh_call(*args, wt=wt)
    if code != 0:
        raise fused.Stop(where, shown + " exit %d" % code, code)
    return out


def event(wt, n, *fields):
    fused.checked(fused_where(fields), fused.script("event.sh"), *fields, cwd=wt,
                  env=tunables.with_values(VERI_ISSUE=n))


def fused_where(fields):
    return "2.2" if "stage=plan" in fields else "2.3"


def run(n, settled, title):
    wt = settled["worktree"]
    waited = load_wait(wt, n)
    if waited is not None:
        return verdict(n, wt, waited)
    ledger = os.path.relpath(run_dir.ledger(".", n))
    plan_sha, k = commit_plan(n, wt, ledger)
    fused.checked("2.3", fused.script("push-branch.sh"), cwd=wt)
    branch = fused.checked("2.3", "git", "branch", "--show-current", cwd=wt).strip()
    pr_url = draft_pr(n, wt, settled, title, k, branch)
    fused.checked("2.4", fused.script("comment.sh"), n, "plan", cwd=wt)
    gh("2b", "api", "repos/{owner}/{repo}/issues/%s/comments" % n,
       "-f", "body=" + github.published(start_comment(n, k, branch)), wt=wt)
    refresh_spec(n, wt)
    lines = ["plan_sha=" + plan_sha, "steps=%d" % k, "pr_url=" + pr_url,
             "pr_number=" + pr_url.rstrip("/").rsplit("/", 1)[-1]]
    launch_verdict_plan(n, wt, settled)
    save_wait(wt, n, lines)
    return verdict(n, wt, lines)


def wait_record(wt, n):
    return run_dir.issue_file(wt, n, "-plan-publish-wait")


def save_wait(wt, n, lines):
    """Record the launched leaf's wait: the conductor it runs under (FC7) and the lines settled so far, so a second
    call only waits again (FC6)."""
    with open(wait_record(wt, n), "w") as f:
        json.dump({"conductor": fused.conductor(wt), "lines": lines}, f)


def load_wait(wt, n):
    """The settled lines a first call recorded before its wait ran out; None when there is no usable record. A record
    another conductor wrote is removed: its leaf is a dead run's (FC7)."""
    try:
        with open(wait_record(wt, n)) as f:
            record = json.load(f)
        lines, theirs = record["lines"], record.get("conductor")
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None
    if theirs != fused.conductor(wt):
        os.remove(wait_record(wt, n))
        return None
    return lines


SPEC = ".tdd/issue-%s-spec.md"
LEAF = "verdict-plan"


def refresh_spec(n, wt):
    """Step 2c's refresh before the launch: 0, 2 and 3 go on; 1, a changed criteria count, stops it (PT6)."""
    fused.checked("2c", fused.script("refresh-spec.sh"), n, SPEC % n, cwd=wt, ok=(0, 2, 3))


def launch_verdict_plan(n, wt, settled):
    """The verdict-plan leaf under *Launching a leaf* (FC8): the stop check, the completion files cleared, then the
    detached supervise.sh with step 2c's arguments, no --step, VERI_TEST_CMD the fast tier (PT7, FC9)."""
    code, out, _ = fused.call(fused.script("stop-requested.sh"), cwd=wt)
    mode = out.strip()
    if code not in (0, 3) or (code == 0 and mode != "at-ledger"):
        raise fused.Stop("2c", "stop-requested.sh exit %d%s" % (code, " " + mode if mode else ""), code)
    for name in (LEAF + ".exit", LEAF + ".pid"):
        with contextlib.suppress(FileNotFoundError):
            os.remove(run_dir.run_file(wt, name))
    fused.checked("2c", fused.script("detach-leaf.sh"), fused.script("supervise.sh"), LEAF,
                  fused.script("run-verdict.sh"), "--branch-base", fused_step.branch_base("2c", wt, n), "plan",
                  SPEC % n, os.path.relpath(run_dir.ledger(".", n)), cwd=wt,
                  env=tunables.with_values(VERI_TEST_CMD=settled["fast_cmd"], VERI_ISSUE=n),
                  out=".tdd/verify-plan.reason", err=".tdd/verify-plan.err")


def verdict(n, wt, lines):
    """Wait for verdict-plan: 0 posts the verify-plan comment and settles <lines> with verify_plan=PASS; 1 or 2
    stops it before that comment."""
    code = fused.call(fused.script("wait-leaf.sh"), LEAF, cwd=wt)[0]
    if code == 3:
        sys.stdout.write("waiting on %s\n" % LEAF)
        return 3
    with contextlib.suppress(FileNotFoundError):
        os.remove(wait_record(wt, n))
    if code != 0:
        raise fused.Stop("2c", "wait-leaf.sh %s exit %d" % (LEAF, code), code)
    fused.checked("2c", fused.script("comment.sh"), n, "verify-plan", cwd=wt)
    return fused.settle(wt, n, "plan-publish", lines + ["verify_plan=PASS"])


def commit_plan(n, wt, ledger):
    """Step 2.2: the scope check, then the ledger committed alone from a tree listing nothing else (PT1, PT2, PT8);
    (plan sha, step count)."""
    fused.checked("2.2", fused.script("scope-check.sh"), ledger, ".", cwd=wt)
    with open(os.path.join(wt, ledger)) as f:
        steps = fused.checked("2.2", fused.script("ledger-steps.sh"), cwd=wt, stdin=f.read())
    k = len([line for line in steps.splitlines() if line.strip()])
    listed = fused.checked("2.2", "git", "status", "--porcelain", "--untracked-files=all", cwd=wt).splitlines()
    if [line for line in listed if line[3:] != ledger]:
        raise fused.Stop("2.2", "tree-check", 1)
    fused.checked("2.2", "git", "add", ledger, cwd=wt)
    fused.checked("2.2", "git", "commit", "-m", "plan: scope #%s into %d steps (#%s)" % (n, k, n), cwd=wt)
    plan_sha = fused.checked("2.2", "git", "rev-parse", "HEAD", cwd=wt).strip()
    began = os.path.join(wt, ".tdd", "stage-plan.t")
    if os.path.exists(began):
        with open(began) as f:
            secs = int(time.time()) - int(f.read().strip() or 0)
        event(wt, n, "stage-end", "stage=plan", "status=0", "secs=%d" % secs)
    return plan_sha, k


def draft_pr(n, wt, settled, title, k, branch):
    """Step 2.3's draft PR, opened only when <branch> has none (PT4); its url."""
    found = gh("2.3", "api", "repos/{owner}/{repo}/pulls?head={owner}:%s" % branch, "-q", ".[0].html_url // empty",
               wt=wt).strip()
    if found:
        return found
    code, out, _ = fused.call(fused.script("stack-branch.sh"), cwd=wt)
    if code not in (0, 3):
        raise fused.Stop("2.3", "stack-branch.sh exit %d" % code, code)
    base = out.strip() if code == 0 else settled["default_branch"]
    event(wt, n, "stage-start", "stage=draft-pr")
    began = time.monotonic()
    body = ("<!-- veri:run-body -->\nCloses #%s — work in progress: %d steps planned. The ledger %s is "
            "the source of truth.\n<!-- /veri:run-body -->" % (n, k, os.path.relpath(run_dir.ledger(".", n))))
    args = ("api", "repos/{owner}/{repo}/pulls", "-F", "draft=true", "-f", "base=" + base, "-f", "head=" + branch,
            "-f", "title=" + title, "-f", "body=" + body, "-q", ".html_url")
    code, out, shown = gh_call(*args, wt=wt)
    event(wt, n, "stage-end", "stage=draft-pr", "status=%d" % code, "secs=%d" % math.ceil(time.monotonic() - began))
    if code != 0:
        raise fused.Stop("2.3", shown + " exit %d" % code, code)
    return out.strip()


def start_comment(n, k, branch):
    """Step 2b's comment: the branch, the worktree (as `.tdd/wt/<n>`, never a local absolute path), the step count, and
    that each phase will be blind-verified."""
    return ("veri started on branch `%s`, worktree `.tdd/wt/%s`: %d steps planned. Each phase will be "
            "blind-verified." % (branch, n, k))


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
