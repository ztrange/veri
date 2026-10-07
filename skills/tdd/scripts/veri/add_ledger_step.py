"""add-ledger-step.sh's computations, run in-process."""
import os
import re
import sys

try:
    from .ledger import ADDED_MARK, CRITERION_TAG, ledger_steps, new_step
except ImportError:
    from ledger import ADDED_MARK, CRITERION_TAG, ledger_steps, new_step

REPAIR_MARKS = ("⟦ci-repair⟧", "⟦suite-repair⟧")
BYTES = "surrogateescape"
USAGE = "usage: add-ledger-step.sh <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]"


def warn(message):
    sys.stderr.write(message + "\n")


def refuse(message):
    warn(message)
    return 2


def criterion_of(line):
    if CRITERION_TAG not in line:
        return ""
    return line.rsplit(CRITERION_TAG, 1)[1].split("⟧", 1)[0]


def is_repair(text):
    return any(mark in text for mark in REPAIR_MARKS)


def added_step(text, k):
    head, tail = new_step(text, k).rsplit(f" {ADDED_MARK}", 1)
    step = head + ("" if is_repair(text) else f" {ADDED_MARK}") + tail
    return step if k else step.removesuffix(f" {CRITERION_TAG}⟧")


def bash_integer(value):
    try:
        n = int(value, 8 if value.startswith("0") else 10)
    except ValueError:
        return None
    n %= 2**64
    return n - 2**64 if n >= 2**63 else n


def is_anchor_step(line, anchor):
    return anchor in line and ledger_steps(line)


def write_ledger(path, mode, text):
    with open(path, mode) as f:
        f.write(text.encode(errors=BYTES))


def main(argv):
    if len(argv) < 4 or "" in argv[:3]:
        return refuse(USAGE)
    path, where, anchor, *texts = argv
    if where not in ("after", "before", "instead-of"):
        return refuse("add-ledger-step.sh: position must be after, before or instead-of: " + where)
    try:
        with open(path, "rb") as f:
            lines = f.read().decode(errors=BYTES).split("\n")
    except OSError as error:
        warn(f"add-ledger-step.sh: {path}: {error.strerror}")
        lines = [""]
    terminated = lines[:-1]
    if lines[-1] == "":
        lines = terminated
    if sum(1 for line in lines if is_anchor_step(line, anchor)) != 1:
        return refuse("add-ledger-step.sh: anchor matches no single step: " + anchor)
    budget = os.environ.get("VERI_STEP_GROWTH", "5")
    if not re.fullmatch("[0-9]+", budget):
        return refuse("add-ledger-step.sh: VERI_STEP_GROWTH must be a whole number >= 0: " + budget)
    added = sum(record[4] == "1" for record in ledger_steps("\n".join(lines)))
    cap = bash_integer(budget)
    if cap is None:
        warn(f'add-ledger-step.sh: {budget}: value too great for base (error token is "{budget}")')
    elif added + sum(not is_repair(text) for text in texts) > cap:
        headings = [line for line in terminated if line.startswith("## ")]
        owed = "" if headings[-1:] == ["## Owed steps"] else "\n## Owed steps\n\n"
        if not owed and lines is not terminated:
            owed = "\n"
        owed += "".join(f"- {text}\n" for text in texts)
        write_ledger(path, "ab", owed)
        return 1
    out = []
    for line in lines:
        if not is_anchor_step(line, anchor):
            out.append(line)
            continue
        steps = [added_step(text, criterion_of(line)) for text in texts]
        if where == "after":
            out.append(line)
        out.extend(steps)
        if where == "before":
            out.append(line)
    write_ledger(path, "wb", "".join(line + "\n" for line in out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
