"""run-finished.sh's checks, run in-process."""
import os
import sys

from status import main_working_tree

USAGE = "usage: run-finished.sh <issue>\n"


def main(argv):
    if len(argv) != 1:
        sys.stderr.write(USAGE)
        return 2
    issue = argv[0]
    if not os.path.isdir(os.path.join(main_working_tree(), ".tdd", "wt", issue)):
        sys.stderr.write("run-finished.sh: no run for issue %s\n" % issue)
        return 2
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
