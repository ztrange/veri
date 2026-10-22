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
import subprocess
import sys

import pytest

SKILL = pathlib.Path(__file__).resolve().parents[3] / "SKILL.md"
BAIL = SKILL.with_name("BAIL.md")
RESUME = SKILL.with_name("RESUME.md")

INSERTION = rb"\$s/add-ledger-step\.sh"

COST_CHECK = "#### The step's cost check"
WS = "[ \t\n\r\f\v]"

_UPPER = bytes.maketrans(bytes(range(65, 91)), bytes(range(97, 123)))
_SPACE = rb"[ \t\n\r\f\v]"


def _records():
    out, rec = [], b""
    for line in (SKILL.read_bytes() + b"\n\n" + BAIL.read_bytes() + b"\n"
                 + SKILL.with_name("PIN.md").read_bytes() + b"\n\n" + RESUME.read_bytes()
                 + b"\n\n" + SKILL.with_name("REVISE.md").read_bytes()).split(b"\n"):
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


def _comment_mark(records, event, heading, *patterns):
    return _mark(records, event, f"posts the `{heading}` comment", *patterns, b"comment")


def _records_or_fail(what):
    records = _records()
    assert records, f"SKILL.md has no instructions to read — {what} could not be checked"
    return records


def _event_calls(record):
    return [m.group(0) for m in re.finditer(rb"event\.sh [a-z][a-z-]*( [a-z]+=[^ ]+)*", record)]


def test_skill_prescribes_an_event_sh_call_for_each_of_the_conductors_seven_marks_beside_the_issue_comment_it_mirrors():
    records = _records_or_fail("no mark")
    problems = []
    for result in (
        _mark(records, b"step-start", "takes the next unchecked step with next-unchecked.sh", rb"next-unchecked\.sh"),
        _comment_mark(records, b"pin", "### 📌 Already satisfied", b"already satisfied"),
        _comment_mark(records, b"revise", "### ♻️ Revise <phase> — attempt <k>", b"revise <phase>", b"attempt"),
        _comment_mark(records, b"bail", "### ⛔ Bailed — <phase>", b"bailed"),
        _comment_mark(records, b"done", "### ✅ Done — <pr-url>", b"pr-url"),
        _comment_mark(records, b"resume", "### ▶️ Resuming", b"resuming"),
    ):
        problems += result[1]
    assert not problems, "\n".join(problems)


def test_skill_prescribes_an_event_sh_step_added_call_beside_every_add_ledger_step_insertion():
    records = _records_or_fail("the step-added mark")
    problems, insertions = [], 0
    for line in records:
        if not re.search(INSERTION, line) or b"<split: value>" in line:
            continue
        insertions += 1
        if not _calls_event(line, b"step-added"):
            problems.append(f"SKILL.md inserts a step with no `event.sh step-added` beside it: {line[:130].decode(errors='replace')}")
    if not insertions:
        problems.append("SKILL.md prescribes no `$S/add-ledger-step.sh` call — where `event.sh step-added` belongs could not be read")
    assert not problems, "\n".join(problems)


def test_skill_marks_the_exhausted_budget_split_and_the_needs_user_park_in_the_event_log_the_split_told_apart_from_a_leaf_volunteered_one():
    records = _records_or_fail("the exhausted-budget marks")
    split_rec = park_rec = bail_rec = volunteered_rec = b""
    for line in records:
        if b"exhausted-answer" in line and b"instead-of" in line:
            split_rec = line
        elif b"exhausted-answer" in line and b"park" in line:
            park_rec = line
        elif re.search(rb"exit" + _SPACE + b"+3", line) and b"revise-exhausted" in line:
            bail_rec = line
        elif re.search(INSERTION, line) and re.search(_SPACE + b"before" + _SPACE, line) and b"split:" in line:
            volunteered_rec = line

    problems = []
    split_calls = _event_calls(split_rec)
    if not split_rec:
        problems.append("SKILL.md prescribes no instead-of insertion beside .tdd/exhausted-answer.txt — where the split outcome's mark belongs could not be read")
    elif not volunteered_rec:
        problems.append("SKILL.md prescribes no `before` insertion for a leaf-volunteered split — what the exhausted split must be told apart from could not be read")
    elif not any(call not in volunteered_rec for call in split_calls):
        problems.append(f"SKILL.md marks the split a run reaches at exhaustion with nothing a leaf-volunteered split does not write too, so the log cannot say which of the two grew the plan: {split_rec[:130].decode(errors='replace')}")

    if not park_rec:
        problems.append("SKILL.md prescribes no park beside .tdd/exhausted-answer.txt — where the escalated outcome's mark belongs could not be read")
    else:
        park_calls = _event_calls(park_rec)
        if not park_calls:
            problems.append("SKILL.md parks a step at exhaustion with no `event.sh` call beside it, so the outcome that stops a run without bailing it leaves no mark in the log")
        else:
            split_names = {call.split()[1] for call in split_calls}
            if not any(call.split()[1] not in split_names for call in park_calls):
                problems.append("SKILL.md marks the parked step only with marks the split branch writes too, so the escalated outcome is not distinguishable from the split one")

    if not bail_rec:
        problems.append("SKILL.md no longer names the revise-exhausted cause against exhausted-outcome.sh's exit 3, so the bailed outcome's own mark could not be read")
    assert not problems, "\n".join(problems)


