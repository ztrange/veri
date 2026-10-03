"""render-leaf-log.sh's rendering of a leaf's stream-json log, run in-process."""
import json
import sys


def main(argv):
    for line in sys.stdin:
        try:
            json.loads(line)
        except ValueError:
            return 2
    return 0
