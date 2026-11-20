"""skill-edit-half.sh's computation, run in-process: a ⟦skill-edit⟧ step's clean path in one call (PRD 038.4, #4450)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import run_start

USAGE = 'usage: skill-edit-half.sh <n> [--change "<change>"]'


def main(argv):
    if not argv:
        sys.stderr.write(USAGE + "\n")
        return 2
    n = argv[0]
    wt = fused.read_settled(run_start.preflight_file(n))["worktree"]
    _, body, _ = fused.call("gh", "api", "repos/{owner}/{repo}/issues/%s" % n, "-q", ".body", cwd=wt)
    with open(os.path.join(wt, ".tdd", "issue-%s-body" % n), "w") as f:
        f.write(body)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
