"""run-done.sh's computation, run in-process: DRAFT-PR.md sub-step 4 on its clean path, the stop ask, the final done
comment and the clearing of a reported stop request, made in one call (PRD 027.12). It never merges (sub-step 3)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step
import pr_finish
import pr_ready_wait

NAME = "run-done"
USAGE = "usage: run-done.sh <n>"
WHERE = "4"

# The $S/ scripts this call makes, in the order each is first made (git aside); unit/test_run_done.py fails when one is
# a script DRAFT-PR.md sub-step 4 does not name (FC19).
CALLS = ("stop-requested.sh", "comment.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    """DC1, DC2: stop-requested.sh (every exit goes on), the tree check, comment.sh <n> done, then
    stop-requested.sh --clear when the first call exited 0 or 2."""
    given = fused_step.inputs(NAME + ".sh", n)
    if given is None:
        return 2
    _, wt = given
    asked = fused.call(fused.script("stop-requested.sh"), cwd=wt)[0]
    if pr_ready_wait.dirty(WHERE, wt, render_left(wt, n)):
        raise fused.Stop(WHERE, "tree-check", 1)
    fused.checked(WHERE, fused.script("comment.sh"), n, "done", cwd=wt)
    cleared = asked in (0, 2)
    if cleared:
        fused.checked(WHERE, fused.script("stop-requested.sh"), "--clear", cwd=wt)
    return fused.settle(wt, n, NAME, ["stop_requested=%d" % asked, "cleared=%d" % cleared])


def render_left(wt, n):
    """{the metrics file} when .tdd/issue-<n>-pr-ready-wait holds a non-zero `metrics=`: a failed render may leave that
    file behind, carried rather than committed, so it is no dirt here either; else nothing."""
    try:
        failed = fused.read_settled(fused.settled_file(wt, n, pr_ready_wait.NAME)).get("metrics", "0") != "0"
    except OSError:
        failed = False
    return {pr_finish.METRICS % n} if failed else set()


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
