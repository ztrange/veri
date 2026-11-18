"""resume-start.sh's computation, run in-process: RESUME.md sub-steps 1-4's fixed calls and the owed verify-plan
launch, made in one call (PRD 038.6)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import fused
import run_dir
import run_start

USAGE = "usage: resume-start.sh <n>"


def inputs(n):
    """(preflight lines, run-start values) once every input file is readable; else None, each missing one named on
    stderr."""
    missing, lines, values = [], None, None
    try:
        with open(run_start.preflight_file(n)) as f:
            lines = f.read().splitlines()
    except OSError:
        missing.append(".tdd/issue-%s-preflight" % n)
    if lines is not None:
        wt = dict(line.split("=", 1) for line in lines if "=" in line).get("worktree", "")
        if not os.path.exists(run_dir.ledger(wt, n)):
            missing.append(os.path.relpath(run_dir.ledger(".", n)))
        try:
            values = fused.read_settled(run_dir.issue_file(wt, n, "-run-start"))
        except OSError:
            missing.append(".tdd/issue-%s-run-start" % n)
    for name in missing:
        sys.stderr.write("resume-start.sh: no %s\n" % name)
    return None if missing else (lines, values)


def main(argv):
    return fused.entry(argv, "resume-start.sh", run)


def run(n):
    given = inputs(n)
    if given is None:
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
