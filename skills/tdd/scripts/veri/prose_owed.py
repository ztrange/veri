"""prose-owed.sh's entry point, run in-process."""
import os
import sys

import requirements

USAGE = "usage: prose-owed.sh <repo-root>"


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    root = argv[0]
    path = os.path.join(root, "REQUIREMENTS.md")
    if not os.path.exists(path):
        return 0
    owed = requirements.units(path)
    for unit in owed:
        print(unit)
    return 1 if owed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
