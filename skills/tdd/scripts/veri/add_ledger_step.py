"""add-ledger-step.sh's computations, run in-process."""
import os
import re
import sys

import tunables

try:
    from .event_log import read_events
    from .ledger import ADDED_MARK, CRITERION_TAG, STEP_RE, ledger_steps, multi_tag_refusal, new_step
except ImportError:
    from event_log import read_events
    from ledger import ADDED_MARK, CRITERION_TAG, STEP_RE, ledger_steps, multi_tag_refusal, new_step

SUITE_REPAIR = "⟦suite-repair⟧"
REPAIR_MARKS = ("⟦ci-repair⟧", SUITE_REPAIR)
BYTES = "surrogateescape"
USAGE = "usage: add-ledger-step.sh [--criterion <k>] <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]  (--planned goes with --criterion <k>)"


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


def added_step(text, k, planned=False):
    head, tail = new_step(text, k).rsplit(f" {ADDED_MARK}", 1)
    step = head + ("" if is_repair(text) or planned else f" {ADDED_MARK}") + tail
    return step if k else step.removesuffix(f" {CRITERION_TAG}⟧")


def added_since_last_resume(path):
    log = os.path.join(os.path.dirname(path), "events.jsonl")
    try:
        events = read_events(log)
    except (OSError, ValueError):
        return True
    names = [event.get("event") for event in events]
    if "resume" not in names:
        return True
    return "step-added" in names[len(names) - names[::-1].index("resume"):]


def spec_path(path):
    return re.sub(r"\.md$", "", path) + "-spec.md"


def spec_criteria(path):
    spec = spec_path(path)
    try:
        with open(spec, "rb") as f:
            text = f.read().decode(errors=BYTES)
    except OSError:
        return None, set()
    section = re.search(r"^## Acceptance criteria\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    body = section.group(1) if section else ""
    boxes = [line for line in body.split("\n") if ledger_steps(line)]
    return len(boxes), {str(n) for n, line in enumerate(boxes, 1) if STEP_RE.fullmatch(line).group(2) in "xX"}


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
    criterion = None
    planned = argv[:1] == ["--planned"]
    if planned:
        argv = argv[1:]
    if argv[:1] == ["--criterion"]:
        criterion, argv = "".join(argv[1:2]), argv[2:]
    if not planned and criterion is not None and argv[:1] == ["--planned"]:
        planned, argv = True, argv[1:]
    if len(argv) < 4 or "" in argv[:3]:
        return refuse(USAGE)
    if criterion is not None and not re.fullmatch("[1-9][0-9]*", criterion):
        return refuse("add-ledger-step.sh: --criterion must be a whole number >= 1: " + criterion)
    if planned and not criterion:
        return refuse("add-ledger-step.sh: --planned requires --criterion")
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
    records = ledger_steps("\n".join(lines))
    refusal = multi_tag_refusal(records)
    if refusal:
        return refuse("add-ledger-step.sh: " + refusal)
    known, ticked = spec_criteria(path) if planned else (None, set())
    if planned and known is None:
        return refuse("add-ledger-step.sh: --planned: cannot read the spec file " + spec_path(path))
    if criterion in ticked:
        return refuse(f"add-ledger-step.sh: --planned: criterion {criterion} is already ticked in the issue body")
    if known is not None and int(criterion) > known:
        return refuse(f"add-ledger-step.sh: --planned: criterion {criterion} is not in the issue body ({known} criteria)")
    if planned and any(criterion_of(line) == criterion for line in lines if ledger_steps(line)):
        return refuse("add-ledger-step.sh: --planned: a step already serves criterion " + criterion)
    if sum(1 for line in lines if is_anchor_step(line, anchor)) != 1:
        return refuse("add-ledger-step.sh: anchor matches no single step: " + anchor)
    earlier = [line for line in lines if ledger_steps(line) and SUITE_REPAIR in line]
    if earlier and added_since_last_resume(path) and any(SUITE_REPAIR in text for text in texts):
        warn("add-ledger-step.sh: this run already inserted a suite-repair step: " + earlier[0])
        return 1
    budget = tunables.read("VERI_STEP_GROWTH", "5")
    if not re.fullmatch("[0-9]+", budget):
        return refuse("add-ledger-step.sh: VERI_STEP_GROWTH must be a whole number >= 0: " + budget)
    added = sum(record[4] == "1" for record in records)
    cap = bash_integer(budget)
    if cap is None:
        warn(f'add-ledger-step.sh: {budget}: value too great for base (error token is "{budget}")')
    elif not planned and added + sum(not is_repair(text) for text in texts) > cap:
        headings = [line for line in lines if line.startswith("## ")]
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
        steps = [added_step(text, criterion or criterion_of(line), planned) for text in texts]
        if where == "after":
            out.append(line)
        out.extend(steps)
        if where == "before":
            out.append(line)
    write_ledger(path, "wb", "".join(line + "\n" for line in out))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
