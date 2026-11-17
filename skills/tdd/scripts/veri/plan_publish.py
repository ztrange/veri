"""plan-publish.sh's computation, run in-process: SKILL.md step 2's fixed tail once the plan is written (sub-steps 2-4,
step 2b, and step 2c up to its PASS branch), made in one call (PRD 027.3)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import run_dir
import run_start

USAGE = "usage: plan-publish.sh <n> <title-file>"


def inputs(n, title_file):
    """(settled preflight values, title) once every input file is readable; else None, each missing one named on
    stderr."""
    missing = []
    try:
        settled = fused.read_settled(run_start.preflight_file(n))
    except OSError:
        settled = None
        missing.append(".tdd/issue-%s-preflight" % n)
    if settled is not None and not os.path.exists(run_dir.ledger(settled.get("worktree", ""), n)):
        missing.append(".tdd/issue-%s.md" % n)
    try:
        with open(title_file) as f:
            title = f.read().strip()
    except OSError:
        title = None
        missing.append(title_file)
    for name in missing:
        sys.stderr.write("plan-publish.sh: no %s\n" % name)
    return None if missing else (settled, title)


def main(argv):
    if len(argv) != 2 or not argv[0].isdigit():
        sys.stderr.write(USAGE + "\n")
        return 2
    n, title_file = argv
    given = inputs(n, title_file)
    if given is None:
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
