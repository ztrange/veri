"""discarded-exit.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry


USAGE = "usage: discarded-exit.sh"


def main(argv):
    refused = entry.no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
