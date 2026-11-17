"""run-done.sh's computation, run in-process: DRAFT-PR.md sub-step 4 on its clean path, the stop ask, the final done
comment and the clearing of a reported stop request, made in one call (PRD 027.12). It never merges (sub-step 3)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step

NAME = "run-done"


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
