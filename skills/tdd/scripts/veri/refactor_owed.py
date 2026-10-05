"""refactor-owed.sh's owed-file append, render and list, run in-process."""
import os
import sys

USAGE = ("refactor-owed: usage: refactor-owed.sh append <file> '<STEP>' < leaf-report.txt\n"
         "                      refactor-owed.sh render <file>\n"
         "                      refactor-owed.sh list <file>")


def refuse():
    print(USAGE, file=sys.stderr)
    return 2


def main(argv):
    verb = argv[0] if argv else ""
    file = argv[1] if len(argv) > 1 else ""
    if not verb or not file:
        return refuse()
    if verb == "append":
        return 0
    if verb in ("render", "list"):
        if not os.path.exists(file) or os.path.getsize(file) == 0:
            return 3
    return refuse()
