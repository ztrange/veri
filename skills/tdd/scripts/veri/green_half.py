"""green-half.sh's computation, run in-process: a step's Green half on the PASS path (SKILL.md *Green*, sub-steps
1-3), made in one call after a clean red-half.sh (PRD 027.5)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import fused_step
import ledger
import plan_publish
import replaces_case
import run_dir
from ledger import handed_out

NAME = "green-half"
USAGE = "usage: green-half.sh <n>"
SPEC = ".tdd/issue-%s-spec.md"
LEDGER = run_dir.ledger("", "%s")
RED_HALF = ".tdd/issue-%s-red-half"

# The $S/ scripts this call makes, in the order each is first made (git and gh aside); unit/test_green_half.py fails
# when one is a script SKILL.md's Green section does not name, save two it exempts by name (FC19).
CALLS = ("build-develop-prompt.sh", "stop-requested.sh", "detach-leaf.sh", "supervise.sh", "run-leaf.sh",
         "wait-leaf.sh", "step-cost.sh", "step-budget.sh", "extract-result.sh", "suite-reported.sh",
         "tests-frozen.sh", "event.sh", "run-verdict.sh", "comment.sh", "graded-changed.sh", "tick-ledger.sh",
         "push-branch.sh", "pr-body.sh")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER, SPEC, RED_HALF)
    if given is None:
        return 2
    settled, wt = given
    red = fused.read_settled(os.path.join(wt, RED_HALF % n))
    step = fused_step.first_step(wt, n, handed_out)
    if step is None or not ledger.same_step(red.get("step", ""), step):
        sys.stderr.write("green-half.sh: .tdd/issue-%s-red-half names another step than the open one\n" % n)
        return 2
    if replaces_case.is_replaces_case_step(step) or "⟦ci-repair⟧" in step:
        sys.stderr.write("green-half.sh: a step its prose runs: %s\n" % step)
        return 2
    values = {"test_path": red["test_path"], "target_test": red["target_test"]}
    at = (fused.load_wait(wt, n, NAME) or (develop(n, wt, settled, step, values), None))[0]
    if at == "develop-green":
        waited(wt, n, "1", "develop-green", step)
        at = verify(n, wt, settled, step, values)
    if at == "verdict-green":
        waited(wt, n, "2", "verdict-green", step)
    return finish(n, wt, step, values)


def waited(wt, n, where, name, step):
    """A leaf's wait, then the step's cost check (RH4); a leaf's 1 or 2 stops it at <where> before that check, which
    the conductor's prose then makes."""
    code = fused.wait(wt, n, NAME, name)
    if code != 0:
        raise fused.Stop(where, "wait-leaf.sh %s exit %d" % (name, code), code)
    fused_step.cost_check(wt, step)


def develop(n, wt, settled, step, values):
    """Green 1's launch (GH2): the green prompt from the Red values and the fast tier, no owed cases."""
    fast = settled["fast_cmd"]
    fused.checked("1", fused.script("build-develop-prompt.sh"), "green", SPEC % n, step, fast, values["test_path"],
                  values["target_test"], fast, cwd=wt, out=".tdd/develop-green.prompt")
    fused.launch("1", wt, "develop-green", "run-leaf.sh", ".tdd/develop-green.prompt", "--permission-mode",
                 "bypassPermissions", env=fused.step_env(n, step, VERI_TEST_CMD=fast), out=".tdd/develop-green.out",
                 err=".tdd/develop-green.err")
    fused.save_wait(wt, n, NAME, "develop-green", values)
    return "develop-green"


# The report lines that route a Green elsewhere (GH4): the conductor's routes, never this call's.
ROUTES = ("WRONG_TEST", "SUPERSEDED", "SPLIT", "TIDY_FIRST")


