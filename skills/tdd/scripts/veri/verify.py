"""verify.sh's logic, run in-process."""
import sys

from leaf_role import _write
from run_verdict import takes_a_value

USAGE = ("usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file>"
         " <test-path> [<target-test-id>]")


def main(argv):
    args = list(argv)
    while args and takes_a_value(args[0]):
        args = args[2:]
    if len(args) < 3:
        _write(sys.stderr, USAGE)
        return 2
    return 0
