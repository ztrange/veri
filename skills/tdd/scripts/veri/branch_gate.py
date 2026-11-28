"""branch-gate.sh's computation, run in-process: on entering the Draft PR step, whether CI stands in for the branch's
full run and, under `local`, that run and its recorded time (DRAFT-PR.md's opening paragraphs), made in one call
(PRD 027.7)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys
import time

import fused
import fused_step
import run_dir
import tunables
from ledger import handed_out

NAME = "branch-gate"
USAGE = "usage: branch-gate.sh <n>"
LEDGER = run_dir.ledger("", "%s")
WHERE = "opening"  # the replaced paragraphs come before sub-step 1 and carry no number of their own
RUN = "branch-full-%s"  # the full run's detach-command.sh name: .tdd/branch-full-<n>.out and .exit
DETACH = fused.script("detach-command.sh")

# The $S/ scripts this call makes, in the order each is first made; unit/test_branch_gate.py fails when one is a script
# DRAFT-PR.md's opening paragraphs do not name (FC19).
CALLS = ("branch-suite.sh", "detect-test-command.sh", "event.sh", "detach-command.sh", "full-tier-time.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    step = fused_step.first_step(wt, n, handed_out)
    if step is not None:
        sys.stderr.write("branch-gate.sh: an unchecked step is left, next-unchecked.sh would hand it out: %s\n" % step)
        return 2
    resumed = fused.load_wait(wt, n, NAME)
    if resumed is not None:
        values = resumed[1]
    else:
        mode = fused.checked(WHERE, fused.script("branch-suite.sh"), cwd=wt).strip()
        if mode == "ci":
            return fused.settle(wt, n, NAME, ["branch_suite=ci"])
        if mode != "local":
            raise fused.Stop(WHERE, "branch-suite.sh printed " + (mode or "nothing"), 2)
        values = start(wt, n)
        fused.save_wait(wt, n, NAME, RUN % n, values)
    code = fused.call(DETACH, "wait", RUN % n, cwd=wt)[0]
    if code == 3:
        raise fused.Waiting(RUN % n)
    os.remove(fused.wait_record(wt, n, NAME))
    secs = int(time.time()) - values["began"]
    mark(wt, n, "stage-end", "stage=full-suite", "status=%d" % code, "secs=%d" % secs)
    if code != 0:
        raise fused.Stop(WHERE, "detach-command.sh wait %s exit %d" % (RUN % n, code), code)
    fused.checked(WHERE, fused.script("full-tier-time.sh"), "--record", str(secs), values["full"], cwd=wt)
    return fused.settle(wt, n, NAME, ["branch_suite=local"])


def start(wt, n):
    """The full command detect-test-command.sh prints, started detached inside the `full-suite` stage: {"full",
    "began"}, the epoch second it started."""
    full = fused.checked(WHERE, fused.script("detect-test-command.sh"), "--tier", "all", cwd=wt).strip()
    mark(wt, n, "stage-start", "stage=full-suite")
    began = int(time.time())
    fused.checked(WHERE, DETACH, "start", RUN % n, "sh", "-c", full, cwd=wt)
    return {"full": full, "began": began}


def mark(wt, n, *fields):
    """`VERI_ISSUE=<n> VERI_ACTOR=conductor event.sh <fields>`, as the opening paragraphs mark the stage."""
    fused.checked(WHERE, fused.script("event.sh"), *fields, cwd=wt,
                  env=tunables.with_values(VERI_ISSUE=n, VERI_ACTOR="conductor"))


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
