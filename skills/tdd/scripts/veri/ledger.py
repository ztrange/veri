"""The ledger reader and ticker, ledger_steps and ledger_tick, run in-process;
the one module that spells the ledger's grammar.

Interface: reading (read_ledger, ledger_items, ledger_steps, items_at), writing (replace_ledger, rewrite_ledger,
ledger_tick, ledger_mark_phase, ledger_clear_pending, tick_line), a step's parts and predicates (body, listed_phases,
next_phase, unphased, trailing_markers, unit_of, carries_mark, is_added, is_human_owed, is_skill_edit, is_retired,
handed_out), builders (new_step, open_step_line, mark, retire_mark), checks (multi_tag_refusal) and
the constants (STEP_RE, ITEM_RE, PHASES_RE, OPEN_STEP, TICKED_STEP, PENDING_MARK, ADDED_MARK, INTERFACE_PHASES, ...).
"""
import os
import re
import shutil
import sys
import tempfile
from collections import namedtuple

from git import git
from run_dir import ledger as run_ledger

OPEN_STEP = "- [ ]"
TICKED_STEP = "- [x]"
PENDING_MARK = " ⟂ refactor pending"
ADDED_MARK = "⟦added⟧"
CRITERION_TAG = "⟦criterion "
SPACE = r"[ \t\n\v\f\r]"
STEP_RE = re.compile(rf"({SPACE}*-{SPACE})\[([ xX])\]( (.*))?")
CRITERION_RE = CRITERION_TAG + "([0-9]+)⟧"
KIND_RE = re.compile(r"⟦(full-suite|human-owed|diff-checked)⟧ (?:" + ADDED_MARK
                     + " )?(?:⟦(?:branch|quality)-repair⟧ )?" + CRITERION_RE)
INTERFACE_PHASES = ("expand", "cover-new", "migrate", "contract-a", "contract-b")  # the phases of an interface change
MARK_DELIMITER = " ⟂ "
PHASES_RE = re.compile(r"⟦phases: ([^⟧]*)⟧")
TRAILING_RUN_RE = re.compile(r"((?:(?:^| |(?<=⟧))⟦[^⟦⟧]*⟧)+)(?: ⟂ [^⟦⟧⟂]*)*$")
HEADING_UNIT_RE = re.compile(r"(?:[^`]*(?<=\s)`(?=\S)[^`]*`)*+[^`]*(?=`)")


# A clause (cut at , ; . or a newline) that names the before-state and says green or pass, and says
# nothing of failing, being red, negating or "after": "fails on the before-state and passes after" is not it.
_CLAUSE = r"(?:(?!\bfail|\bred\b|\bnot\b|n't|\bafter\b)[^,;.\n])*"
BEFORE_STATE_GREEN = re.compile(
    r"(?:^|(?<=[,;.\n]))" + _CLAUSE
    + r"(?:before-state" + _CLAUSE + r"\b(?:green|pass)|\b(?:green|pass)" + _CLAUSE + r"before-state)")


def ledger_path(run_dir, issue):
    """One-line delegate of run_dir.ledger. Its only caller is wrong_test_route.py (line 312, owned by open PR #3792);
    delete it, and its tests (test_ledger.py, test_wrong_test_route.py), once #3792 lands and that module calls
    run_dir.ledger."""
    return run_ledger(run_dir, issue)


def added_file(path):
    """The `-added.md` record beside a ledger file: the planned steps its run added."""
    return re.sub(r"\.md$", "", path) + "-added.md"


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
    return record.state == "open" and record.kind in ("step", "diff-checked")


def is_added(step):
    """True when the added marker ends the text, the pending mark and one criterion marker cut."""
    untagged = step.removesuffix(PENDING_MARK)
    tag = untagged.rfind(" " + CRITERION_TAG)
    if tag != -1 and untagged.endswith("⟧"):
        untagged = untagged[:tag]
    return untagged.endswith(" " + ADDED_MARK)


def body(step):
    """step's text before its first ' ⟂ ' mark; step itself when it carries none."""
    return step.split(MARK_DELIMITER, 1)[0]


def retire_mark(reason):
    """The mark that retires a step, e.g. retire_mark("already holds")."""
    return f" ⟂ retired {reason}"


def is_retired(text):
    """True when text carries any retire mark."""
    return "⟂ retired" in text


def mark(phase, state):
    """The mark a phase appends to its step: state is "done" for its commit, "owed" for a contract filed as owed."""
    return f" ⟂ {phase} {state}"


