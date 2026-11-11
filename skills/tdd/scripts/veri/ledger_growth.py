"""ledger-growth.sh's check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import os
import re
import subprocess
import sys

import tunables

try:
    from .event_log import read_events
    from .add_ledger_step import added_file
    from .ledger import ADDED_MARK, CRITERION_TAG, STEP_RE, is_added, read_ledger, replace_ledger
except ImportError:
    from event_log import read_events
    from add_ledger_step import added_file
    from ledger import ADDED_MARK, CRITERION_TAG, STEP_RE, is_added, read_ledger, replace_ledger

USAGE = "usage: ledger-growth.sh <plan-ledger-file> <ledger-file> | plan-sha"


def step_texts(text):
    steps = []
    for line in text.split("\n"):
        match = STEP_RE.fullmatch(line)
        if match:
            steps.append((match.group(4) or "").split(" ⟂ ", 1)[0])
    return steps


def added_steps(ledger):
    try:
        with open(added_file(ledger), "rb") as f:
            return step_texts(f.read().decode(errors="surrogateescape"))
    except FileNotFoundError:
        return []


def recorded_steps(ledger):
    log = os.path.join(os.path.dirname(ledger), "events.jsonl")
    try:
        events = read_events(log, skip_unreadable=True)
    except FileNotFoundError:
        return added_steps(ledger)
    return added_steps(ledger) + [step for event in events
            if event.get("event") == "step-added" and event.get("actor") == "add-ledger-step"
            and isinstance(event.get("step"), str)
            for step in step_texts(event["step"])]


PLAN_BASELINE_RE = re.compile(r"[0-9a-f]+ plan: (scope|rewrite)\b")


def plan_sha(log):
    for line in log.split("\n"):
        if PLAN_BASELINE_RE.match(line):
            return line.split(" ", 1)[0]
    return None


def git_out(directory, *args):
    return subprocess.run(["git", "-C", directory, *args], check=True, stdout=subprocess.PIPE,
                          text=True, errors="surrogateescape").stdout


def record_lines(steps):
    return "".join(f"- [ ] {step}\n" for step in steps).encode(errors="surrogateescape")


def record_existing(ledger):
    added = added_file(ledger)
    if os.path.exists(added):
        print(f"ledger-growth.sh: {os.path.basename(added)} already exists", file=sys.stderr)
        return 2
    directory = os.path.dirname(os.path.abspath(ledger))
    try:
        sha = plan_sha(git_out(directory, "log", "--format=%H %s"))
        if sha is None:
            print("ledger-growth.sh: no plan commit in the ledger's history", file=sys.stderr)
            return 2
        planned = set(step_texts(git_out(directory, "show", f"{sha}:./{os.path.basename(ledger)}")))
        steps = step_texts(read_ledger(ledger))
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"ledger-growth.sh: cannot read {ledger}: {error}", file=sys.stderr)
        return 2
    with open(added, "wb") as f:
        f.write(record_lines(step for step in steps if step not in planned))
    return 0


def record_rewrite(pre, ledger):
    try:
        before = set(step_texts(read_ledger(pre)))
        steps = step_texts(read_ledger(ledger))
        recorded = set(recorded_steps(ledger))
        with open(added_file(ledger), "ab") as f:
            f.write(record_lines(step for step in steps if step not in before
                                 and step not in recorded))
    except OSError as error:
        return unreadable(error)
    return 0


def reopen(ledger, needle, change):
    try:
        lines = read_ledger(ledger).split("\n")
    except OSError as error:
        return unreadable(error)
    for i, line in enumerate(lines):
        match = STEP_RE.fullmatch(line)
        if not match or needle not in line:
            continue
        body = match.group(4).split(" ⟂ ", 1)[0]
        if "⟦skill-edit⟧" not in body:
            print(f"ledger-growth.sh: not a skill-edit step: {body}", file=sys.stderr)
            return 2
        head, tag, k = body.rpartition(" " + CRITERION_TAG)
        head = head.removesuffix(" " + ADDED_MARK)
        step = f"{head} change: {change} {ADDED_MARK}{tag}{k}"
        lines[i] = f"- [ ] {step}"
        replace_ledger(ledger, "\n".join(lines))
        with open(added_file(ledger), "ab") as f:
            f.write(record_lines([step]))
        return 0


def unreadable(error):
    print(f"ledger-growth.sh: {error.filename}: {error.strerror}", file=sys.stderr)
    return 2


def main(argv):
    if len(argv) == 2 and argv[0] == "record-existing":
        return record_existing(argv[1])
    if len(argv) == 3 and argv[0] == "record-rewrite":
        return record_rewrite(argv[1], argv[2])
    if len(argv) == 4 and argv[0] == "reopen":
        return reopen(*argv[1:])
    if argv == ["plan-sha"]:
        sha = plan_sha(sys.stdin.read())
        if sha is None:
            print("ledger-growth.sh: no plan commit in the log", file=sys.stderr)
            return 2
        print(sha)
        return 0
    if len(argv) != 2 or not argv[0] or not argv[1]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        planned = set(step_texts(read_ledger(argv[0])))
        steps = step_texts(read_ledger(argv[1]))
    except OSError as error:
        return unreadable(error)
    budget = tunables.read("VERI_STEP_GROWTH", "5")
    if not re.fullmatch("[0-9]+", budget):
        print(f"ledger-growth.sh: VERI_STEP_GROWTH must be a whole number >= 0: {budget}", file=sys.stderr)
        return 2
    try:
        recorded = recorded_steps(argv[1])
    except OSError as error:
        return unreadable(error)
    unrecorded_new = [step for step in steps if step not in planned
                      and step not in recorded]
    off = [step for step in unrecorded_new if not is_added(step)]
    for step in off:
        print(f"ledger-growth.sh: step added without ⟦added⟧: {step}", file=sys.stderr)
    unrecorded = [step for step in unrecorded_new if is_added(step)]
    for step in unrecorded:
        print(f"ledger-growth.sh: step added without an add-ledger-step.sh record: {step}", file=sys.stderr)
    over = sum(is_added(step) for step in steps) > int(budget)
    if over:
        print(f"ledger-growth.sh: more than {budget} ⟦added⟧ steps (VERI_STEP_GROWTH)", file=sys.stderr)
    return 1 if off or unrecorded or over else 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
