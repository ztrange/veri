"""seam-settle.sh's computation, run in-process: after a stage done by hand, write the record that stage's script
would have written, so the next stage runs as after a clean call (PRD 038.1 SC6, SC7)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step
import run_dir
from ledger import handed_out
from next_pending_refactor import refactor_pending

USAGE = "usage: seam-settle.sh <n> <stage> key=value…"
LEDGER = run_dir.ledger("", "%s")


def main(argv):
    n, stage, pairs = argv[0], argv[1], argv[2:]
    given = fused_step.inputs("seam-settle.sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    values = dict(pair.split("=", 1) for pair in pairs)
    step = fused_step.first_step(wt, n, handed_out if stage == "red-half" else refactor_pending)
    return fused.settle(wt, n, stage, ["step=" + step] + RECORDS[stage](wt, n, values))


def red_half(wt, n, values):
    target = values["target_test"]
    return ["test_path=" + values["test_path"], "target_test=" + target,
            "red_test_id=" + fused_step.red_test_id(values["test_path"], target), "against_unmodified=FAILS"]


def green_half(wt, n, values):
    return ["green_sha=" + green_sha(wt, n), "test_path=" + values["test_path"]]


def refactor_half(wt, n, values):
    return ["green_sha=" + green_sha(wt, n), "verdict_log=" + fused_step.verdict_log(wt)]


def green_sha(wt, n):
    """The step's green commit as refactor-half.sh reads it: the last commit that changed the ledger."""
    code, out, _ = fused.run_script("git", "log", "-1", "--format=%H", "--", LEDGER % n, cwd=wt)
    if code != 0 or not out.strip():
        raise RuntimeError("git log -1 -- %s exit %d" % (LEDGER % n, code))
    return out.strip()


# The record each stage's script writes after `step=`, from the stage's contract values and the committed facts.
RECORDS = {"red-half": red_half, "green-half": green_half, "refactor-half": refactor_half}


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
