"""verify.sh's logic, run in-process."""
import os
import sys

from run_verdict import takes_a_value

USAGE = ("usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file>"
         " <test-path> [<target-test-id>]")


def _write(stream, line):
    stream.flush()
    stream.buffer.write(os.fsencode(line + "\n"))
    stream.buffer.flush()


def main(argv):
    args = list(argv)
    while args and takes_a_value(args[0]):
        args = args[2:]
    if len(args) < 3:
        _write(sys.stderr, USAGE)
        return 2
    return 0
