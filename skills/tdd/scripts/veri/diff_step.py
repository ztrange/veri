"""diff-step.sh's computation, run in-process: a ⟦diff-checked⟧ step's clean path (DIFF-CHECKED.md), sliced like the
fused halves of a step, ending on step-tick.sh (PRD 038.3)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import run_dir
from ledger import handed_out, has_kind

NAME = "diff-step"
USAGE = "usage: diff-step.sh <n>"
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = run_dir.ledger("", "%s")
KIND = "⟦diff-checked⟧"

# The $S/ scripts this call makes, in the order each is first made (git aside).
CALLS = ("build-develop-prompt.sh", "stop-requested.sh", "detach-leaf.sh", "supervise.sh", "run-leaf.sh",
         "wait-leaf.sh", "suite-reported.sh", "diff-leaf-deviation.sh", "run-verdict.sh", "step-tick.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER, SPEC)
    if given is None:
        return 2
    settled, wt = given
    step = fused_step.first_step(wt, n, handed_out)
    if step is None or not has_kind(step, KIND):
        sys.stderr.write("diff-step.sh: no open %s step in %s\n" % (KIND, LEDGER % n))
        return 2
    resumed = fused.load_wait(wt, n, NAME)
    at, values = resumed if resumed is not None else develop(n, wt, settled, step)
    if at == "develop-diff":
        code = fused.wait(wt, n, NAME, "develop-diff")
        if code != 0:
            raise fused.Stop("develop", "wait-leaf.sh develop-diff exit %d" % code, code)
        at = verify(n, wt, settled, step, values)
    if at == "verdict-diff":
        code = fused.wait(wt, n, NAME, "verdict-diff", rejected_step=step)
        if code != 0:
            raise fused.Stop("verify", "wait-leaf.sh verdict-diff exit %d" % code, code)
    if has_kind(step, "⟦test-quality⟧"):
        flip(n, wt, step, values)
    fused.checked("tick", fused.script("step-tick.sh"), n, cwd=wt)
    return 0


def flip(n, wt, step, values):
    """The flip of a ⟦test-quality⟧ step (DST3): the last `FLIP: <test file> '<old>→<new>'` line of the report of the
    leaf that made the step's last commit, probed with the `veri: one test file:` command on that file, else the
    all-tier one. The probe's 0 goes on; its 1, or no readable FLIP: line, is a verify-diff REJECT; its 2, or a
    detect-test-command.sh 2, no answer. The FLIP: line is read here, never handed to a verifier (DST12)."""
    leaf = values["leaf"]
    said = fused.report("flip", wt, ".tdd/%s.out" % leaf, "FLIP")["FLIP"]
    parsed = parse_flip(said or "")
    if parsed is None:
        reject(n, wt, step, values, "flip", "REJECT: the report of %s carries no FLIP: line\n" % leaf)
    path, old, new = parsed
    code, alone, _ = fused.call(fused.script("detect-test-command.sh"), "--tier", "one test file", cwd=wt)
    if code == 0:
        command = ("sh", "-c", alone.strip(), "sh", path)
    elif code == 3:
        command = ("sh", "-c", fused.checked("flip", fused.script("detect-test-command.sh"), "--tier", "all",
                                             cwd=wt).strip())
    else:
        raise fused.Stop("flip", "detect-test-command.sh --tier one test file exit %d" % code, 2)
    code = fused.call(fused.script("mutation-probe.sh"), path, old, new, "--", *command, cwd=wt,
                      out=".tdd/flip-probe.out")[0]
    if code == 1:
        reject(n, wt, step, values, "flip", "REJECT: flipping %s→%s in %s left %s green\n" % (old, new, path, path))
    if code != 0:
        raise fused.Stop("flip", "mutation-probe.sh exit %d" % code, 2)


def parse_flip(value):
    """(test file, old, new) of a FLIP: value `<test file> '<old>→<new>'`; None when it is not one."""
    path, _, rest = value.strip().partition(" ")
    rest = rest.strip()
    if not path or len(rest) < 2 or rest[0] != "'" or rest[-1] != "'" or "→" not in rest:
        return None
    old, _, new = rest[1:-1].partition("→")
    return path, old, new


def reject(n, wt, step, values, where, reason):
    """A verify-diff REJECT the stage itself finds (the flip): <reason> written to
    .tdd/verify-diff.reason, the step's rejected record left as a verifier's REJECT leaves it, so revise.sh <n> diff
    takes the step up; then a stop with exit 1."""
    import json
    with open(os.path.join(wt, ".tdd", "verify-diff.reason"), "w") as f:
        f.write(reason)
    with open(fused.wait_record(wt, n, NAME + "-rejected"), "w") as f:
        json.dump({"conductor": fused.conductor(wt), "at": "verdict-diff", "values": values, "step": step}, f)
    raise fused.Stop(where, reason.strip(), 1)


def develop(n, wt, settled, step):
    """The step base sha, a committed fact (the ledger's last commit, DIFF-CHECKED.md), then the develop-diff leaf's
    launch. (at, values) for the wait."""
    base = fused.checked("develop", "git", "log", "-1", "--format=%H", "--", LEDGER % n, cwd=wt).strip()
    fast = settled["fast_cmd"]
    fused.checked("develop", fused.script("build-develop-prompt.sh"), "diff", SPEC % n, step, fast, fast, cwd=wt,
                  out=".tdd/develop-diff.prompt")
    fused.launch("develop", wt, "develop-diff", "run-leaf.sh", ".tdd/develop-diff.prompt", "--permission-mode",
                 "bypassPermissions", env=fused.step_env(n, step, VERI_TEST_CMD=fast), out=".tdd/develop-diff.out",
                 err=".tdd/develop-diff.err")
    values = {"step_base": base, "leaf": "develop-diff"}
    fused.save_wait(wt, n, NAME, "develop-diff", values)
    return "develop-diff", values


def verify(n, wt, settled, step, values):
    """The leaf's checks, then the verifier: suite-reported.sh (its 2, no SUITE: line, stops for the conductor's
    adjudication), diff-leaf-deviation.sh (0 a deviation recorded, 3 none, both going on), then verdict-diff, or its recorded skip with `diff` switched off (ADR-0033): the leaf launched, or None."""
    leaf = values["leaf"]
    fused.checked("develop", fused.script("suite-reported.sh"), leaf, cwd=wt, err=".tdd/suite-reported.err")
    fused.checked("develop", fused.script("diff-leaf-deviation.sh"), leaf, values["step_base"], LEDGER % n, cwd=wt,
                  ok=(0, 3))
    if has_kind(step, "⟦test-quality⟧") and possible_bug(wt, leaf):
        return None
    if fused_step.verify_switched_off(wt, n, "diff"):
        fused.mark("verify", wt, n, step, "verify-diff-skipped", "reason=switched-off")
        with open(os.path.join(wt, ".tdd", "verdict-diff.exit"), "w") as f:
            f.write("skipped\n")
        return None
    launch_verdict("verify", n, wt, settled, step, values)
    fused.save_wait(wt, n, NAME, "verdict-diff", values)
    return "verdict-diff"


def possible_bug(wt, leaf):
    """The last `POSSIBLE-BUG:` line of <leaf>'s report, or None: a strengthened case the leaf found red, reverted and
    left uncommitted (SG2), so no verdict-diff judges the step."""
    return fused.report("develop", wt, ".tdd/%s.out" % leaf, "POSSIBLE-BUG")["POSSIBLE-BUG"]


def launch_verdict(where, n, wt, settled, step, values):
    """verdict-diff's launch, stopping at <where>: the one set of run-verdict.sh arguments diff-step.sh and revise.sh's
    re-verify share, against the step base taken before the develop-diff leaf ran (REVISE.md *The diff phase*)."""
    fast = settled["fast_cmd"]
    fused.launch(where, wt, "verdict-diff", "run-verdict.sh", "--step", step, "--fast-cmd", fast,
                 "--branch-base", fused_step.branch_base(where, wt, n), "diff", SPEC % n, values["step_base"],
                 env=fused.step_env(n, step, VERI_TEST_CMD=fast), out=".tdd/verify-diff.reason",
                 err=".tdd/verify-diff.err")



if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
