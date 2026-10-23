"""ledger-growth.sh's check, run in-process."""
import os
import re
import sys

import tunables

try:
    from .event_log import read_events
    from .ledger import STEP_RE, is_added, read_ledger
except ImportError:
    from event_log import read_events
    from ledger import STEP_RE, is_added, read_ledger

USAGE = "usage: ledger-growth.sh <plan-ledger-file> <ledger-file>"


def step_texts(text):
    steps = []
    for line in text.split("\n"):
        match = STEP_RE.fullmatch(line)
        if match:
            steps.append((match.group(4) or "").split(" ⟂ ", 1)[0])
    return steps


def recorded_steps(ledger):
    log = os.path.join(os.path.dirname(ledger), "events.jsonl")
    try:
        events = read_events(log, skip_unreadable=True)
    except OSError:
        return []
    return [step for event in events
            if event.get("event") == "step-added" and event.get("actor") == "add-ledger-step"
            and isinstance(event.get("step"), str)
            for step in step_texts(event["step"])]


def main(argv):
    if len(argv) != 2 or not argv[0] or not argv[1]:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        planned = set(step_texts(read_ledger(argv[0])))
        steps = step_texts(read_ledger(argv[1]))
    except OSError as error:
        print(f"ledger-growth.sh: {error.filename}: {error.strerror}", file=sys.stderr)
        return 2
    budget = tunables.read("VERI_STEP_GROWTH", "5")
    if not re.fullmatch("[0-9]+", budget):
        print(f"ledger-growth.sh: VERI_STEP_GROWTH must be a whole number >= 0: {budget}", file=sys.stderr)
        return 2
    recorded = recorded_steps(argv[1])
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
