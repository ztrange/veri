"""lib/ledger.sh's ledger_steps, run in-process."""
import re

PENDING_MARK = " ⟂ refactor pending"
ADDED_MARK = "⟦added⟧"
STEP_RE = re.compile(r"(\s*-\s)\[([ xX])\]( (.*))?")
CRITERION_RE = r"⟦criterion ([0-9]+)⟧"
KIND_RE = re.compile(r"⟦(full-suite|human-owed)⟧ " + CRITERION_RE)


def ledger_steps(text):
    """One (index, state, kind, pending, added, criterion, text) record per step line."""
    records = []
    for line in text.split("\n"):
        match = STEP_RE.fullmatch(line)
        if not match:
            continue
        state = "open" if match.group(2) == " " else "done"
        step = match.group(4) or ""
        kind = KIND_RE.search(step)
        criterion = re.search(CRITERION_RE, step)
        pending = state == "done" and step.endswith(PENDING_MARK)
        if pending:
            step = step[: -len(PENDING_MARK)]
        records.append((
            str(len(records) + 1),
            state,
            kind.group(1) if kind else "step",
            "1" if pending else "0",
            "1" if ADDED_MARK in step else "0",
            criterion.group(1) if criterion else "",
            step,
        ))
    return records
