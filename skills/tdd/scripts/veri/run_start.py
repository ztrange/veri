"""run-start.sh's computation, run in-process: SKILL.md step 1's fixed calls after preflight, made in one call
(PRD 027.13)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import run_dir
import tunables

USAGE = "usage: run-start.sh <n>"


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
    """Step 1's sub-steps 2-4 in the worktree preflight settled, in their order."""
    wt = settled["worktree"]
    fused.checked("1.2", fused.script("leaf-timeout.sh"), settled["baseline"], "--full", settled["full"], cwd=wt,
                  env=tunables.with_values(VERI_ISSUE=n))
    fused.checked("1.3", fused.script("capture-spec.sh"), n, cwd=wt, into=os.path.join(".tdd", "issue-%s-spec.md" % n))
    ignored = fused.checked("1.4", fused.script("ensure-run-state-ignored.sh"), cwd=wt).strip()
    if ignored == "added":
        listed = fused.checked("1.4", "git", "status", "--porcelain", cwd=wt).splitlines()
        if [line for line in listed if line[3:] != ".gitignore"]:
            raise fused.Stop("1.4", "tree-check", 1)
        fused.checked("1.4", "git", "add", ".gitignore", cwd=wt)
        fused.checked("1.4", "git", "commit", "-m", "chore: ignore veri run state (#%s)" % n, cwd=wt)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
