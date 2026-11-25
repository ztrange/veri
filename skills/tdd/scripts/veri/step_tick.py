"""step-tick.sh's computation, run in-process: the close of a step no cycle closes (DIFF-CHECKED.md's PASS bullet),
in one call (PRD 038.3 DST6): the tick, its commit and push, the stop ask, and step-close.sh's mirror and next stop,
reused by import."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step
import ledger
import run_dir
from ledger import handed_out
from step_close import mirror, next_stop

NAME = "step-tick"
USAGE = "usage: step-tick.sh <n>"
LEDGER = run_dir.ledger("", "%s")
# The kinds it closes, a step no cycle closes (038.4 adds ⟦skill-edit⟧; a cycle step's close is step-close.sh's) -> the
# subject its tick commits under: a ⟦diff-checked⟧ one the one runs use (PRD 038.3 S14), a ⟦go-red⟧ one a test commit,
# since its product is the proof a guard's case goes red (#4443).
SUBJECTS = {"⟦diff-checked⟧": "chore: diff-checked — %s (#%s)", ledger.GO_RED_MARK: "test: go-red — %s (#%s)",
            "⟦skill-edit⟧": "chore: skill-edit — %s (#%s)"}

# The $S/ scripts this call makes, in the order each is first made (git and gh aside).
CALLS = ("tick-ledger.sh", "push-branch.sh", "stop-requested.sh", "comment.sh", "criterion-finished.sh",
         "ledger-steps.sh", "tick-issue-criterion.sh", "event.sh", "next-unchecked.sh", "run-affordable.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    step = fused_step.first_step(wt, n, handed_out)
    if step is None:
        sys.stderr.write("step-tick.sh: no open step in %s\n" % (LEDGER % n))
        return 2
    kind = (ledger.GO_RED_MARK if ledger.is_go_red(step) else "⟦skill-edit⟧" if ledger.is_skill_edit(step)
            else "⟦diff-checked⟧" if ledger.has_kind(step, "⟦diff-checked⟧") else None)
    if kind is None:
        sys.stderr.write("step-tick.sh: not a ⟦diff-checked⟧ step nor a ⟦go-red⟧ one: %s\n" % step)
        return 2
    # PRD 027 D10: the tree is checked before the irreversible act, so no change outside .tdd/ rides the tick commit.
    stray = [path for path in fused.changed_paths("tick", wt) if not path.startswith(".tdd/")]
    if stray:
        raise fused.Stop("tick", "tree-check " + " ".join(stray), 1)
    fused.checked("tick", fused.script("tick-ledger.sh"), LEDGER % n, step, cwd=wt)
    fused.checked("tick", "git", "add", "-A", cwd=wt)
    fused.checked("tick", "git", "commit", "-m", SUBJECTS[kind] % (fused_step.summary(step), n), cwd=wt)
    try:
        fused.checked("tick", fused.script("push-branch.sh"), cwd=wt)
        code, said, _ = fused.call(fused.script("stop-requested.sh"), cwd=wt)
        if code != 3:
            raise fused.Stop("tick", "stop-requested.sh exit %d%s" % (code, " " + said.strip() if said.strip() else ""),
                             code)
        mirror(wt, n, step)
        sys.stdout.write("next=%s\n" % next_stop(wt, n))
        return 0
    except (fused.Stop, fused.Waiting):
        raise
    except Exception as error:
        # Past the commit the push may have landed: an unforeseen error is no answer, never a redo of the tick.
        raise fused.Stop("tick", "%s %s" % (type(error).__name__, error), 2)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