def trailing_markers(step):
    """The run of ⟦…⟧ markers ending step's text, before any ⟂ marks; "" for none."""
    run = TRAILING_RUN_RE.search(step)
    return run.group(1) if run else ""


def unphased(text):
    """text without its refactor-pending mark and every ⟂ <phase> done mark."""
    return re.sub(r" ⟂ \S+ done", "", text.removesuffix(PENDING_MARK))


def unit_of(text):
    """The unit a skill-edit step names: its first path-shaped backticked span, or None.

    A heading unit (`<file>#<heading>`) runs past inner pairs, each opened by a backtick that whitespace precedes
    and a non-space follows, to the first other backtick, so a heading holding backticks stays whole and one
    closed by punctuation ends there, before any later span; with no such backtick it is the plain span.
    """
    for match in re.finditer(r"`([^`]+)`", text):
        span = match.group(1)
        if "/" in span or span.endswith(".md"):
            heading = HEADING_UNIT_RE.match(text, match.start(1)) if "#" in span else None
            return heading.group() if heading else span
    return None


def carries_mark(text, name):
    """True when ⟦name⟧ occurs anywhere in text."""
    return f"⟦{name}⟧" in text


def has_kind(step, mark):
    """True when step is of the kind <mark> names (a full mark, "⟦ci-repair⟧"; "⟦phases:" for a phases mark).

    A kind comes from the step's trailing marker run, plus exactly one leading form: a leading ⟦skill-edit⟧.
    step may be a whole ledger line, its `- [ ] ` / `- [x] ` prefix is dropped first. A mark quoted anywhere else,
    or leading any other step, is no kind (#4709)."""
    found = STEP_RE.fullmatch(step)
    text = (found.group(4) or "") if found else step
    if mark in trailing_markers(text):
        return True
    return mark == "⟦skill-edit⟧" and text.startswith("⟦skill-edit⟧")


def is_skill_edit(step):
    return has_kind(step, "⟦skill-edit⟧")


GO_RED_MARK = "⟦go-red⟧"
GO_RED_PROBE_RE = re.compile(r"probe `([^`]+)` `([^`]+)` → `([^`]*)` on `([^`]+)`")


def is_go_red(step):
    """True when ⟦go-red⟧ is among step's trailing markers, the rule is_diff_checked applies to its kind: a guard proven
    by a mutation probe on its named case. A mention elsewhere in the text (a backticked `⟦go-red⟧`, a leading marker)
    is not. The one go-red test every stage applies (tick-ledger, step-tick, run-step, red-half, go-red-step)."""
    return carries_mark(trailing_markers(step), "go-red")


def go_red_probe(step):
    """(file, old, new, case) a ⟦go-red⟧ step's ``probe `<file>` `<old>` → `<new>` on `<case>` `` names; None when
    the step names no such probe."""
    match = GO_RED_PROBE_RE.search(step)
    return match.groups() if match else None


def is_human_owed(step):
    step = step.strip()
    return step.startswith("⟦human-owed⟧") or carries_mark(trailing_markers(step), "human-owed")


DEVIATION_RE = re.compile(r"⟦deviation ([^⟧]+)⟧")


def deviation_rule(step):
    """The rule a deviation line's trailing ⟦deviation <rule>⟧ marker names, the line a bail's deviate answer leaves
    for a human's review; None for any other line."""
    found = DEVIATION_RE.search(trailing_markers(step))
    return found.group(1) if found else None


def listed_phases(step):
    """The phases step lists, in order; [] for a step that lists none."""
    listed = PHASES_RE.search(trailing_markers(step))
    return [phase.strip() for phase in listed.group(1).split(",")] if listed else []


def next_phase(step):
    """The first phase step lists and has not marked done, or None once a phase is marked owed.

    cover-new and dual-stub run before migrate whatever order the step lists them in.
    """
    phases = listed_phases(step)
    for early in ("cover-new", "dual-stub"):
        if early in phases and "migrate" in phases:
            phases.remove(early)
            phases.insert(phases.index("migrate"), early)
    for phase in phases:
        if mark(phase, "owed") in step:
            return None
        if mark(phase, "done") not in step:
            return phase
    return None


def open_step_line(text):
    """The unticked checkbox line holding text."""
    return f"{OPEN_STEP} {text}"


def new_step(text, criterion):
    """The ledger_add_step line for text and criterion."""
    return open_step_line(f"{text} {ADDED_MARK} {CRITERION_TAG}{criterion}⟧")


ITEM_RE = re.compile(r"\s*- \[(.)\] (.*)")


