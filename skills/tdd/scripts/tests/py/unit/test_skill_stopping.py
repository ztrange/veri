"""Cases for the sequence skills/tdd/SKILL.md runs when a stop is requested, read as text."""
import importlib
import pathlib
import re

from skill_sections import has_match as _has, plain as _plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

PROCEDURE = "## Procedure"
PREFLIGHT = "## 0. Preflight — baseline checks (bail before any cycle)"
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


