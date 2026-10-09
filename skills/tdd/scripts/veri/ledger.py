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


def decode_ledger(data):
    """data with every NUL dropped, decoded as UTF-8 with surrogateescape."""
    return data.replace(b"\0", b"").decode(errors="surrogateescape")


def read_ledger_stdin():
    """decode_ledger over all of stdin's bytes."""
    return decode_ledger(sys.stdin.buffer.read())


def is_added(step):
    """True when the added marker ends the text, the pending mark and one criterion marker cut."""
    untagged = step.removesuffix(PENDING_MARK)
    tag = untagged.rfind(" " + CRITERION_TAG)
    if tag != -1 and untagged.endswith("⟧"):
        untagged = untagged[:tag]
    return untagged.endswith(" " + ADDED_MARK)


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
        state = "open" if match.group(2) == " " else "done"
        step = match.group(4) or ""
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


def ledger_tick(text, matcher, pending=False):
    """(True, text with the first open step holding matcher ticked), or (False, text)."""
    return _rewrite_first_step(
        text,
        lambda match, line: match.group(2) == " " and matcher in line,
        lambda match, line: f"{match.group(1)}[x]{match.group(3) or ''}{PENDING_MARK if pending else ''}",
    )


def ledger_clear_pending(text, matcher):
    """(True, text with the first line holding matcher cleared of the mark), or (False, text)."""
    return _rewrite_first_step(
        text,
        lambda match, line: match.group(2) != " " and line.endswith(PENDING_MARK) and matcher in line,
        lambda match, line: line.removesuffix(PENDING_MARK),
    )
