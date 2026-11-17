"""red-half.sh's computation, run in-process: a step's Red half on the FAILS path (SKILL.md *Red*, sub-steps 1-3),
made in one call (PRD 027.4)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
from ledger import handed_out

NAME = "red-half"
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = ".tdd/issue-%s.md"
# The step kinds whose Red is not this one (RH1): they run from their own files or need a route's --except.
REFUSED = ("⟦diff-checked⟧", "⟦phases:", "⟦skill-edit⟧", "⟦fixture-repair⟧")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused.inputs(NAME + ".sh", n, LEDGER, SPEC)
    if given is None:
        return 2
    settled, wt = given
    step = fused.first_step(wt, n, handed_out)
    if step is None or any(kind in step for kind in REFUSED):
        sys.stderr.write("red-half.sh: %s\n" % ("no open step" if step is None else "a step its prose runs: " + step))
        return 2
    values = develop(n, wt, settled, step)
    waited(wt, n, "1", "develop-red", step)
    values.update(red_report(wt))
    return 0


def waited(wt, n, where, name, step):
    """A leaf's wait, then the step's cost check (RH4); a leaf's 1 or 2 stops it at <where> before that check, which
    the conductor's prose then makes."""
    code = fused.wait(wt, n, NAME, name)
    if code != 0:
        raise fused.Stop(where, "wait-leaf.sh %s exit %d" % (name, code), code)
    fused.cost_check(wt, step)


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
    """Red 1's three report lines, printed (RH5): a missing one stops with exit 2, PASSES or UNTESTABLE with 1."""
    got = fused.report("1", wt, "develop-red", "TEST_PATH", "TARGET_TEST", "AGAINST_UNMODIFIED")
    for key in ("TEST_PATH", "TARGET_TEST", "AGAINST_UNMODIFIED"):
        if got[key]:
            sys.stdout.write("%s=%s\n" % (key.lower(), got[key]))
    against = got["AGAINST_UNMODIFIED"]
    if against in ("PASSES", "UNTESTABLE"):
        raise fused.Stop("2", "AGAINST_UNMODIFIED: " + against, 1)
    for key in ("TEST_PATH", "TARGET_TEST", "AGAINST_UNMODIFIED"):
        if not got[key] or key == "AGAINST_UNMODIFIED" and against != "FAILS":
            raise fused.Stop("1", "no %s: line" % key, 2)
    return {"test_path": got["TEST_PATH"], "target_test": got["TARGET_TEST"]}


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
