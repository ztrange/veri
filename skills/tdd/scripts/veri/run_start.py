"""run-start.sh's computation, run in-process: SKILL.md step 1's fixed calls after preflight, made in one call
(PRD 027.13)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import run_dir
import tunables

USAGE = "usage: run-start.sh <n>"

# The $S/ scripts this call makes, in its order (git aside); unit/test_run_start.py fails when one is a script SKILL.md
# step 1 does not name (FC19).
CALLS = ("leaf-timeout.sh", "capture-spec.sh", "ensure-run-state-ignored.sh", "plan-reverify.sh")


def preflight_file(n):
    """The settled file preflight.sh wrote for issue <n>: in its worktree under the main tree this is called from, or
    in this directory's .tdd/ when called from the worktree."""
    under_main = run_dir.issue_file(run_dir.worktree("", n), n, "-preflight")
    return under_main if os.path.exists(under_main) else run_dir.issue_file(".", n, "-preflight")


def main(argv):
    if len(argv) != 1 or not argv[0].isdigit():
        sys.stderr.write(USAGE + "\n")
        return 2
    n = argv[0]
    path = preflight_file(n)
    try:
        settled = fused.read_settled(path)
    except OSError:
        sys.stderr.write("run-start.sh: no .tdd/issue-%s-preflight: run preflight.sh first\n" % n)
        return 2
    try:
        return run(n, settled)
    except fused.Stop as stop:
        return fused.stopped(stop)


def run(n, settled):
    """Step 1's sub-steps 2-5 in the worktree preflight settled, in their order; 0 with .tdd/issue-<n>-run-start
    written and its lines printed last (ST3), else a Stop."""
    wt = settled["worktree"]
    reused = ("--reused",) if settled.get("full_tier_mode") == "reuse" else ()
    fused.checked("1.2", fused.script("leaf-timeout.sh"), settled["baseline"], "--full", settled["full"], *reused,
                  cwd=wt, env=tunables.with_values(VERI_ISSUE=n))
    spec = os.path.join(".tdd", "issue-%s-spec.md" % n)
    fused.checked("1.3", fused.script("capture-spec.sh"), n, cwd=wt, out=spec)
    ignored = fused.checked("1.4", fused.script("ensure-run-state-ignored.sh"), cwd=wt).strip()
    if ignored == "added":
        listed = fused.checked("1.4", "git", "status", "--porcelain", cwd=wt).splitlines()
        if [line for line in listed if line[3:] != ".gitignore"]:
            raise fused.Stop("1.4", "tree-check", 1)
        fused.checked("1.4", "git", "add", ".gitignore", cwd=wt)
        fused.checked("1.4", "git", "commit", "-m", "chore: ignore veri run state (#%s)" % n, cwd=wt)
    ledger = os.path.relpath(run_dir.ledger(".", n))
    resume = os.path.exists(os.path.join(wt, ledger))
    lines = ["run=" + ("resume" if resume else "fresh"), "spec=" + spec,
             "timeout_recorded=" + os.path.join(".tdd", "issue-%s-timeout" % n), "gitignore=" + ignored]
    if resume:
        code = fused.call(fused.script("plan-reverify.sh"), ledger, cwd=wt)[0]
        if code not in (0, 3):
            raise fused.Stop("1.5", "plan-reverify.sh %s exit %d" % (ledger, code), code)
        lines.append("verify_plan=" + ("owed" if code == 0 else "skip"))
    return fused.settle(wt, n, "run-start", lines)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
