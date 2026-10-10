"""lib/ledger.sh's ledger_steps and ledger_tick, run in-process."""
import re
import sys

OPEN_STEP = "- [ ]"
PENDING_MARK = " ⟂ refactor pending"
ADDED_MARK = "⟦added⟧"
CRITERION_TAG = "⟦criterion "
SPACE = r"[ \t\n\v\f\r]"
STEP_RE = re.compile(rf"({SPACE}*-{SPACE})\[([ xX])\]( (.*))?")
CRITERION_RE = CRITERION_TAG + "([0-9]+)⟧"
KIND_RE = re.compile(r"⟦(full-suite|human-owed|diff-checked)⟧ " + CRITERION_RE)
PHASES_RE = re.compile(r"⟦phases: ([^⟧]*)⟧")


def decode_ledger(data):
    """data with every NUL dropped, decoded as UTF-8 with surrogateescape."""
    return data.replace(b"\0", b"").decode(errors="surrogateescape")


def read_ledger_stdin():
    """decode_ledger over all of stdin's bytes."""
    return decode_ledger(sys.stdin.buffer.read())


def handed_out(record):
    """True when record is an open step or diff-checked step."""
    return record[1] == "open" and record[2] in ("step", "diff-checked")


def is_added(step):
    """True when the added marker ends the text, the pending mark and one criterion marker cut."""
    untagged = step.removesuffix(PENDING_MARK)
    tag = untagged.rfind(" " + CRITERION_TAG)
    if tag != -1 and untagged.endswith("⟧"):
        untagged = untagged[:tag]
    return untagged.endswith(" " + ADDED_MARK)


def phase_mark(phase):
    """The mark a phase's commit appends to its step."""
    return f" ⟂ {phase} done"


def listed_phases(step):
    """The phases step lists, in order; [] for a step that lists none."""
    listed = PHASES_RE.search(step)
    return [phase.strip() for phase in listed.group(1).split(",")] if listed else []


def next_phase(step):
    """The first phase step lists and has not marked done, or None."""
    return next((phase for phase in listed_phases(step) if phase_mark(phase) not in step), None)


def new_step(text, criterion):
    """lib/ledger.sh's ledger_add_step line for text and criterion."""
    return f"{OPEN_STEP} {text} {ADDED_MARK} {CRITERION_TAG}{criterion}⟧"


def ledger_steps(text):
    """One (index, state, kind, pending, added, criterion, text) record per step line."""
    records = []
    for line in text.split("\n"):
        match = STEP_RE.fullmatch(line)
        if not match:
            continue
        step = match.group(4) or ""
        phased_done = PHASES_RE.search(step) and next_phase(step) is None
        state = "open" if match.group(2) == " " and not phased_done else "done"
        kind = KIND_RE.search(step)
        criterion = re.search(CRITERION_RE, step)
        added = is_added(step)
        pending = state == "done" and step.endswith(PENDING_MARK)
        if pending:
            step = step[: -len(PENDING_MARK)]
        records.append((
            str(len(records) + 1),
            state,
            kind.group(1) if kind else "step",
            "1" if pending else "0",
            "1" if added else "0",
            criterion.group(1) if criterion else "",
            step,
        ))
    return records


def multi_tag_refusal(steps):
    """The refusal for the first of steps carrying more than one criterion tag, or ""."""
    for *_, text in steps:
        if text.count(CRITERION_TAG) > 1:
            return f"step '{text}' carries more than one criterion tag; one step serves one criterion"
    return ""


def _rewrite_first_step(text, selects, rewrite):
    """(True, text with the first step line selects accepts rewritten), or (False, text)."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        match = STEP_RE.fullmatch(line)
        if match and selects(match, line):
            lines[i] = rewrite(match, line)
            return True, "\n".join(lines)
    return False, text


def _open_holding(matcher):
    """A selector accepting an open step line that holds matcher."""
    return lambda match, line: match.group(2) == " " and matcher in line


def ledger_tick(text, matcher, pending=False):
    """(True, text with the first open step holding matcher ticked), or (False, text)."""
    return _rewrite_first_step(
        text,
        _open_holding(matcher),
        lambda match, line: f"{match.group(1)}[x]{match.group(3) or ''}{PENDING_MARK if pending else ''}",
    )


def _with_phase_mark(line, phase):
    """line with phase's mark appended; ValueError when line does not list phase or phase is not next."""
    if phase not in listed_phases(line):
        raise ValueError(f"step does not list phase '{phase}'")
    if next_phase(line) != phase:
        raise ValueError(f"phase '{phase}' is not the step's next phase")
    return line + phase_mark(phase)


def ledger_mark_phase(text, matcher, phase):
    """(True, text with the first open step holding matcher marked phase done), or (False, text).

    ValueError when that step does not list phase.
    """
    return _rewrite_first_step(
        text,
        _open_holding(matcher),
        lambda match, line: _with_phase_mark(line, phase),
    )


def ledger_clear_pending(text, matcher):
    """(True, text with the first line holding matcher cleared of the mark), or (False, text)."""
    return _rewrite_first_step(
        text,
        lambda match, line: match.group(2) != " " and line.endswith(PENDING_MARK) and matcher in line,
        lambda match, line: line.removesuffix(PENDING_MARK),
    )
