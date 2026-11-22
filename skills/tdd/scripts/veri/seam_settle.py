"""seam-settle.sh's computation, run in-process: after a stage done by hand, write the record that stage's script
would have written, so the next stage runs as after a clean call (PRD 038.1 SC6, SC7)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import contextlib
import os
import sys

import entry
import event_log
import fused
import fused_step
import green_half as green_half_script
import run_dir
import seam_contract
from ledger import handed_out, same_step
from next_pending_refactor import refactor_pending

USAGE = "usage: seam-settle.sh <n> <stage> key=value…"
LEDGER = run_dir.ledger("", "%s")


def main(argv):
    if len(argv) < 2 or not argv[0].isdigit():
        return entry.refuse(usage=USAGE)
    n, stage, pairs = argv[0], argv[1], argv[2:]
    values = {}
    refusal = refused(stage, pairs, values)
    if refusal:
        return entry.refuse("seam-settle.sh: " + refusal, usage=USAGE)
    given = fused_step.inputs("seam-settle.sh", n, LEDGER)
    if given is None:
        return 2
    _, wt = given
    step = fused_step.first_step(wt, n, handed_out if stage == "red-half" else refactor_pending)
    if step is None and stage == "green-half" and revised(wt, n):
        code = fused.entry([n], "green-half.sh", green_half_script.run)
        if code != 0:
            return code
        step = fused_step.first_step(wt, n, refactor_pending)
    if step is None:
        return entry.refuse("seam-settle.sh: no open step for %s in %s" % (stage, LEDGER % n))
    code = fused.settle(wt, n, stage, ["step=" + step] + RECORDS[stage](wt, n, values, step))
    if stage == "red-half":
        # Red recovered by hand answers its REJECT: only revise.sh's finish removes this record otherwise, and a left
        # one would send a later bare run-step.sh call back to revise.sh <n> red (#4613).
        with contextlib.suppress(FileNotFoundError):
            os.remove(fused.wait_record(wt, n, "red-half-rejected"))
    return code


def revised(wt, n):
    """True when green-half's wait record is the one a revise.sh PASS re-saved (`revised`): its Green 3 is still owed
    (REVISE.md, PASS branch, #4551)."""
    resumed = fused.load_wait(wt, n, "green-half")
    return resumed is not None and bool(resumed[1].get("revised"))


def refused(stage, pairs, values):
    """Why <pairs> do not settle <stage> under its seam contract, or None, <values> filled with them (SC6)."""
    if stage not in seam_contract.CONTRACTS:
        return "unknown stage %s (one of %s)" % (stage, ", ".join(seam_contract.CONTRACTS))
    owed = seam_contract.CONTRACTS[stage]
    for pair in pairs:
        key, _, value = pair.partition("=")
        if key not in owed:
            return "unknown key %s for %s (its contract: %s)" % (key, stage, " ".join(owed) or "no key")
        if key in values:
            return "repeated key " + key
        if not value:
            return "empty key " + key
        if "\n" in value or "\r" in value:
            return "newline in key " + key
        values[key] = value
    missing = [key for key in owed if key not in values]
    return "missing key %s for %s" % (missing[0], stage) if missing else None


def red_half(wt, n, values, step):
    target = values["target_test"]
    return ["test_path=" + values["test_path"], "target_test=" + target,
            "red_test_id=" + fused_step.red_test_id(values["test_path"], target), "against_unmodified=FAILS"]


def green_half(wt, n, values, step):
    return ["green_sha=" + green_sha(wt, n), "test_path=" + values["test_path"]]


def refactor_half(wt, n, values, step):
    """The verdict as the automatic path's record names it: the log's hash and its `uncovered-spec` flags (#4029),
    the flags left out when the step's verify was skipped, as refactor-half.sh leaves them out: the log is then an
    earlier step's."""
    verdict_log, uncovered = fused_step.verdict(wt)
    return (["green_sha=" + green_sha(wt, n), "verdict_log=" + verdict_log]
            + ["uncovered_spec=" + flag for flag in uncovered if not verify_skipped(wt, step)])


def verify_skipped(wt, step):
    """True when the step's last verify-refactor event in the journal is `verify-refactor-skipped` (SKILL.md Refactor
    5) rather than a refactor `verdict`: no verifier ran for it since, so no log is its."""
    found = [e for e in event_log.events(wt, "verify-refactor-skipped", "verdict", skip_unreadable=True)
             if (e.get("event") != "verdict" or e.get("phase") == "refactor") and same_step(e.get("step", ""), step)]
    return bool(found) and found[-1].get("event") == "verify-refactor-skipped"


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
