"""The ledger reader and ticker, ledger_steps and ledger_tick, run in-process."""
import os
import re
import shutil
import sys
import tempfile

OPEN_STEP = "- [ ]"
TICKED_STEP = "- [x]"
PENDING_MARK = " ⟂ refactor pending"
ADDED_MARK = "⟦added⟧"
CRITERION_TAG = "⟦criterion "
SPACE = r"[ \t\n\v\f\r]"
STEP_RE = re.compile(rf"({SPACE}*-{SPACE})\[([ xX])\]( (.*))?")
CRITERION_RE = CRITERION_TAG + "([0-9]+)⟧"
KIND_RE = re.compile(r"⟦(full-suite|human-owed|diff-checked)⟧ (?:" + ADDED_MARK + " )?" + CRITERION_RE)
PHASES_RE = re.compile(r"⟦phases: ([^⟧]*)⟧")
TRAILING_RUN_RE = re.compile(r"((?:(?:^| |(?<=⟧))⟦[^⟦⟧]*⟧)+)(?: ⟂ [^⟦⟧⟂]*)*$")


def ledger_path(run_dir, issue):
    return os.path.join(run_dir, ".tdd", f"issue-{issue}.md")


class LeftBehind(OSError):
    """A failed replace_ledger whose temp file, its filename, could not be removed."""


def replace_ledger(path, data):
    """Write data to a temp file beside path's real file and swap it in; OSError on failure."""
    path = os.path.realpath(path)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "wb" if isinstance(data, bytes) else "w") as file:
            file.write(data)
        shutil.copymode(path, tmp)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            raise LeftBehind(None, None, tmp) from None
        raise


def rewrite_ledger(path, text):
    """replace_ledger with text newline-terminated; None on success, else the temp file left behind ('' if none)."""
    try:
        replace_ledger(path, (text.rstrip("\n") + "\n").encode(errors="surrogateescape"))
    except LeftBehind as error:
        return error.filename
    except OSError:
        return ""
    return None


def decode_ledger(data):
    """data with every NUL dropped, decoded as UTF-8 with surrogateescape."""
    return data.replace(b"\0", b"").decode(errors="surrogateescape")


def read_ledger(path):
    """decode_ledger over all of path's bytes; OSError when it cannot be read."""
    with open(path, "rb") as file:
        return decode_ledger(file.read())


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


def mark(phase, state):
    """The mark a phase appends to its step: state is "done" for its commit, "owed" for a contract filed as owed."""
    return f" ⟂ {phase} {state}"


def trailing_markers(step):
    """The run of ⟦…⟧ markers ending step's text, before any ⟂ marks; "" for none."""
    run = TRAILING_RUN_RE.search(step)
    return run.group(1) if run else ""


def carries_mark(text, name):
    """True when ⟦name⟧ occurs anywhere in text."""
    return f"⟦{name}⟧" in text


def is_human_owed(step):
    step = step.strip()
    return step.startswith("⟦human-owed⟧") or carries_mark(trailing_markers(step), "human-owed")


def listed_phases(step):
    """The phases step lists, in order; [] for a step that lists none."""
    listed = PHASES_RE.search(trailing_markers(step))
    return [phase.strip() for phase in listed.group(1).split(",")] if listed else []


def next_phase(step):
    """The first phase step lists and has not marked done, or None once a phase is marked owed.

    cover-new runs before migrate whatever order the step lists them in.
    """
    phases = listed_phases(step)
    if "cover-new" in phases and "migrate" in phases:
        phases.remove("cover-new")
        phases.insert(phases.index("migrate"), "cover-new")
    for phase in phases:
        if mark(phase, "owed") in step:
            return None
        if mark(phase, "done") not in step:
            return phase
    return None


def new_step(text, criterion):
    """The ledger_add_step line for text and criterion."""
    return f"{OPEN_STEP} {text} {ADDED_MARK} {CRITERION_TAG}{criterion}⟧"


def ledger_steps(text):
    """One (index, state, kind, pending, added, criterion, text) record per step line."""
    records = []
    for line in text.split("\n"):
        match = STEP_RE.fullmatch(line)
        if not match:
            continue
        step = match.group(4) or ""
        phased_done = listed_phases(step) and next_phase(step) is None
        state = "open" if match.group(2) == " " and not phased_done else "done"
        markers = trailing_markers(step)
        kind = KIND_RE.search(markers)
        criterion = (re.findall(CRITERION_RE, markers) or [""])[-1]
        added = is_added(step)
        pending = state == "done" and step.endswith(PENDING_MARK)
        if pending:
            step = step[: -len(PENDING_MARK)]
        records.append((
            str(len(records) + 1),
            state,
            kind.group(1) if kind else "human-owed" if is_human_owed(step) else "step",
            "1" if pending else "0",
            "1" if added else "0",
            criterion,
            step,
        ))
    return records


def multi_tag_refusal(steps):
    """The refusal for the first of steps carrying more than one criterion tag, or ""."""
    for *_, text in steps:
        if trailing_markers(text).count(CRITERION_TAG) > 1:
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


def _with_phase_mark(line, phase, state):
    """line with mark(phase, state) appended; ValueError when line does not list phase or phase is not next."""
    if phase not in listed_phases(line):
        raise ValueError(f"step does not list phase '{phase}'")
    if next_phase(line) != phase:
        raise ValueError(f"phase '{phase}' is not the step's next phase")
    return line + mark(phase, state)


def ledger_mark_phase(text, matcher, phase, owed=False):
    """(True, text with the first open step holding matcher marked phase done, or owed), or (False, text).

    ValueError when that step does not list phase.
    """
    return _rewrite_first_step(
        text,
        _open_holding(matcher),
        lambda match, line: _with_phase_mark(line, phase, "owed" if owed else "done"),
    )


def ledger_clear_pending(text, matcher):
    """(True, text with the first line holding matcher cleared of the mark), or (False, text)."""
    return _rewrite_first_step(
        text,
        lambda match, line: match.group(2) != " " and line.endswith(PENDING_MARK) and matcher in line,
        lambda match, line: line.removesuffix(PENDING_MARK),
    )
