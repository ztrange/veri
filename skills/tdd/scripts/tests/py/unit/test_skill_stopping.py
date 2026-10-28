"""Cases for the sequence skills/tdd/SKILL.md runs when a stop is requested, read as text."""
import importlib
import pathlib
import re

from skill_sections import LOWER, has_match as _has, plain as _plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

LAUNCHING = "## Launching a leaf — detach, then wait in the foreground"
PROCEDURE = "## Procedure"
PREFLIGHT = "## 0. Preflight — baseline checks (bail before any cycle)"
BAILING = "## Bailing"
SCRIPTS = "## The scripts (this skill's `scripts/` directory)"


def _section(heading, doc=SKILL):
    section = importlib.import_module("skill_sections").section(doc, heading)
    lines = _plain(section).split("\n")[1:]
    assert "".join(lines).strip(), f"{doc.name} has no {heading} section — nothing could be checked"
    return lines


def _first(pattern, lines):
    return next((n for n, line in enumerate(lines, 1) if re.search(pattern, line)), None)


def _after(a, b):
    return bool(a and b and a > b)


def _joined(lines):
    return re.sub(" +", " ", " ".join(lines) + " ")


def _word(word):
    return rf"(^|[^a-z-]){word}([^a-z-]|$)"


def _either_order(a, b):
    return rf"{a}[^.;]*{b}|{b}[^.;]*{a}"


def _require(problems, pattern, lines, message):
    if not _has(pattern, lines):
        problems.append(message)


def _refuse(problems, pattern, lines, message):
    if _has(pattern, lines):
        problems.append(message)


def _branch(lines, start, end):
    out, inside = [], False
    for line in lines:
        if not inside and re.search(start, line):
            inside = True
        if inside:
            out.append(line)
            if re.search(end, line):
                break
    return out


def _unreadable_at_ledger(problems, what, lines):
    _require(problems, r"exit 2[^.;]*at-ledger", lines,
             f"{what} never says stop-requested.sh's exit 2 is a stop in mode at-ledger")
    _require(problems, _either_order("exit 2", "unreadable"), lines,
             f"{what} never says to narrate that the stop request was unreadable on exit 2")


def test_launching_a_leaf_runs_stop_requested_before_every_leaf_launch_exit_3_launches_as_normal_at_ledger_launches_the_leaf_anyway_at_leaf_and_now_launch_nothing_and_go_to_stopping():
    lines, problems = [_joined(_section(LAUNCHING))], []
    _require(problems, r"stop-requested\.sh", lines, "the Launching a leaf section never runs stop-requested.sh")
    _require(problems, _either_order(r"before[^.;]*launch", r"stop-requested\.sh"), lines,
             "the Launching a leaf section never says stop-requested.sh runs before a leaf is launched")
    _require(problems, r"exit 3[^.;]*launch", lines,
             "the Launching a leaf section never says stop-requested.sh's exit 3 launches as normal")
    _require(problems, r"at-ledger[^.;]*launch", lines,
             "the Launching a leaf section never says mode at-ledger launches the leaf anyway")
    for mode in ("at-leaf", "now"):
        _require(problems, _word(mode) + r"[^.;]*launch(es)? nothing", lines,
                 f"the Launching a leaf section never says mode {mode} launches nothing")
    _require(problems, r"launch(es)? nothing[^.;]*stopping", lines,
             "the Launching a leaf section never sends a launch-nothing mode to Stopping")
    assert not problems, problems


def test_launching_a_leaf_treats_stop_requested_exit_2_as_a_stop_in_mode_at_ledger_narrating_that_the_request_was_unreadable():
    problems = []
    _unreadable_at_ledger(problems, "the Launching a leaf section", [_joined(_section(LAUNCHING))])
    assert not problems, problems