def ledger_items(text):
    """Every checkbox item of a ledger text, ticked or not: a match of (box character, step text) per line."""
    return [m for m in (ITEM_RE.match(line) for line in text.splitlines()) if m]


def items_at(rev, path):
    """The checkbox items the ledger at `path` holds at `rev`; OSError when git cannot show it."""
    done = git("show", "%s:%s" % (rev, path), capture_output=True)
    if done.returncode != 0:
        raise OSError("git show %s:%s failed: %s" % (rev, path, " ".join(os.fsdecode(done.stderr).split())))
    return ledger_items(done.stdout.decode("utf-8", "replace"))


# One ledger step. A tuple, so it unpacks, compares and tab-joins as the plain 7-tuple always did; the flag fields
# (pending, added) stay the strings "1"/"0" that ledger-steps.sh prints. `number` is the 1-based position among
# step lines (named so it does not shadow tuple.index), `state` "open" or "done", `kind` "step", "full-suite",
# "diff-checked" or "human-owed". `collections.namedtuple`, not typing.NamedTuple: typing costs ~3 ms of import
# every importer of this module would pay.
Step = namedtuple("Step", "number state kind pending added criterion text")


def ledger_steps(text):
    """One Step (number, state, kind, pending, added, criterion, text) per step line."""
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
        records.append(Step(
            str(len(records) + 1),
            state,
            kind.group(1) if kind else "human-owed" if is_human_owed(step) else "step",
            "1" if pending else "0",
            "1" if added else "0",
            criterion,
            step,
        ))
    return records


def same_step(one, other):
    """True when two step texts name one step: equal once each drops its ⟦…⟧ marks and its trailing ⟂ suffix, the one
    comparison a fused stage makes of its record's step and the open one (PRD 038.1 SC3, #4310)."""
    def key(text):
        return " ".join(re.sub(r"⟦[^⟦⟧]*⟧", " ", body(text)).split())
    return key(one) == key(other)


def same_text(reference, text):
    """step_at's default text rule: the reference is the step's whole text."""
    return reference == text


def step_at(steps, reference, *, text_matches=same_text, by_index=False):
    """The Step a reference names, or None: the one answer to "no such step".

    A reference is a step number or a step's text. Two things the callers differ on are parameters:
    - text_matches(reference, text): which texts the reference names (default: equal; the first match wins).
    - by_index: False (default) reads a reference of digits (str.isdigit) as a 1-based position, int-parsed
      ("01" is step 1; none past the last or below the first; never looked up as text). True takes a reference
      only as one of the steps' own `number` strings ("01" is none) and, when none is, looks it up as text.
    """
    if by_index:
        found = next((step for step in steps if step.number == reference), None)
        return found or next((step for step in steps if text_matches(reference, step.text)), None)
    if reference.isdigit():
        try:
            position = int(reference)
        except ValueError:
            return None
        return steps[position - 1] if 1 <= position <= len(steps) else None
    return next((step for step in steps if text_matches(reference, step.text)), None)


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


def tick_line(match):
    """The step line a STEP_RE match was made of, its box ticked."""
    return f"{match.group(1)}[x]{match.group(3) or ''}"


def ledger_tick(text, matcher, pending=False):
    """(True, text with the first open step holding matcher ticked), or (False, text)."""
    return _rewrite_first_step(
        text,
        _open_holding(matcher),
        lambda match, line: f"{tick_line(match)}{PENDING_MARK if pending else ''}",
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


_SURROUND, _SHORT = "surround", "short"
SURROUND_SHORT_MARK = mark(_SURROUND, _SHORT)


def ledger_mark_surround_short(text, matcher):
    """(True, text with the first open step holding matcher marked ⟂ surround short), (None, text) when that step
    already carries the mark (its one free relaunch is spent), or (False, text) when no open step holds matcher.

    ValueError when surround is not that step's next phase.
    """
    spent = []

    def rewrite(match, line):
        if line.endswith(SURROUND_SHORT_MARK) or SURROUND_SHORT_MARK + " " in line:
            spent.append(line)
            return line
        return _with_phase_mark(line, _SURROUND, _SHORT)

    found, new = _rewrite_first_step(text, _open_holding(matcher), rewrite)
    return (None, text) if spent else (found, new)


def ledger_clear_pending(text, matcher):
    """(True, text with the first line holding matcher cleared of the mark), or (False, text)."""
    return _rewrite_first_step(
        text,
        lambda match, line: match.group(2) != " " and line.endswith(PENDING_MARK) and matcher in line,
        lambda match, line: line.removesuffix(PENDING_MARK),
    )