def _text_calls_event(line, event):
    return re.search(r"event\.sh" + WS + "+" + re.escape(event) + r"([^a-z0-9-]|$)", line)


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


def test_skill_md_revise_exhausted_split_writes_step_split_carrying_at_exhausted():
    lines = SKILL.read_text().splitlines() + SKILL.with_name("REVISE.md").read_text().splitlines()
    exhausted = sum(1 for line in lines
                    if _text_calls_event(line, "step-split")
                    and re.search(r"event\.sh step-split" + WS + "+at=exhausted(" + WS + "|$)", line))
    assert exhausted >= 1, "no `event.sh step-split at=exhausted`, so the revise-exhausted split lost the spelling #408 gave it"


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


@pytest.mark.process("SKILL.md's own event.sh refactor line runs under bash -c, its $(next-pending-refactor.sh) and event.sh shim starting real processes")
def test_a_run_whose_skill_md_refactor_mark_is_present_renders_real_refactor_and_stopped_cells_for_that_step_and_unknown_for_a_step_without_one(tmp_path, run_cli):
    scripts = SKILL.parent / "scripts"
    call = next((line.strip() for line in SKILL.read_text().splitlines() if "event.sh refactor " in line), None)
    assert call, "SKILL.md has no `event.sh refactor` call line to run — the report could not be checked"
    tidied = "the step whose refactor mark was written"
    untidied = "the step that wrote no refactor mark"
    for old, new in (("$S", str(scripts)), ("<n>", "230"), ("<STEP>", tidied), ("<count>", "7"),
                     ("<VERI_REFACTOR_BUDGET>", "5"), ("<reason>", "budget")):
        call = call.replace(old, new)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-230.md").write_text(f"- [x] {tidied} ⟂ refactor pending\n- [ ] {untidied}\n")
    event = importlib.import_module("veri.event")
    for step in (tidied, untidied):
        code, out, err = run_cli(event, ["launch", "name=develop-refactor"], cwd=tmp_path, env={
            "VERI_ISSUE": "230", "VERI_ACTOR": "developer", "VERI_STEP": step, "VERI_PHASE": "refactor", "VERI_ATTEMPT": "1"})
        assert code == 0, f"event.sh could not write the fixture's launch line for step: {step}: {err}"
    ran = subprocess.run(["bash", "-c", call], cwd=tmp_path, capture_output=True, text=True)
    assert ran.returncode == 0, f"the call SKILL.md prescribes did not run: {call}: {ran.stderr}"
    code, report, err = run_cli(importlib.import_module("veri.metrics"), ["230"], cwd=tmp_path)
    assert code == 0, f"want metrics.sh to exit 0, it did not: {report}{err}"

    def cell_of(step, want):
        seen, col = False, 0
        for line in report.splitlines():
            if not line.startswith("|"):
                seen, col = False, 0
                continue
            cells = line.split("|")
            if not seen:
                seen = True
                for i in range(1, len(cells) - 1):
                    if cells[i].strip() == want:
                        col = i
                continue
            if col and cells[1].strip() == step:
                return cells[col].strip()
        return ""

    problems = []
    for step, heading, want in ((tidied, "refactor", "7/5"), (tidied, "stopped", "budget"),
                                (untidied, "refactor", "unknown"), (untidied, "stopped", "unknown")):
        got = cell_of(step, heading)
        if got != want:
            problems.append(f'step "{step}": want its {heading} cell to say `{want}`, it says `{got}`')
    assert not problems, "\n".join(problems) + f"\nthe report was: {report!r}"