def _phase_exit2(heading, anchor):
    inside, kept = False, []
    for raw in (SKILL.read_text() + "\n" + SKILL.with_name("REVISE.md").read_text()).splitlines():
        if re.match(r"#{2,4} ", raw):
            inside = bool(re.search(heading, raw.translate(LOWER)))
            continue
        if inside:
            kept.append(_plain(raw))
    out, buf, hit = None, "", False
    for line in kept:
        if re.match(r"[ \t]*$", line) or re.match(r"[ \t]*(- |[0-9]+\. )", line):
            if hit:
                out = buf
                break
            buf = ""
        if re.match(r"[ \t]*$", line):
            continue
        buf += " " + line
        if re.search(anchor, line):
            hit = True
    else:
        if hit:
            out = buf
    return None if out is None else re.sub(" +", " ", out)


def test_launching_a_leaf_asks_stop_requested_before_reading_a_leafs_wait_leaf_exit_2_as_killed_stuck_and_a_pending_now_goes_to_stopping_instead_of_bailing():
    lines, problems = [_joined(_section(LAUNCHING))], []
    _require(problems, _either_order(r"stop-requested\.sh", r"before[^.;]*killed-stuck"), lines,
             "the Launching a leaf section never asks stop-requested.sh before reading a leaf's exit 2 as killed-stuck")
    _require(problems, rf"{_word('now')}[^.;]*stopping[^.;]*(instead of|rather than)[^.;]*bailing|{_word('now')}[^.;]*(instead of|rather than)[^.;]*bailing[^.;]*stopping", lines,
             "the Launching a leaf section never sends a leaf's exit 2 with a pending now to Stopping instead of Bailing")
    assert not problems, problems


def test_each_phases_leaf_exit_2_branch_points_back_to_launching_a_leaf_where_stop_requested_is_asked_before_the_exit_2_is_read_as_killed_stuck():
    phases = [
    ]
    problems = []
    for phase, heading, anchor in phases:
        clause = _phase_exit2(heading, anchor)
        if not clause:
            problems.append(f"the {phase} branch has no exit-2 clause to read — nothing could be checked")
            continue
        _require(problems, "launching a leaf", [clause],
                 f"the {phase} branch reads a leaf's exit 2 without pointing back to Launching a leaf — a pending now stop there would bail")
    assert not problems, problems


def test_987_preflight_step_3_runs_stop_requested_clear_beside_the_tdd_conductor_pid_write():
    lines, problems = [_joined(_branch(_section(PREFLIGHT, SKILL.with_name("PREFLIGHT.md")), r"^3\. suite is green at baseline", r"^4\. "))], []
    _require(problems, r"\.tdd/conductor\.pid", lines,
             "preflight step 3 has no .tdd/conductor.pid write to read — nothing could be checked beside it")
    _require(problems, r"stop-requested\.sh --clear", lines,
             "preflight step 3 never runs stop-requested.sh --clear — a request a killed run left behind would stop the run that resumes it")
    assert not problems, problems


def test_standing_bail_rule_is_stated_once_and_no_line_names_bailing_without_bail_md():
    pointer = "<base directory>/BAIL.md"
    files = [SKILL, SKILL.with_name("SCRIPTS.md"), SKILL.with_name("RECONCILE.md")]
    texts = {path.name: path.read_text().split("\n") for path in files}
    rule = [line for line in texts["SKILL.md"] if "Whenever this procedure says **bail**" in line and pointer in line]
    assert len(rule) == 1, f"SKILL.md holds {len(rule)} standing bail rule lines, expected exactly 1"
    bare = [f"{name}:{n}" for name, lines in texts.items() for n, line in enumerate(lines, 1)
            if re.search(r"\bBailing\b", line) and pointer not in line]
    assert not bare, f"lines name Bailing without {pointer}: {bare}"


def test_skill_md_carries_none_of_the_bailing_sections_lines():
    moved = [r"preserve-attempt\.sh <n> .*\bbail\b", r"event\.sh bail cause=<cause>", r"metrics: what bailing on"]
    skill = SKILL.read_text().split("\n")
    assert not [line for line in skill if line == BAILING], "SKILL.md still carries the ## Bailing heading"
    left = [p for p in moved if _has(p, skill)]
    assert not left, f"SKILL.md still carries the moved lines {left}"
