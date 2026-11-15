"""prose-owed.sh's entry point, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import os
import re
import sys

import event
import git
from grade_prose import owed_listed
from ledger import OPEN_STEP, carries_mark

USAGE = "usage: prose-owed.sh <repo-root>"


def waive(ledger, owed):
    steps = [l for l in ledger.splitlines() if l.startswith(OPEN_STEP) and carries_mark(l, "skill-edit")]
    still, waived = [], []
    for unit in owed:
        step = next((s for s in steps if re.search(r"(?<![\w./-])" + re.escape(unit) + r"(?![\w/-]|\.\w)", s)), None)
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
        still, waived = waive(f.read(), [u for _, u in owed])
    for unit, step in waived:
        event.append(".", {}, "prose-owed-waived", ["unit=" + unit, "step=" + step])
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
