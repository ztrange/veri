"""stack-land.sh's logic, run in-process: lands the stack's tested cut on the default branch (PRD 034.4a)."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry

USAGE = "usage: stack-land.sh [--now]"


def main(argv):
    if argv not in ([], ["--now"]):
        return entry.refuse(usage=USAGE)


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
