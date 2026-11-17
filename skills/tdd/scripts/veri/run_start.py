"""run-start.sh's computation, run in-process: SKILL.md step 1's fixed calls after preflight, made in one call
(PRD 027.13)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import run_dir

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
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
