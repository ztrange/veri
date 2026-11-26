"""branch-suite.sh's logic, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry
import suite_mode

USAGE = "usage: branch-suite.sh"


def main(argv):
    refused = entry.no_arguments(argv, USAGE)
    if refused is not None:
        return refused
    return suite_mode.run("branch-suite.sh", "VERI_BRANCH_SUITE")


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
