"""add-ledger-step.sh's computations, run in-process."""
import os
import sys

from .ledger import CRITERION_TAG, ledger_steps, new_step

USAGE = "usage: add-ledger-step.sh <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]"


def refuse(message):
    sys.stderr.write(message + "\n")
    return 2


def criterion_of(line):
    return line.rsplit(CRITERION_TAG, 1)[1].split("⟧", 1)[0]


def main(argv):
    if len(argv) < 4 or "" in argv[:3]:
        return refuse(USAGE)
    path, where, anchor, *texts = argv
    if where != "after":
        return refuse("add-ledger-step.sh: position must be after, before or instead-of: " + where)
    with open(path, "rb") as f:
        content = f.read().decode()
    added = sum(record[4] == "1" for record in ledger_steps(content))
    if added + len(texts) > int(os.environ.get("VERI_STEP_GROWTH", "5")):
        return 1
    out = []
    for line in content.split("\n"):
        out.append(line)
        if anchor in line and ledger_steps(line):
            out.extend(new_step(text, criterion_of(line)) for text in texts)
    with open(path, "wb") as f:
        f.write("\n".join(out).encode())
    return 0
