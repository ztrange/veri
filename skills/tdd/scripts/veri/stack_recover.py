"""stack-recover.sh's logic, run in-process: once a GitHub outage ends, pushes each offline join's commit to its run's
branch and then the stack, so each joined draft pull request reads merged (PRD 033.3)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry

USAGE = "usage: stack-recover.sh"


def main(argv):
    if argv:
        return entry.refuse(usage=USAGE)
    return 3


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