def verify(n, wt, settled, step, values):
    """Green 1's checks, then Green 2's verifier (GH3-GH6): the route lines first, since a split or wrong-test report
    carries no SUITE: line by design, then suite-reported.sh and the two frozen-test checks, then verdict-green, or its
    recorded skip with `green` switched off. The leaf it launched, or None."""
    got = fused.report("1", wt, ".tdd/develop-green.out", *ROUTES)
    for key in ROUTES:
        if got[key] is not None:
            raise fused.Stop("1", "%s: %s" % (key, got[key]), 1)
    fused.checked("1", fused.script("suite-reported.sh"), "develop-green", cwd=wt, err=".tdd/suite-reported.err")
    fused.checked("1", fused.script("tests-frozen.sh"), "check", "--step", step, cwd=wt)
    fused.checked("1", fused.script("tests-frozen.sh"), "check-earlier", LEDGER % n, "--step", step, cwd=wt)
    if fused_step.verify_switched_off(wt, n, "green"):
        fused.mark("2", wt, n, step, "verify-green-skipped", "reason=switched-off")
        with open(os.path.join(wt, ".tdd", "verdict-green.exit"), "w") as f:
            f.write("skipped\n")
        return None
    fast = settled["fast_cmd"]
    fused.launch("2", wt, "verdict-green", "run-verdict.sh", "--step", step, "--fast-cmd", fast, "green", SPEC % n,
                 values["test_path"], values["target_test"], env=fused.step_env(n, step, VERI_TEST_CMD=fast),
                 out=".tdd/verify-green.reason", err=".tdd/verify-green.err")
    fused.save_wait(wt, n, NAME, "verdict-green", values)
    return "verdict-green"


def finish(n, wt, step, values):
    """Green 3 on a PASS (GH7-GH12): both comments, the graded check, the frozen tests once more, the atomic
    tick-and-commit (ADR-0007), the push, the PR body, the stop ask, and the settled file."""
    fused.checked("3", fused.script("comment.sh"), n, "green", cwd=wt)
    fused.checked("3", fused.script("comment.sh"), n, "verify-green", cwd=wt)
    base = fused.checked("3", "git", "log", "-1", "--format=%H", "--", LEDGER % n, cwd=wt).strip()
    fused.checked("3", fused.script("graded-changed.sh"), base, cwd=wt)
    fused.checked("3", fused.script("tests-frozen.sh"), "check", "--step", step, cwd=wt)
    fused.checked("3", fused.script("tick-ledger.sh"), "--refactor-pending", LEDGER % n, step, cwd=wt)
    fused.checked("3", "git", "add", "-A", cwd=wt)
    fused.checked("3", "git", "commit", "-m", "%s: %s (#%s)" % (kind(wt, n), fused_step.summary(step), n), cwd=wt)
    green_sha = fused.checked("3", "git", "rev-parse", "HEAD", cwd=wt).strip()
    fused.checked("3", fused.script("push-branch.sh"), cwd=wt)
    pr_body(n, wt)
    code, said, _ = fused.call(fused.script("stop-requested.sh"), cwd=wt)
    if code != 3:
        raise fused.Stop("3", "stop-requested.sh exit %d%s" % (code, " " + said.strip() if said.strip() else ""), code)
    return fused.settle(wt, n, NAME, ["step=" + step, "green_sha=" + green_sha, "test_path=" + values["test_path"]])


def kind(wt, n):
    """`fix` when the spec holds the `## Bug` section capture-spec.sh writes for a bug issue, else `feat` (GH9)."""
    with open(os.path.join(wt, SPEC % n), encoding="utf-8", errors="replace") as f:
        return "fix" if "## Bug" in f.read().splitlines() else "feat"


def pr_body(n, wt):
    """Green 3's PR body, `<done> of <total>` counted from the ticked ledger, on the PR read from the branch as
    RESUME.md sub-step 4 reads it (GH10)."""
    branch = fused.checked("3", "git", "branch", "--show-current", cwd=wt).strip()
    url = plan_publish.gh("3", "api", "repos/{owner}/{repo}/pulls?head={owner}:%s" % branch, "-q",
                          ".[0].html_url // empty", wt=wt).strip()
    if not url:
        raise fused.Stop("3", "no PR for " + branch, 2)
    with open(os.path.join(wt, LEDGER % n), encoding="utf-8", errors="surrogateescape") as f:
        records = ledger.ledger_steps(f.read())
    body = ".tdd/green-half-pr-body.md"
    with open(os.path.join(wt, body), "w") as f:
        f.write("Closes #%s — work in progress: %d of %d steps done. The ledger %s is the source of truth.\n"
                % (n, len([r for r in records if r.state == "done"]), len(records), LEDGER % n))
    fused.checked("3", fused.script("pr-body.sh"), url.rstrip("/").rsplit("/", 1)[-1], body, cwd=wt)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
