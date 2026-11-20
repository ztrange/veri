"""skill-edit-half.sh's computation, run in-process: a ⟦skill-edit⟧ step's clean path in one call (PRD 038.4, #4450)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import ledger
import run_start

DETACH = fused.script("detach-command.sh")
STEP = fused.script("skill-edit-step.sh")
TICK = fused.script("step-tick.sh")
USAGE = 'usage: skill-edit-half.sh <n> [--change "<change>"]'


def main(argv):
    with fused.quiet():
        return run(argv)


def run(argv):
    if not argv:
        sys.stderr.write(USAGE + "\n")
        return 2
    n = argv[0]
    wt = fused.read_settled(run_start.preflight_file(n))["worktree"]
    _, body, _ = fused.call("gh", "api", "repos/{owner}/{repo}/issues/%s" % n, "-q", ".body", cwd=wt)
    with open(os.path.join(wt, ".tdd", "issue-%s-body" % n), "w") as f:
        f.write(body)
    with open(ledger.ledger_path(wt, n)) as f:
        step = next(line for line in f if line.startswith(ledger.OPEN_STEP + " "))
    body_file = os.path.join(".tdd", "issue-%s-body" % n)
    added = ["--added", step.rstrip("\n")] if ledger.is_added(step.rstrip("\n")) else []
    fused.call(DETACH, "start", "skill-edit-" + n, STEP, *added, body_file, ledger.unit_of(step), cwd=wt)
    fused.call(DETACH, "wait", "skill-edit-" + n, cwd=wt)
    return fused.call(TICK, n, cwd=wt)[0]


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
