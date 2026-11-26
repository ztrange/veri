"""add-ledger-step.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys
import time

import entry
import event
import issue_body
import ledger_growth
import pid_file
import replaces_case
import requirements
import tunables
from event_log import read_events
from git import git
from ledger import (
    ADDED_MARK,
    CRITERION_TAG,
    STEP_RE,
    added_file,
    carries_mark,
    has_kind,
    is_retired,
    is_skill_edit,
    ledger_steps,
    multi_tag_refusal,
    new_step,
    read_ledger,
    replace_ledger,
    same_step,
    trailing_markers,
    unit_of,
)
from ledger import body as step_body

SUITE_REPAIR = "suite-repair"
REPAIR_MARKS = ("ci-repair", SUITE_REPAIR, "branch-repair")
# The marks of which one run inserts at most one step: the second is refused (exit 1). Not REPAIR_MARKS, which only exempts.
ONE_PER_RUN = (SUITE_REPAIR, "lint-repair")
BYTES = "surrogateescape"
USAGE = "usage: add-ledger-step.sh [--planned] [--criterion <k>] <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]  (--planned goes with --criterion <k>)"


def warn(message):
    sys.stderr.write(message + "\n")


def criterion_of(line):
    if CRITERION_TAG not in line:
        return ""
    return line.rsplit(CRITERION_TAG, 1)[1].split("⟧", 1)[0]


def has_mark(text, marks):
    markers = trailing_markers(text)
    return any(carries_mark(markers, mark) for mark in marks)


def is_repair(text):
    return has_mark(text, REPAIR_MARKS)


def is_one_per_run(text, mark):
    return has_mark(text, (mark,))


def added_step(text, k, planned=False):
    head, tail = new_step(text, k).rsplit(f" {ADDED_MARK}", 1)
    step = head + ("" if is_repair(text) or planned else f" {ADDED_MARK}") + tail
    return step if k else step.removesuffix(f" {CRITERION_TAG}⟧")


def repair_following(steps, anchor, mark):
    return next((following for line, following in zip(steps, steps[1:], strict=False) if anchor in line and is_one_per_run(following, mark)), None)


class UnreadableLog(Exception):
    pass


def events_log(path):
    return os.path.join(os.path.dirname(path), "events.jsonl")


def added_since_last_resume(path, steps, mark):
    log = events_log(path)
    try:
        events = read_events(log)
    except OSError:
        return True
    except ValueError as error:
        raise UnreadableLog(f"add-ledger-step.sh: cannot read {log}, line: {error.line}") from error
    names = [event.get("event") for event in events]
    if "resume" not in names:
        return True
    after = events[len(names) - names[::-1].index("resume"):]
    found = (
        repair_following(steps, str(event.get("anchor") or "\n"), mark)
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
    boxes = issue_body.criteria(text)
    return len(boxes), {str(n) for n, (_, line) in enumerate(boxes, 1) if STEP_RE.fullmatch(line).group(2) in "xX"}


class MissingUnit(Exception):
    pass


def restates_list(path, unit):
    try:
        lines = requirements.read_lines(spec_path(path))
    except FileNotFoundError:
        return False
    rows = [requirements.table_cells(line)[:2] for heading, line in requirements.requirements_lines(lines)
            if heading == unit and line.startswith("|")][2:]
    try:
        current = requirements.claims(requirements.list_path(unit), unit)
    except FileNotFoundError as error:
        raise MissingUnit(unit) from error
    return sorted(current.splitlines()) == sorted("\t".join(row) for row in rows)


def verified_plan_size(path):
    """The steps the ledger at `path` held at the commit `ledger-growth.sh plan-sha` prints; None when git names none."""
    directory = os.path.dirname(os.path.abspath(path))
    log = git("log", "--format=%H %s", cwd=directory, capture_output=True, text=True, errors=BYTES)
    sha = ledger_growth.plan_sha(log.stdout) if log.returncode == 0 else None
    if sha is None:
        return None
    shown = git("show", f"{sha}:./{os.path.basename(path)}", cwd=directory, capture_output=True)
    if shown.returncode != 0:
        return None
    return len(ledger_growth.step_texts(shown.stdout.decode(errors=BYTES)))


def is_anchor_step(line, anchor):
    return anchor in line and ledger_steps(line)


def write_ledger(path, text, appended=""):
    open(path, "ab").close()
    replace_ledger(path, (text + appended).encode(errors=BYTES))


def record_insertions(path, steps, awake):
    with open(added_file(path), "ab") as f:
        f.write("".join(step + "\n" for step in steps).encode(errors=BYTES))
    with open(events_log(path), "ab") as f:
        for step in steps:
            context = {b"actor": b"add-ledger-step", b"step": step.encode(errors=BYTES)}
            f.write(event.line([b"step-added"], context, int(time.time()), awake))


NOT_DURABLE = "add-ledger-step.sh: the added step is not durable (uncommitted, so a bail's revert would drop it until someone commits it)"


def commit_amendment(path):
    tree = os.path.dirname(os.path.dirname(os.path.abspath(path)))
    live = pid_file.recorded_started(tree)
    if live is None or int(live) in pid_file.ancestors():
        print(NOT_DURABLE, file=sys.stderr)
        return
    paths = [os.path.abspath(path), os.path.abspath(added_file(path))]
    for argv in (["add", "--", *paths],
                 ["commit", "-q", "-m", "plan: step added while the conductor is live", "--", *paths]):
        done = subprocess.run(["git", *argv], cwd=tree, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if done.returncode == 0:
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=tree, capture_output=True, text=True).stdout.strip()
        print(f"add-ledger-step.sh: the added step is durable (committed in {head})", file=sys.stderr)
    else:
        print(NOT_DURABLE, file=sys.stderr)


def drop_replaced_records(tdd, n, replaced, was_open):
    """Remove each `<stage>-rejected` wait record under <tdd> naming the <replaced> step and, when it <was_open> (the
    exit files are the open step's), each `verdict-<phase>.exit` (#4547): ledger.same_step drops ⟦added⟧, and an exit
    file names no step, so the step put in its place would read either as its own verdict."""
    import glob
    import json
    for path in glob.glob(os.path.join(tdd, "issue-%s-*-rejected-wait" % n)):
        try:
            with open(path) as f:
                theirs = json.load(f).get("step")
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(theirs, str) and same_step(theirs, replaced):
            os.remove(path)
    for path in glob.glob(os.path.join(tdd, "verdict-*.exit")) if was_open else ():
        os.remove(path)


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
        return entry.refuse(USAGE)
    if criterion is not None and not re.fullmatch("[1-9][0-9]*", criterion):
        return entry.refuse("add-ledger-step.sh: --criterion must be a whole number >= 1: " + criterion)
    if planned and not criterion:
        return entry.refuse("add-ledger-step.sh: --planned requires --criterion")
    path, where, anchor, *texts = argv
    return add(path, where, anchor, texts, criterion=criterion, planned=planned)


def add(path, where, anchor, texts, *, criterion=None, planned=False):
    """Insert each of `texts` as a ledger step `where` ("after", "before" or "instead-of") the one step of the
    ledger at `path` whose line holds `anchor`: what `add-ledger-step.sh` does once its arguments are parsed.

    `criterion` is the criterion number as a string (None: each step inherits the anchor's); `planned` (needs a
    criterion) inserts steps the spec already lists, outside the VERI_STEP_GROWTH_PERCENT budget.
    Returns 0 inserted; 1 clean negative (growth budget spent, the texts parked under "## Owed steps"; an
    unreadable replaces-case step; a second suite-repair or lint-repair step this run); 2 refused (stderr says why) or no answer.
    Writes the ledger, its added-steps record and events.jsonl (step-added, plan); commits the amendment when a
    conductor is live. Prints refusals and notes to stderr, as the script does; an empty path, position or anchor
    is refused with the usage line (exit 2), as on the command line.
    """
    if "" in (path, where, anchor):
        return entry.refuse(USAGE)
    if where not in ("after", "before", "instead-of"):
        return entry.refuse("add-ledger-step.sh: position must be after, before or instead-of: " + where)
    for text in texts:
        if CRITERION_TAG in text:
            return entry.refuse("add-ledger-step.sh: the text already holds a criterion tag: " + text)
        if step_body(text) != text:
            return entry.refuse("add-ledger-step.sh: the text holds the refactor-pending delimiter ' ⟂ ': " + text)
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
        return entry.refuse("add-ledger-step.sh: " + refusal)
    known, ticked = spec_criteria(path) if planned else (None, set())
    if planned and known is None:
        return entry.refuse("add-ledger-step.sh: --planned: cannot read the spec file " + spec_path(path))
    if criterion in ticked:
        return entry.refuse(f"add-ledger-step.sh: --planned: criterion {criterion} is already ticked in the issue body")
    if known is not None and int(criterion) > known:
        return entry.refuse(f"add-ledger-step.sh: --planned: criterion {criterion} is not in the issue body ({known} criteria)")
    if planned and any(criterion_of(line) == criterion for line in lines if ledger_steps(line)):
        return entry.refuse("add-ledger-step.sh: --planned: a step already serves criterion " + criterion)
    if sum(1 for line in lines if is_anchor_step(line, anchor)) != 1:
        return entry.refuse("add-ledger-step.sh: anchor matches no single step: " + anchor)
    for text in texts:
        if has_mark(text, ("replaces-case",)) and replaces_case.parse(text) is None:
            warn("add-ledger-step.sh: cannot read the case names of step: " + text.replace("\n", " "))
            return 1
    for text in texts:
        if not (is_skill_edit(text.strip())):
            continue
        unit = unit_of(text)
        if unit is None and "`" in text:
            return entry.refuse("add-ledger-step.sh: no unit path was found in step: " + text.replace("\n", " "))
        if unit is None:
            return entry.refuse("add-ledger-step.sh: a skill-edit step must name its unit path in backticks: " + text.replace("\n", " "))
        try:
            restated = restates_list(path, unit)
        except MissingUnit:
            return entry.refuse(f"add-ledger-step.sh: {unit}: the unit file does not exist")
        if restated:
            return entry.refuse(f"add-ledger-step.sh: {unit}: the issue's Requirements restate no row that differs from the unit's list; a requirements row is needed")
    steps = [line for line in lines if ledger_steps(line)]
    for mark in ONE_PER_RUN:
        earlier = [line for line in steps if is_one_per_run(line, mark) and not is_retired(line)]
        try:
            this_run = added_since_last_resume(path, steps, mark) if earlier else False
        except UnreadableLog as unreadable:
            return entry.refuse(str(unreadable))
        if this_run and any(is_one_per_run(text, mark) for text in texts):
            warn(f"add-ledger-step.sh: this run already inserted a {mark} step: " + (earlier[0] if this_run is True else this_run))
            return 1
    if tunables.is_set("VERI_STEP_GROWTH"):
        return entry.refuse("add-ledger-step.sh: " + ledger_growth.RETIRED)
    percent = tunables.get("VERI_STEP_GROWTH_PERCENT")
    if not tunables.parses("VERI_STEP_GROWTH_PERCENT", percent):
        return entry.refuse("add-ledger-step.sh: VERI_STEP_GROWTH_PERCENT must be a whole number >= 0: " + percent)
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
    added = sum(record.added == "1" for record in ledger_steps("\n".join(kept))) + sum(not is_repair(text) for text in texts)
    plan_size = verified_plan_size(path) if added and not planned else 0
    if plan_size is None:
        return entry.refuse("add-ledger-step.sh: no plan commit holds " + os.path.basename(path)
                            + " (git log names no plan: scope or plan: rewrite commit that git show can read)")
    if not planned and added > ledger_growth.growth_cap(int(percent), plan_size):
        headings = [line for line in lines if line.startswith("## ")]
        owed = "" if headings[-1:] == ["## Owed steps"] else "\n## Owed steps\n\n"
        if not owed and lines is not terminated:
            owed = "\n"
        owed += "".join(f"- {text}\n" for text in texts)
        write_ledger(path, read_ledger(path), owed)
        return 1
    bare = next((line for line in inserted_lines if has_kind(line, "⟦diff-checked⟧") and CRITERION_TAG not in line), None)
    if bare:
        return entry.refuse("add-ledger-step.sh: a diff-checked step needs a ⟦criterion k⟧ tag: " + bare)
    awake = event.awake_reading()
    if isinstance(awake, int):
        return 2
    grown = "".join(line + "\n" for line in out)
    write_ledger(path, grown)
    record_insertions(path, inserted_lines, awake)
    commit_amendment(path)
    issue = re.fullmatch(r"issue-(\d+)\.md", os.path.basename(path))
    if issue:
        tdd = os.path.dirname(os.path.abspath(path))
        if where == "instead-of":
            replaced = next(line for line in lines if is_anchor_step(line, anchor))
            first_open = next((line for line in lines if any(r.state == "open" for r in ledger_steps(line))), None)
            drop_replaced_records(tdd, issue.group(1), ledger_steps(replaced)[0].text, replaced == first_open)
        event.mark(os.path.dirname(tdd), event.context(tunables.with_values(VERI_ISSUE=issue.group(1))),
                   "plan", ["steps=%d" % len(ledger_steps(grown))])
    return 0


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
