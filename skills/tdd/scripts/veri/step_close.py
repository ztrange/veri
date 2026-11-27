"""step-close.sh's computation, run in-process: a step's close-out after a passing or skipped verify-refactor
(SKILL.md *Refactor loop*, sub-step 6's PASS branch), made in one call after a clean refactor-half.sh (PRD 027.8)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys
import time

import fused
import fused_step
import github_queue
import plan_publish
import run_dir
import tunables
from ledger import PENDING_MARK
from next_pending_refactor import refactor_pending

NAME = "step-close"
USAGE = "usage: step-close.sh <n>"
LEDGER = run_dir.ledger("", "%s")
REFACTOR_HALF = ".tdd/issue-%s-refactor-half"

# The $S/ scripts this call makes, in the order each is first made (git and gh aside); unit/test_step_close.py fails
# when one is a script SKILL.md's Refactor loop section does not name (FC19).
CALLS = ("graded-changed.sh", "tests-frozen.sh", "clear-refactor-pending.sh", "push-branch.sh",
         "event.sh", "stop-requested.sh", "comment.sh", "criterion-finished.sh", "ledger-steps.sh",
         "tick-issue-criterion.sh", "next-unchecked.sh", "run-affordable.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    step = fused_step.first_step(wt, n, refactor_pending)
    if step is None:
        sys.stderr.write("step-close.sh: no refactor-pending step\n")
        return 2
    settled_after = settled_verdict(wt, n)
    verdict_log, uncovered = fused_step.verdict(wt)
    if fused_step.record(NAME, wt, n, step, (("verdict_log", verdict_log),)) is None:
        return 1
    if settled_after != verdict_log:
        # The log is the flags' committed source: a record settled after another verdict (or none) gains them, so a
        # revised PASS's uncovered behaviour is never skipped (#4029); a log the record was settled after adds nothing.
        fused_step.gain(NAME, wt, n, "refactor-half", "uncovered_spec", uncovered, step)
    for uncovered in read_half(wt, n).get("uncovered_spec", []):
        raise fused.Stop("6", "uncovered_spec=" + uncovered, 1)
    # The step's green commit is the last that changed its refactor-pending line's count: a later plan commit that
    # only inserted a step after it leaves that count alone (#4510). The checkbox's "] " anchors the text, so a
    # step whose text ends in this one's is not matched.
    line = "] " + step + PENDING_MARK
    green_sha = fused.checked("6", "git", "log", "-1", "--format=%H", "-S", line, "--", LEDGER % n, cwd=wt).strip()
    if not green_sha:
        raise fused.Stop("6", "no green commit for %s in %s" % (step, LEDGER % n), 2)
    fused_step.refresh(NAME, wt, n, "refactor-half", {"green_sha": green_sha})
    checks(wt, n, green_sha)
    try:
        commit(wt, n, step)
        mirror(wt, n, step)
        return fused.settle(wt, n, NAME, ["next=" + next_stop(wt, n)])
    except (fused.Stop, fused.Waiting):
        raise
    except Exception as error:
        # Past the checks the push may have landed: an unforeseen error names 6, so the conductor goes on from 6
        # rather than redoing the branch from its start, which would end the stage and post step-done twice.
        raise fused.Stop("6", "%s %s" % (type(error).__name__, error), 2) from error


def ledger_text(wt, n):
    with open(os.path.join(wt, LEDGER % n), encoding="utf-8", errors="surrogateescape") as f:
        return f.read()


def mirror(wt, n, step):
    """6's mirror (CO7): the step-done comment, each `⟦criterion k⟧` of the step asked whether it is finished (0 ticks
    criterion k's first line in the issue body, 3 ticks nothing), then the step-done mark. While GitHub is down
    (#4803) a finished criterion is queued as a `tick` for `github-queue.sh replay` instead, reading no issue body:
    GitHub is asked once per step, up front at the first finished criterion (`.tdd/github-outage` in the main working
    tree, else github-status.sh's read), and an incident begun after that is caught by a body read or tick that got no
    answer while github-status reports one, which queues that criterion and every later one."""
    fused.checked("6", fused.script("comment.sh"), n, "step-done", cwd=wt)
    top = github_queue.root(wt)
    down = None
    for k in re.findall(r"⟦criterion (\d+)⟧", step):
        if asked(fused.script("criterion-finished.sh"), k, cwd=wt, stdin=ledger_text(wt, n),
                 err=".tdd/criterion-finished.err") == 0:
            if down is None:
                down = top is not None and github_queue.down(top)
            if down:
                github_queue.queue_tick(top, n, k)
                continue
            try:
                tick(wt, n, k)
            except fused.Stop as stop:
                if stop.code != 2 or top is None or not github_queue.incident():
                    raise
                down = True
                github_queue.queue_tick(top, n, k)
    done = fused.checked("6", fused.script("ledger-steps.sh"), "last-done", cwd=wt, stdin=ledger_text(wt, n)).strip()
    fused.mark("6", wt, n, done, "step-done")


def tick(wt, n, k):
    """Criterion k's first line in the issue body, ticked with tick-issue-criterion.sh, whose 3 goes on like its 0."""
    body = plan_publish.gh("6", "api", "repos/{owner}/{repo}/issues/%s" % n, "-q", ".body", wt=wt)
    line = fused.checked("6", fused.script("ledger-steps.sh"), "criterion", k, cwd=wt, stdin=body).strip()
    fused.checked("6", fused.script("tick-issue-criterion.sh"), n, line, ok=(0, 3), cwd=wt)


def next_stop(wt, n):
    """Where the run goes next (CO8): `draft-pr` when next-unchecked.sh exits 3, else `cycle` when run-affordable.sh,
    given the count of open steps a cycle closes, exits 0 or 3; any other answer stops it."""
    if asked(fused.script("next-unchecked.sh"), cwd=wt, stdin=ledger_text(wt, n)) == 3:
        return "draft-pr"
    rows = fused.checked("6", fused.script("ledger-steps.sh"), cwd=wt, stdin=ledger_text(wt, n)).splitlines()
    open_steps = sum(1 for row in rows if row.split("\t")[1:3] == ["open", "step"])
    asked(fused.script("run-affordable.sh"), str(open_steps), cwd=wt)
    return "cycle"


def asked(name, *args, **kw):
    """A question whose exit 0 or 3 is the answer: that code; any other stops it at 6."""
    code, _, _ = fused.call(name, *args, **kw)
    if code not in (0, 3):
        raise fused.Stop("6", fused.shown(name, *args, **kw) + " exit %d" % code, code)
    return code


def checks(wt, n, green_sha):
    """6's checks before the clear (CO2, CO3): graded units, the refactored re-record."""
    fused.checked("6", fused.script("graded-changed.sh"), green_sha, cwd=wt)
    fused.checked("6", fused.script("tests-frozen.sh"), "rerecord-refactored", LEDGER % n, green_sha, cwd=wt)


def commit(wt, n, step):
    """The tree check (CO4, D10), then the clear, the `chore: refactor verified` commit and its push (CO5), the
    stage's end, and the stop ask after that push (CO6)."""
    allowed = {LEDGER % n, ".tdd/issue-%s-added.md" % n, ".tdd/issue-%s-refactor-owed.md" % n}
    if set(fused.changed_paths("6", wt)) - allowed:
        raise fused.Stop("6", "tree-check", 1)
    fused.checked("6", fused.script("clear-refactor-pending.sh"), LEDGER % n, step, cwd=wt)
    fused.checked("6", "git", "add", "-A", cwd=wt)
    subject = "chore: refactor verified for %s (#%s)" % (fused_step.summary(step), n)
    fused.checked("6", "git", "commit", "-m", subject, cwd=wt)
    fused.checked("6", fused.script("push-branch.sh"), cwd=wt)
    stage_end(wt, n)
    code, said, _ = fused.call(fused.script("stop-requested.sh"), cwd=wt)
    if code != 3:
        raise fused.Stop("6", "stop-requested.sh exit %d%s" % (code, " " + said.strip() if said.strip() else ""), code)


def stage_end(wt, n):
    """The refactor-loop stage ends with status 0 once the push exits 0, before its stop check."""
    try:
        with open(os.path.join(wt, ".tdd", "stage-rl.t")) as f:
            started = int(f.read().strip())
    except (OSError, ValueError) as error:
        raise fused.Stop("6", "no .tdd/stage-rl.t", 2) from error
    fused.checked("6", fused.script("event.sh"), "stage-end", "stage=refactor-loop", "status=0",
                  "secs=%d" % (int(time.time()) - started), cwd=wt, env=tunables.with_values(VERI_ISSUE=n))


def settled_verdict(wt, n):
    """The `verdict_log=` the refactor-half record was settled after, before any refresh; None without one."""
    try:
        return fused.read_settled(os.path.join(wt, REFACTOR_HALF % n)).get("verdict_log")
    except OSError:
        return None


def read_half(wt, n):
    """{key: [its values, in order]} of .tdd/issue-<n>-refactor-half, which may hold a key more than once."""
    values = {}
    with open(os.path.join(wt, REFACTOR_HALF % n), encoding="utf-8", errors="surrogateescape") as f:
        for line in f.read().splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values.setdefault(key, []).append(value)
    return values


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
