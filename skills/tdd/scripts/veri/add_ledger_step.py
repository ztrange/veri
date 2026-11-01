"""add-ledger-step.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import sys
import time

import event
import replaces_case
import requirements
import skill_edit_guard
import tunables

try:
    from .event_log import read_events
    from .ledger import ADDED_MARK, CRITERION_TAG, STEP_RE, carries_mark, ledger_steps, read_ledger, replace_ledger, multi_tag_refusal, new_step, trailing_markers
except ImportError:
    from event_log import read_events
    from ledger import ADDED_MARK, CRITERION_TAG, STEP_RE, carries_mark, ledger_steps, read_ledger, replace_ledger, multi_tag_refusal, new_step, trailing_markers

SUITE_REPAIR = "suite-repair"
REPAIR_MARKS = ("ci-repair", SUITE_REPAIR)
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


def has_mark(text, marks):
    markers = trailing_markers(text)
    return any(carries_mark(markers, mark) for mark in marks)


def is_repair(text):
    return has_mark(text, REPAIR_MARKS)


def is_suite_repair(text):
    return has_mark(text, (SUITE_REPAIR,))


def added_step(text, k, planned=False):
    head, tail = new_step(text, k).rsplit(f" {ADDED_MARK}", 1)
    step = head + ("" if is_repair(text) or planned else f" {ADDED_MARK}") + tail
    return step if k else step.removesuffix(f" {CRITERION_TAG}⟧")


def repair_following(steps, anchor):
    return next((following for line, following in zip(steps, steps[1:]) if anchor in line and is_suite_repair(following)), None)


class UnreadableLog(Exception):
    pass


def events_log(path):
    return os.path.join(os.path.dirname(path), "events.jsonl")


def added_since_last_resume(path, steps):
    log = events_log(path)
    try:
        events = read_events(log)
    except OSError:
        return True
    except ValueError as error:
        raise UnreadableLog(f"add-ledger-step.sh: cannot read {log}, line: {error.line}")
    names = [event.get("event") for event in events]
    if "resume" not in names:
        return True
    after = events[len(names) - names[::-1].index("resume"):]
    found = (
        repair_following(steps, str(event.get("anchor") or "\n"))
        for event in after
        if event.get("event") == "step-added"
    )
    return next((line for line in found if line), False)


def sibling(path, suffix):
    return re.sub(r"\.md$", "", path) + suffix


def spec_path(path):
    return sibling(path, "-spec.md")


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


def unit_of(text):
    found = re.search(r"`([^`]+)`", text)
    return found.group(1) if found else None


def restates_list(path, unit):
    lines = requirements.read_lines(spec_path(path))
    rows = [requirements.table_cells(line)[:2] for heading, line in requirements.requirements_lines(lines)
            if heading == unit and line.startswith("|")][2:]
    current = requirements.claims(skill_edit_guard.list_path(unit), unit)
    return sorted(current.splitlines()) == sorted("\t".join(row) for row in rows)


def bash_integer(value):
    try:
        n = int(value, 8 if value.startswith("0") else 10)
    except ValueError:
        return None
    n %= 2**64
    return n - 2**64 if n >= 2**63 else n


def is_anchor_step(line, anchor):
    return anchor in line and ledger_steps(line)


def write_ledger(path, text, appended=""):
    open(path, "ab").close()
    replace_ledger(path, (text + appended).encode(errors=BYTES))


def added_file(path):
    return sibling(path, "-added.md")


def record_insertions(path, steps, awake):
    with open(added_file(path), "ab") as f:
        f.write("".join(step + "\n" for step in steps).encode(errors=BYTES))
    with open(events_log(path), "ab") as f:
        for step in steps:
            context = {b"actor": b"add-ledger-step", b"step": step.encode(errors=BYTES)}
            f.write(event.line([b"step-added"], context, int(time.time()), awake))


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
    for text in texts:
        if CRITERION_TAG in text:
            return refuse("add-ledger-step.sh: the text already holds a criterion tag: " + text)
    try:
        lines = read_ledger(path).split("\n")
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
    for text in texts:
        if has_mark(text, ("replaces-case",)) and replaces_case.parse(text) is None:
            warn("add-ledger-step.sh: cannot read the case names of step: " + text.replace("\n", " "))
            return 1
    for text in texts:
        unit = unit_of(text)
        if carries_mark(text, "skill-edit") and restates_list(path, unit):
            return refuse(f"add-ledger-step.sh: {unit}: the issue's Requirements restate no row that differs from the unit's list; a requirements row is needed")
    steps = [line for line in lines if ledger_steps(line)]
    earlier = [line for line in steps if is_suite_repair(line)]
    try:
        this_run = added_since_last_resume(path, steps) if earlier else False
    except UnreadableLog as unreadable:
        return refuse(str(unreadable))
    if this_run and any(is_suite_repair(text) for text in texts):
        warn("add-ledger-step.sh: this run already inserted a suite-repair step: " + (earlier[0] if this_run is True else this_run))
        return 1
    budget = tunables.read("VERI_STEP_GROWTH", "5")
    if not re.fullmatch("[0-9]+", budget):
        return refuse("add-ledger-step.sh: VERI_STEP_GROWTH must be a whole number >= 0: " + budget)
    out = []
    inserted_lines = []
    for line in lines:
        if not is_anchor_step(line, anchor):
            out.append(line)
            continue
        inserted = [added_step(text, criterion or criterion_of(line), planned) for text in texts]
        if where == "after":
            out.append(line)
        out.extend(inserted)
        inserted_lines.extend(inserted)
        if where == "before":
            out.append(line)
    kept = [line for line in lines if where != "instead-of" or not is_anchor_step(line, anchor)]
    added = sum(record[4] == "1" for record in ledger_steps("\n".join(kept))) + sum(not is_repair(text) for text in texts)
    cap = bash_integer(budget)
    if cap is None:
        warn(f'add-ledger-step.sh: {budget}: value too great for base (error token is "{budget}")')
    elif not planned and added > cap:
        headings = [line for line in lines if line.startswith("## ")]
        owed = "" if headings[-1:] == ["## Owed steps"] else "\n## Owed steps\n\n"
        if not owed and lines is not terminated:
            owed = "\n"
        owed += "".join(f"- {text}\n" for text in texts)
        write_ledger(path, read_ledger(path), owed)
        return 1
    awake = event.awake_reading()
    if isinstance(awake, int):
        return 2
    grown = "".join(line + "\n" for line in out)
    write_ledger(path, grown)
    record_insertions(path, inserted_lines, awake)
    issue = re.fullmatch(r"issue-(\d+)\.md", os.path.basename(path))
    if issue:
        tdd = os.path.dirname(os.path.abspath(path))
        event.mark(os.path.dirname(tdd), event.context(tunables.with_values(VERI_ISSUE=issue.group(1))),
                   "plan", ["steps=%d" % len(ledger_steps(grown))])
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
