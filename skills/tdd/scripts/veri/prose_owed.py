"""prose-owed.sh's entry point, run in-process."""
import glob
import os
import re
import sys

import git
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
    graded = grade_prose.graded_path(unit)
    for fields in graded_lines(graded):
        if fields[0] == unit and len(fields) > 1:
            return fields[1]
    return None


def orphans(units):
    for graded in sorted(set(glob.glob("skills/*/GRADED")) | set(glob.glob("*/GRADED"))):
        for fields in graded_lines(graded):
            if fields[0] not in units:
                yield fields[0]


def owed_listed(path="REQUIREMENTS.md"):
    paths = [p for p in [path] + sorted(set(glob.glob("*/REQUIREMENTS.md")) | set(glob.glob("skills/*/**/REQUIREMENTS.md", recursive=True))) if os.path.exists(p)]
    listed = [(p, u) for p in paths for u in requirements.listed_units(p)]
    owed = [(p, u) for p, u in listed if graded_signature(u) != grade_prose.signature(p, u)]
    return owed, list(orphans([u for _, u in listed]))


def waive(ledger, owed):
    steps = [l for l in ledger.splitlines() if l.startswith("- [ ]") and "⟦skill-edit⟧" in l]
    still, waived = [], []
    for unit in owed:
        step = next((s for s in steps if "`" + unit + "`" in s), None)
        if step is None:
            still.append(unit)
        else:
            waived.append((unit, step))
    return still, waived


def waived_owed(owed):
    if not owed or not glob.glob(".tdd/issue-*.md"):
        return owed
    ran = git.git("symbolic-ref", "--short", "HEAD", capture_output=True, text=True)
    m = re.fullmatch(r"tdd/(\d+)-.*", ran.stdout.strip()) if ran.returncode == 0 else None
    ledger = ".tdd/issue-" + m.group(1) + ".md" if m else None
    if not ledger or not os.path.exists(ledger):
        return owed
    with open(ledger, encoding="utf-8") as f:
        still, _ = waive(f.read(), [u for _, u in owed])
    return [(p, u) for p, u in owed if u in still]


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    os.chdir(argv[0])
    try:
        owed, gone = owed_listed()
    except ValueError as e:
        print("prose-owed.sh: " + str(e), file=sys.stderr)
        return 2
    owed = waived_owed(owed)
    for _, unit in owed:
        print(unit)
    for unit in gone:
        print(unit, "(orphan)")
    return 1 if owed or gone else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
