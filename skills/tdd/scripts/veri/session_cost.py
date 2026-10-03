"""session-cost.sh's computations, run in-process."""
import sys

USAGE = "usage: session-cost.sh --since <ISO date> [--json] [<transcript.jsonl> ...]"


def refuse():
    print(USAGE, file=sys.stderr)
    return 2


def main(argv):
    return refuse()
