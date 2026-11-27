"""red-half.sh's computation, run in-process: a step's Red half on the FAILS path (SKILL.md *Red*, sub-steps 1-3),
made in one call (PRD 027.4)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import case_reader
import covering_tests
import fused
import fused_step
import ledger
import replaces_case
import run_dir
from ledger import handed_out

NAME = "red-half"
USAGE = "usage: red-half.sh <n>"
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = run_dir.ledger("", "%s")
# The step kinds whose Red is not this one (RH1): they run from their own files or need a route's --except.
REFUSED = ("⟦diff-checked⟧", ledger.GO_RED_MARK, "⟦phases:", "⟦skill-edit⟧", "⟦fixture-repair⟧")


def refused(step):
    """The REFUSED kinds <step> is, in REFUSED's order; ⟦go-red⟧ by ledger.is_go_red, the others by ledger.has_kind:
    the trailing marker run or a leading ⟦skill-edit⟧; a mark quoted anywhere else, or leading any other step, is
    no kind (#4709)."""
    return [kind for kind in REFUSED if (ledger.is_go_red(step) if kind == ledger.GO_RED_MARK
                                         else ledger.has_kind(step, kind))]

# The $S/ scripts this call makes, in the order each is first made (git aside); unit/test_red_half.py fails when one
# is a script SKILL.md's Red section does not name, save three it exempts by name (FC19).
CALLS = ("refresh-spec.sh", "build-develop-prompt.sh", "stop-requested.sh", "detach-leaf.sh", "supervise.sh",
         "run-leaf.sh", "wait-leaf.sh", "step-cost.sh", "step-budget.sh", "extract-result.sh", "red-divergence.sh",
         "unreplaced-cases.sh", "tests-frozen.sh", "event.sh", "run-verdict.sh", "red-setup.sh", "comment.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER, SPEC)
    if given is None:
        return 2
    settled, wt = given
    step = fused_step.first_step(wt, n, handed_out)
    if step is None or refused(step):
        sys.stderr.write("red-half.sh: %s\n" % ("no open step" if step is None else "a step its prose runs: " + step))
        return 2
    resumed = fused.load_wait(wt, n, NAME)
    at, values = resumed if resumed is not None else ("develop-red", develop(n, wt, settled, step))
    if at == "develop-red":
        waited(wt, n, "1", "develop-red", step)
        values.update(red_report(wt))
        at = verify(n, wt, settled, step, values)
    if at == "verdict-red":
        waited(wt, n, "2", "verdict-red", step)
    return finish(n, wt, step, values)


def verify(n, wt, settled, step, values):
    """Red 2 up to the verifier: the prediction gate (RH6), on a ⟦replaces-case⟧ step the replaced-case check (RH7),
    the earlier steps' records (RH8), then verdict-red (RH9), or its recorded skip when `red` is switched off. The
    leaf it launched, or None."""
    gate = fused.call(fused.script("red-divergence.sh"), ".tdd/red-prediction.md", ".tdd/red-run-output.txt", cwd=wt,
                      stdin=read(wt, ".tdd/develop-red.out"), out=".tdd/verify-red.reason")[0]
    if gate != 3:
        raise fused.Stop("2", fused.label("red-divergence.sh", ".tdd/red-prediction.md", ".tdd/red-run-output.txt")
                         + " exit %d" % gate, gate)
    excepted = ()
    if replaces_case.is_replaces_case_step(step):
        fused.checked("2", fused.script("unreplaced-cases.sh"), step, ".tdd/develop-red.out", cwd=wt,
                      err=".tdd/unreplaced-cases.err")
        excepted = (replaces_case.parse(step) or ([], ""))[0]
    fused.checked("2", fused.script("tests-frozen.sh"), "check-earlier", LEDGER % n, "--step", step,
                  *[arg for case in excepted for arg in ("--except", case)], cwd=wt)
    if fused_step.verify_switched_off(wt, n, "red"):
        fused.mark("2", wt, n, step, "verify-red-skipped", "reason=switched-off")
        with open(os.path.join(wt, ".tdd", "verdict-red.exit"), "w") as f:
            f.write("skipped\n")
        return None
    launch_verdict("2", n, wt, settled, step, values)
    fused.save_wait(wt, n, NAME, "verdict-red", values)
    return "verdict-red"


def launch_verdict(where, n, wt, settled, step, values):
    """verdict-red's launch, stopping at <where>: the one set of run-verdict.sh arguments red-half.sh and revise.sh's
    re-verify share (PRD 038.9 RVS13)."""
    fused.launch(where, wt, "verdict-red", "run-verdict.sh", "--step", step, "--fast-cmd", settled["fast_cmd"],
                 "--branch-base", fused_step.branch_base(where, wt, n), "red",
                 SPEC % n, values["test_path"], values["target_test"],
                 env=fused.step_env(n, step, VERI_TEST_CMD=settled["fast_cmd"]), out=".tdd/verify-red.reason",
                 err=".tdd/verify-red.err")


def finish(n, wt, step, values):
    """Red 2's record and Red 3's comments on the PASS path (RH9-RH12): the frozen tests recorded with the Red case,
    red-setup.sh's record, the tree checked, the Red and verify-red comments, and the settled file."""
    target = values["target_test"]
    red_test_id = fused_step.red_test_id(values["test_path"], target)
    revised = values.get("revised")  # revise.sh recorded both on the revised report and posted verify-revised
    if not revised:
        fused.checked("2", fused.script("tests-frozen.sh"), "record", "--step", step, "--red-case", red_test_id,
                      values["test_path"], cwd=wt, out=".tdd/verify-red.reason")
        fused.checked("2", fused.script("red-setup.sh"), "record", n, cwd=wt, ok=(0, 2, 3),
                      stdin=read(wt, ".tdd/develop-red.out"))
    if [p for p in fused.changed_paths("3", wt) if not p.startswith(".tdd/") and not case_reader.is_test_path(p)]:
        raise fused.Stop("3", "tree-check", 1)
    note = ".tdd/red-half-note.md"
    with open(os.path.join(wt, note), "w") as f:
        f.write(REFRESHED.get(values.get("refresh"), "") + "Prediction matched: verify-red judged the test.\n")
    fused.checked("3", fused.script("comment.sh"), n, "red", "--note-file", note, cwd=wt)
    if not revised:
        fused.checked("3", fused.script("comment.sh"), n, "verify-red", cwd=wt)
    return fused.settle(wt, n, NAME, ["step=" + step, "test_path=" + values["test_path"], "target_test=" + target,
                                      "red_test_id=" + red_test_id, "against_unmodified=FAILS"])


# What the Red comment says of refresh-spec.sh's exit (Red 1): 0 a refreshed spec, 2 the capture kept.
REFRESHED = {0: "Spec refreshed from the issue before this step.\n",
             2: "Spec refresh failed; this step ran on the capture.\n"}


def read(wt, path):
    with open(os.path.join(wt, path), encoding="utf-8", errors="replace") as f:
        return f.read()


def waited(wt, n, where, name, step):
    """A leaf's wait, then the step's cost check (RH4); a leaf's 1 or 2 stops it at <where> before that check, which
    the conductor's prose then makes."""
    code = fused.wait(wt, n, NAME, name, rejected_step=step)
    if code != 0:
        raise fused.Stop(where, "wait-leaf.sh %s exit %d" % (name, code), code)
    fused_step.cost_check(wt, step)


def develop(n, wt, settled, step):
    """Red 1: refresh the spec (0, 2 and 3 go on), build the red prompt, and launch develop-red (RH2, RH3)."""
    refreshed = fused.call(fused.script("refresh-spec.sh"), n, SPEC % n, cwd=wt)[0]
    if refreshed == 1:
        raise fused.Stop("1", fused.label("refresh-spec.sh", n, SPEC % n) + " exit 1", 1)
    fused.checked("1", fused.script("build-develop-prompt.sh"), "red", SPEC % n, step, settled["fast_cmd"], cwd=wt,
                  out=".tdd/develop-red.prompt")
    fused.launch("1", wt, "develop-red", "run-leaf.sh", ".tdd/develop-red.prompt", "--permission-mode",
                 "bypassPermissions", env=fused.step_env(n, step, VERI_TEST_CMD=settled["fast_cmd"]),
                 out=".tdd/develop-red.out", err=".tdd/develop-red.err",
                 clear=(".tdd/red-prediction.md", ".tdd/red-run-output.txt"))
    values = {"refresh": refreshed}
    fused.save_wait(wt, n, NAME, "develop-red", values)
    return values


def red_report(wt):
    """Red 1's three report lines, printed (RH5): a missing one stops with exit 2, PASSES or UNTESTABLE with 1, and HOLDS
    with 1 naming its COVERING_TESTS: ids (PRD 044.2)."""
    got = fused.report("1", wt, ".tdd/develop-red.out", "TEST_PATH", "TARGET_TEST", "AGAINST_UNMODIFIED",
                       "COVERING_TESTS")
    for key in ("TEST_PATH", "TARGET_TEST", "AGAINST_UNMODIFIED"):
        if got[key]:
            sys.stdout.write("%s=%s\n" % (key.lower(), got[key]))
    against = got["AGAINST_UNMODIFIED"]
    if against == "HOLDS":
        raise fused.Stop("2", "COVERING_TESTS: " + " ".join(covering_tests.ids(got["COVERING_TESTS"] or "")), 1)
    if against in ("PASSES", "UNTESTABLE"):
        raise fused.Stop("2", "AGAINST_UNMODIFIED: " + against, 1)
    for key in ("TEST_PATH", "TARGET_TEST", "AGAINST_UNMODIFIED"):
        if not got[key] or key == "AGAINST_UNMODIFIED" and against != "FAILS":
            raise fused.Stop("1", "no %s: line" % key, 2)
    return {"test_path": got["TEST_PATH"], "target_test": got["TARGET_TEST"]}


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
