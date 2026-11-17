"""pr-finish.sh's computation, run in-process: DRAFT-PR.md sub-step 2's second block up to the refactor-owed render on
its clean path, after the first wait-ci.sh exited 0, made in one call (PRD 027.11). The PR's title and body stay the
conductor's."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import fused
import fused_step
import run_dir

NAME = "pr-finish"
LEDGER = run_dir.ledger("", "%s")


def main(argv):
    return fused.entry(argv, NAME + ".sh", run)


def run(n):
    given = fused_step.inputs(NAME + ".sh", n, LEDGER)
    if given is None:
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
