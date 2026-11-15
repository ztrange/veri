"""step-cost.sh's computation: what one step of the run has spent on leaves, read off the
run's `usage` events.

The figure is leaf spend only. The conductor's own spending is in no `usage` event, so it is
in no figure this prints — never quote one as "what this step cost" in full.
"""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import sys

import entry
import event_log

USAGE = "usage: step-cost.sh <step-text> | --run | --steps"
LOG = event_log.path("")


def main(argv):
    if len(argv) != 1:
        return entry.refuse("step-cost.sh: expected exactly one argument, got %d" % len(argv), usage=USAGE)
    step = argv[0]
    if step.startswith("-") and step not in ("--run", "--steps"):
        return entry.refuse("step-cost.sh: unknown option '%s'" % step, usage=USAGE)
    code, out = step_costs(step, logical_cwd())
    sys.stdout.write(out)
    return code


def cost(event):
    try:
        return float(event.get("total_cost_usd"))
    except (TypeError, ValueError):
        return 0.0


def logical_cwd():
    pwd = os.environ.get("PWD", "")
    try:
        if os.path.isabs(pwd) and os.path.samefile(pwd, "."):
            return pwd
    except OSError:
        pass
    return os.getcwd()


def step_costs(step, cwd):
    log_path = event_log.path(cwd)
    if not os.access(log_path, os.R_OK):
        sys.stderr.write("step-cost.sh: cannot read %s in %s — run from the run's worktree\n" % (LOG, cwd))
        return 2, ""
    usage = event_log.events(cwd, "usage", skip_unreadable=True, errors="strict")
    if step not in ("--run", "--steps"):
        usage = [e for e in usage if e.get("step", "") == step]
    if not usage:
        return 3, ""
    if step == "--steps":
        dollars, leaves = {}, {}
        for e in usage:
            s = e.get("step", "")
            dollars[s] = dollars.get(s, 0.0) + cost(e)
            leaves[s] = leaves.get(s, 0) + 1
        return 0, "".join("%.2f %d\n" % (dollars[s], leaves[s]) for s in leaves)
    return 0, "%.2f\n" % sum(cost(e) for e in usage)


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
