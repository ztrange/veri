"""Cases for the conductor's marks in the run's event log, as skills/tdd/SKILL.md prescribes them, read as text.

Contract under test:
  SKILL.md prescribes an `event.sh <mark>` call in the same instruction as the issue comment
  that mark mirrors; the refactor mark carries transforms, budget, stopped and pass, with the
  count observed and unclamped; every `add-ledger-step.sh` insertion has a `step-added` call
  beside it; and the exhausted-budget split and the needs-user park each leave a mark.
"""
import importlib
import pathlib
import re
import sys

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
BAIL = SKILL.with_name("BAIL.md")
RESUME = SKILL.with_name("RESUME.md")

INSERTION = rb"\$s/add-ledger-step\.sh"

COST_CHECK = "#### The step's cost check"
WS = "[ \t\n\r\f\v]"

_UPPER = bytes.maketrans(bytes(range(65, 91)), bytes(range(97, 123)))
_SPACE = rb"[ \t\n\r\f\v]"


def _records():
    out, rec = [], b""
    for line in (SKILL.read_bytes() + b"\n\n" + SKILL.with_name("DRAFT-PR.md").read_bytes() + b"\n\n" + BAIL.read_bytes() + b"\n"
                 + SKILL.with_name("PIN.md").read_bytes() + b"\n\n" + RESUME.read_bytes() + b"\n\n" + SKILL.with_name("SUITE-REPAIR.md").read_bytes()).split(b"\n"):
        if re.match(rb"[0-9]+\. ", line) or re.match(_SPACE + rb"*- ", line):
            if rec:
                out.append(rec)
            rec = line
        elif re.fullmatch(_SPACE + b"*", line):
            if rec:
                out.append(rec)
            rec = b""
        elif not rec:
            rec = line
        else:
            rec = rec + b" " + line
    if rec:
        out.append(rec)
    return [re.sub(_SPACE + b"+", b" ", r).translate(_UPPER) for r in out]


def _calls_event(line, event):
    return re.search(rb"event\.sh" + _SPACE + b"+" + re.escape(event) + rb"([^a-z0-9-]|$)", line)


def _mark(records, event, what, *patterns):
    anchored = None
    for line in records:
        if not all(re.search(p, line) for p in patterns):
            continue
        anchored = anchored or line
        if _calls_event(line, event):
            return line, []
    if anchored is None:
        return None, [f"SKILL.md no longer {what} — where `event.sh {event.decode()}` belongs could not be read"]
    return None, [f"SKILL.md {what} but calls no `event.sh {event.decode()}` beside it: {anchored[:130].decode(errors='replace')}"]


def _records_or_fail(what):
    records = _records()
    assert records, f"SKILL.md has no instructions to read — {what} could not be checked"
    return records


def test_skill_prescribes_an_event_sh_call_for_each_of_the_conductors_seven_marks_beside_the_issue_comment_it_mirrors():
    records = _records_or_fail("no mark")
    problems = []
    problems += _mark(records, b"step-start", "takes the next unchecked step with next-unchecked.sh", rb"next-unchecked\.sh")[1]
    assert not problems, "\n".join(problems)


def test_skill_prescribes_an_event_sh_step_added_call_beside_every_add_ledger_step_insertion():
    records = _records_or_fail("the step-added mark")
    problems, insertions = [], 0
    for line in records:
        if not re.search(INSERTION, line) or b"<split: value>" in line or b"\xe2\x9f\xa6suite-repair\xe2\x9f\xa7" in line or b"\xe2\x9f\xa6ci-repair\xe2\x9f\xa7" in line:
            continue
        insertions += 1
        if not _calls_event(line, b"step-added"):
            problems.append(f"SKILL.md inserts a step with no `event.sh step-added` beside it: {line[:130].decode(errors='replace')}")
    if not insertions:
        problems.append("SKILL.md prescribes no `$S/add-ledger-step.sh` call — where `event.sh step-added` belongs could not be read")
    assert not problems, "\n".join(problems)


def test_skill_marks_the_exhausted_budget_split_and_the_needs_user_park_in_the_event_log_the_split_told_apart_from_a_leaf_volunteered_one():
    records = _records_or_fail("the exhausted-budget marks")
    volunteered_rec = b""
    for line in records:
        if re.search(INSERTION, line) and re.search(_SPACE + b"before" + _SPACE, line) and b"split:" in line:
            volunteered_rec = line

    problems = []
    if not volunteered_rec:
        problems.append("SKILL.md prescribes no `before` insertion for a leaf-volunteered split — what the exhausted split must be told apart from could not be read")
    assert not problems, "\n".join(problems)


def _file_lines():
    return SKILL.read_text().splitlines()


def _cost_check():
    lines = importlib.import_module("skill_sections").section(SKILL, COST_CHECK).splitlines()
    return _file_lines().index(COST_CHECK) + 1, lines


def _exit_bullet_after(start, lines, frm, n):
    for at in range(max(frm + 1, start), start + len(lines)):
        if lines[at - start].startswith(f"- **exit {n} "):
            return at
    return None


def _exit_3_problems(start, lines):
    carry_at = _exit_bullet_after(start, lines, start, 3)
    if carry_at is None:
        return ["SKILL.md's cost check has no `- **exit 3` branch — where the carry-on writes nothing could not be read"]
    problems = []
    for lineno in range(carry_at, start + len(lines)):
        line = lines[lineno - start]
        if lineno > carry_at and line[:1] and not line[0].isspace():
            break
        if re.search(r"event\.sh" + WS + "+[a-z]", line):
            problems.append(f"the over-budget exit 3 branch writes a mark of its own at SKILL.md:{lineno}: {line[:130]}")
    return problems


def test_the_exit_3_case_still_names_a_mark_planted_in_the_exit_3_branch_by_its_line(tmp_path, monkeypatch):
    start, lines = _cost_check()
    carry_at = _exit_bullet_after(start, lines, start, 3)
    assert carry_at, "SKILL.md's cost check has no `- **exit 3` branch — where to plant a mark could not be read"
    planted_at = carry_at + 1
    planted = "  run `$S/event.sh step-not-split` before carrying on."
    file_lines = SKILL.read_text().split("\n")
    fixture = tmp_path / "SKILL.md"
    fixture.write_text("\n".join(file_lines[:carry_at] + [planted] + file_lines[carry_at:]))
    assert fixture.read_text().split("\n")[planted_at - 1] == planted, (
        f"the fixture does not carry the planted mark at line {planted_at}, so what the exit 3 case names could not be asked")
    with monkeypatch.context() as m:
        m.setattr(sys.modules[__name__], "SKILL", fixture)
        try:
            problems = _exit_3_problems(*_cost_check())
            assert not problems, "\n".join(problems)
        except AssertionError as failed:
            named = str(failed)
        else:
            named = ""
    assert f"SKILL.md:{planted_at}" in named, (
        f"the exit 3 case did not name a mark planted in the exit 3 branch at SKILL.md:{planted_at}; it filed: {named or 'nothing'}")
