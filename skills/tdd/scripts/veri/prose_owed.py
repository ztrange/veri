"""prose-owed.sh's entry point, run in-process."""
import glob
import os
import sys

import grade_prose
import requirements

USAGE = "usage: prose-owed.sh <repo-root>"


def graded_signature(unit):
    graded = os.path.join(os.path.dirname(unit.partition("#")[0]), "GRADED")
    if not os.path.exists(graded):
        return None
    with open(graded, encoding="utf-8") as f:
        for line in f.read().splitlines():
            fields = line.split(" ")
            if fields[0] == unit and len(fields) > 1:
                return fields[1]
    return None


def orphans(units):
    for graded in sorted(glob.glob("skills/*/GRADED")):
        with open(graded, encoding="utf-8") as f:
            for line in f.read().splitlines():
                unit = line.split(" ")[0]
                if unit not in units:
                    yield unit


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    os.chdir(argv[0])
    path = "REQUIREMENTS.md"
    units = requirements.units(path) if os.path.exists(path) else []
    owed = [u for u in units if graded_signature(u) != grade_prose.signature(path, u)]
    gone = list(orphans(units))
    for unit in owed:
        print(unit)
    for unit in gone:
        print(unit, "(orphan)")
    return 1 if owed or gone else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
