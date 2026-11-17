"""pr-ready-wait.sh's computation, run in-process: DRAFT-PR.md sub-step 2's first block on its clean path, the PR
url read, readying the PR and its first CI wait, made in one call (PRD 027.10)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step

NAME = "pr-ready-wait"


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n)
    if given is None:
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
