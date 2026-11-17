"""step-close.sh's computation, run in-process: a step's close-out after a passing or skipped verify-refactor
(SKILL.md *Refactor loop*, sub-step 6's PASS branch), made in one call after a clean refactor-half.sh (PRD 027.8)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys
import time

import fused
import fused_step
import run_dir
import tunables
from green_half import summary
from next_pending_refactor import refactor_pending

NAME = "step-close"
USAGE = "usage: step-close.sh <n>"
LEDGER = run_dir.ledger("", "%s")
REFACTOR_HALF = ".tdd/issue-%s-refactor-half"


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER, REFACTOR_HALF)
    if given is None:
        return 2
    _, wt = given
    step = fused_step.first_step(wt, n, refactor_pending)
    half = read_half(wt, n)
    if step is None or half.get("step", [None])[0] != step:
        sys.stderr.write("step-close.sh: %s\n" % ("no refactor-pending step" if step is None else
                                                 ".tdd/issue-%s-refactor-half names another step" % n))
        return 2
    for uncovered in half.get("uncovered_spec", []):
        raise fused.Stop("6", "uncovered_spec=" + uncovered, 1)
    green_sha = half.get("green_sha", [""])[0]
    checks(wt, n, green_sha)
    commit(wt, n, step)
    return 0


def checks(wt, n, green_sha):
    """6's checks before the clear (CO2, CO3): graded units, the pins over the step's range, the refactored re-record.
    The `needs a look` pins pin-recheck.sh printed."""
    fused.checked("6", fused.script("graded-changed.sh"), green_sha, cwd=wt)
    base = fused.checked("6", "git", "rev-parse", green_sha + "~1", cwd=wt).strip()
    said = fused.checked("6", fused.script("pin-recheck.sh"), base, cwd=wt, ok=(0, 3))
    fused.checked("6", fused.script("tests-frozen.sh"), "rerecord-refactored", LEDGER % n, green_sha, cwd=wt)
    return said


def commit(wt, n, step):
    """The tree check (CO4, D10), then the clear, the `chore: refactor verified` commit and its push (CO5), the
    stage's end, and the stop ask after that push (CO6)."""
    allowed = {LEDGER % n, ".tdd/issue-%s-added.md" % n, ".tdd/issue-%s-refactor-owed.md" % n}
    if set(fused.changed_paths("6", wt)) - allowed:
        raise fused.Stop("6", "tree-check", 1)
    fused.checked("6", fused.script("clear-refactor-pending.sh"), LEDGER % n, step, cwd=wt)
    fused.checked("6", "git", "add", "-A", cwd=wt)
    fused.checked("6", "git", "commit", "-m", "chore: refactor verified for %s (#%s)" % (summary(step), n), cwd=wt)
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
    except (OSError, ValueError):
        raise fused.Stop("6", "no .tdd/stage-rl.t", 2)
    fused.checked("6", fused.script("event.sh"), "stage-end", "stage=refactor-loop", "status=0",
                  "secs=%d" % (int(time.time()) - started), cwd=wt, env=tunables.with_values(VERI_ISSUE=n))


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
