"""add-ledger-step.sh's computations, run in-process."""
import sys

from .ledger import CRITERION_TAG, new_step

USAGE = "usage: add-ledger-step.sh <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]"


def refuse():
    sys.stderr.write(USAGE + "\n")
    return 2


def criterion_of(line):
    return line.rsplit(CRITERION_TAG, 1)[1].split("⟧", 1)[0]


def main(argv):
    if len(argv) < 4 or "" in argv[:3]:
        return refuse()
    path, where, anchor, *texts = argv
    if where != "after":
        sys.stderr.write("add-ledger-step.sh: position must be after, before or instead-of: %s\n" % where)
        return 2
    with open(path, "rb") as f:
        lines = f.read().decode().split("\n")
    out = []
    for line in lines:
        out.append(line)
        if anchor in line:
            out.extend(new_step(text, criterion_of(line)) for text in texts)
    with open(path, "wb") as f:
        f.write("\n".join(out).encode())
    return 0
