"""step-cost.sh's computation: what one step of the run has spent on leaves, read off the
run's `usage` events.

The figure is leaf spend only. The conductor's own spending is in no `usage` event, so it is
in no figure this prints — never quote one as "what this step cost" in full.
"""
import sys

USAGE = "usage: step-cost.sh <step-text> | --run | --steps"


def refuse(message):
    sys.stderr.write("%s\n%s\n" % (message, USAGE))
    return 2


def main(argv):
    if len(argv) != 1:
        return refuse("step-cost.sh: expected exactly one argument, got %d" % len(argv))
    step = argv[0]
    if step.startswith("-"):
        return refuse("step-cost.sh: unknown option '%s'" % step)
