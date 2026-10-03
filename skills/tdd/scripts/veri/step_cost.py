"""step-cost.sh's computation: what one step of the run has spent on leaves, read off the
run's `usage` events.

The figure is leaf spend only. The conductor's own spending is in no `usage` event, so it is
in no figure this prints — never quote one as "what this step cost" in full.
"""
import json
import os
import re
import sys

USAGE = "usage: step-cost.sh <step-text> | --run | --steps"
LOG = ".tdd/events.jsonl"


def refuse(message):
    sys.stderr.write("%s\n%s\n" % (message, USAGE))
    return 2


def main(argv):
    if len(argv) != 1:
        return refuse("step-cost.sh: expected exactly one argument, got %d" % len(argv))
    step = argv[0]
    if step.startswith("-") and step not in ("--run", "--steps"):
        return refuse("step-cost.sh: unknown option '%s'" % step)
    return report(step)


def value(line, key):
    found = re.search(r'"%s": "((?:[^"\\]|\\.)*)"' % re.escape(key), line)
    return found.group(1) if found else ""


def number(text):
    try:
        return float(text)
    except ValueError:
        return 0.0


def report(step):
    if not os.access(LOG, os.R_OK):
        sys.stderr.write("step-cost.sh: cannot read %s in %s — run from the run's worktree\n"
                         % (LOG, os.getcwd()))
        return 2
    with open(LOG, encoding="utf-8") as log:
        lines = [line.rstrip("\n") for line in log]
    usage = [line for line in lines if value(line, "event") == "usage"]
    if step == "--steps":
        dollars, leaves = {}, {}
        for line in usage:
            s = value(line, "step")
            dollars[s] = dollars.get(s, 0.0) + number(value(line, "total_cost_usd"))
            leaves[s] = leaves.get(s, 0) + 1
        if not leaves:
            return 3
        for s in leaves:
            sys.stdout.write("%.2f %d\n" % (dollars[s], leaves[s]))
        return 0
    if step != "--run":
        escaped = json.dumps(step)[1:-1]
        usage = [line for line in usage if value(line, "step") == escaped]
    if not usage:
        return 3
    sys.stdout.write("%.2f\n" % sum(number(value(line, "total_cost_usd")) for line in usage))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
