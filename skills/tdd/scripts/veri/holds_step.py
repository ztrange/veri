"""holds-step.sh's gate, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import entry
import tick_ledger

USAGE = "usage: holds-step.sh <n> <step-start-sha> <id>…"


def main(argv):
    if len(argv) < 3:
        return entry.refuse(usage=USAGE)
    for case in argv[2:]:
        tick_ledger.run_case(case)
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
