"""run-done.sh's computation, run in-process: DRAFT-PR.md sub-step 4 on its clean path, the stop ask, the final done
comment and the clearing of a reported stop request, made in one call (PRD 027.12). It never merges (sub-step 3)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step

NAME = "run-done"
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
    if fused.changed_paths(WHERE, wt):
        raise fused.Stop(WHERE, "tree-check", 1)
    fused.checked(WHERE, fused.script("comment.sh"), n, "done", cwd=wt)
    cleared = asked in (0, 2)
    if cleared:
        fused.checked(WHERE, fused.script("stop-requested.sh"), "--clear", cwd=wt)
    return fused.settle(wt, n, NAME, ["stop_requested=%d" % asked, "cleared=%d" % cleared])


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
