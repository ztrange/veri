"""prose-owed.sh's entry point, run in-process."""
import glob
import os
import sys

import grade_prose
import requirements

USAGE = "usage: prose-owed.sh <repo-root>"


def graded_lines(graded):
    if not os.path.exists(graded):
        return
    with open(graded, encoding="utf-8") as f:
        for line in f.read().splitlines():
            yield line.split(" ")


def graded_signature(unit):
    graded = os.path.join(os.path.dirname(unit.partition("#")[0]), "GRADED")
    for fields in graded_lines(graded):
        if fields[0] == unit and len(fields) > 1:
            return fields[1]
    return None


def orphans(units):
    for graded in sorted(glob.glob("skills/*/GRADED")):
        for fields in graded_lines(graded):
            if fields[0] not in units:
                yield fields[0]


def owed_and_gone(path="REQUIREMENTS.md"):
    units = requirements.units(path) if os.path.exists(path) else []
    owed = [u for u in units if graded_signature(u) != grade_prose.signature(path, u)]
    return owed, list(orphans(units))


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    os.chdir(argv[0])
    owed, gone = owed_and_gone()
    for unit in owed:
        print(unit)
    for unit in gone:
        print(unit, "(orphan)")
    return 1 if owed or gone else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
