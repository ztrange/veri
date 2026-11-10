"""requirements-preflight.sh's check of an issue's requirements rows, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry

USAGE = "usage: requirements-preflight.sh <issue-body-file> [<ledger>]\n"


def main(argv):
    if not argv:
        sys.stderr.write(USAGE)
        return 2
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
