"""prose-owed.sh's entry point, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import glob
import os
import re
import sys

import event
import git
from grade_prose import listed_pairs, owed_listed
from ledger import OPEN_STEP, is_skill_edit

USAGE = "usage: prose-owed.sh <repo-root>"
PROMPTS = "skills/tdd/scripts/prompts"


def rowless():
    """Each `.md` file under the prompts directory that no tracked REQUIREMENTS.md lists as a unit (#4384)."""
    if not os.path.isdir(PROMPTS):
        return []
    units = set(listed_pairs("REQUIREMENTS.md")[1])
    paths = [PROMPTS + "/" + f for f in sorted(os.listdir(PROMPTS)) if f.endswith(".md") and f != "REQUIREMENTS.md"]
    paths = [p for p in paths if os.path.isfile(p)]
    return [p for p in paths if p not in units]


def waive(ledger, owed):
    steps = [l for l in ledger.splitlines() if l.startswith(OPEN_STEP) and is_skill_edit(l)]
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
        unrowed = rowless()
    except ValueError as e:
        print("prose-owed.sh: " + str(e), file=sys.stderr)
        return 2
    owed = waived_owed(owed)
    for _, unit in owed:
        print(unit)
    for unit in gone:
        print(unit, "(orphan)")
    for path in unrowed:
        print(path, "(no rows)")
    return 1 if owed or gone or unrowed else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
