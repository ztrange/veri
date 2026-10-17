"""Cases for the conductor's marks in the run's event log, as skills/tdd/SKILL.md prescribes them, read as text.

Contract under test:
  SKILL.md prescribes an `event.sh <mark>` call in the same instruction as the issue comment
  that mark mirrors; the refactor mark carries transforms, budget, stopped and pass, with the
  count observed and unclamped; every `add-ledger-step.sh` insertion has a `step-added` call
  beside it; and the exhausted-budget split and the needs-user park each leave a mark.
"""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

INSERTION = rb"\$s/add-ledger-step\.sh"

_UPPER = bytes.maketrans(bytes(range(65, 91)), bytes(range(97, 123)))
_SPACE = rb"[ \t\n\r\f\v]"


def _records():
    out, rec = [], b""
    for line in SKILL.read_bytes().split(b"\n"):
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


def _refactor_mark(records):
    return _mark(records, b"refactor", "posts the `### 🛠️ Refactor` comment",
                 rb"### [^ ]+ refactor( |`|$)", b"post", b"rev-list --count")


def _refactor_call(marked):
    return re.search(rb"(event\.sh" + _SPACE + rb"+refactor([^a-z0-9-][^`]*)?)", marked).group(1)


def _records_or_fail(what):
    records = _records()
    assert records, f"SKILL.md has no instructions to read — {what} could not be checked"
    return records


def _marked_refactor(what):
    records = _records_or_fail(what)
    marked, problems = _refactor_mark(records)
    assert not problems, "\n".join(problems)
    return marked


def _event_calls(record):
    return [m.group(0) for m in re.finditer(rb"event\.sh [a-z][a-z-]*( [a-z]+=[^ ]+)*", record)]


def test_skill_prescribes_an_event_sh_call_for_each_of_the_conductors_seven_marks_beside_the_issue_comment_it_mirrors():
    records = _records_or_fail("no mark")
    problems = []
    for result in (
        _mark(records, b"step-start", "takes the next unchecked step with next-unchecked.sh", rb"next-unchecked\.sh"),
        _comment_mark(records, b"step-done", "### ✅ Step done", b"step done"),
        _comment_mark(records, b"pin", "### 📌 Already satisfied", b"already satisfied"),
        _comment_mark(records, b"revise", "### ♻️ Revise <phase> — attempt <k>", b"revise <phase>", b"attempt"),
        _comment_mark(records, b"bail", "### ⛔ Bailed — <phase>", b"bailed"),
        _comment_mark(records, b"done", "### ✅ Done — <pr-url>", b"pr-url"),
        _comment_mark(records, b"resume", "### ▶️ Resuming", b"resuming"),
    ):
        problems += result[1]
    assert not problems, "\n".join(problems)


def test_skill_writes_an_event_sh_refactor_mark_carrying_transforms_budget_and_stopped_beside_the_refactor_comment():
    call = _refactor_call(_marked_refactor("the refactor mark"))
    problems = [
        f"SKILL.md calls `{call.decode()}` without `{key}=` — metrics.sh's cell stays unknown"
        for key in ("transforms", "budget", "stopped")
        if not re.search(rb"(^|" + _SPACE + rb")" + key.encode() + b"=", call)
    ]
    assert not problems, "\n".join(problems)


def test_skill_prescribes_the_refactor_marks_transforms_as_the_observed_git_rev_list_count_unclamped_on_an_overrun():
    marked = _marked_refactor("the refactor mark's count")
    before = marked.split(b"event.sh refactor", 1)[0]
    sentence = before.rsplit(b". ", 1)[-1]
    problems = []
    if not re.search(rb"observed|rev-list", sentence):
        problems.append(f"SKILL.md introduces the refactor mark without saying its count is the observed one: {sentence[:160].decode(errors='replace')}")
    if not re.search(rb"unclamped|never clamped", sentence):
        problems.append(f"SKILL.md introduces the refactor mark without saying an overrun is recorded unclamped: {sentence[:160].decode(errors='replace')}")
    assert not problems, "\n".join(problems)


def test_skill_names_stopped_nothing_structural_for_refactor_triage_exit_3_and_stopped_structural_owed_for_exit_0_no_stopped_triage_and_keeps_malformed_nothing_left_and_budget():
    marked = _marked_refactor("the refactor mark's stop reasons")
    problems = []
    for code, value in ((b"3", b"nothing-structural"), (b"0", b"structural-owed")):
        exit_re = rb"exit \**" + code + rb"\**"
        value_re = rb"`(stopped=)?" + value + rb"`"
        if not (re.search(exit_re + rb"[^;,.`]{0,40}" + value_re, marked)
                or re.search(value_re + rb"[^;,.`]{0,40}" + exit_re, marked)):
            problems.append(f"SKILL.md does not name `stopped={value.decode()}` against refactor-triage.sh exit {code.decode()}")
    if re.search(rb"`(stopped=)?triage`", marked):
        problems.append("SKILL.md still offers `stopped=triage`, which cannot tell exit 3 from exit 0")
    for value in (b"nothing-left", b"budget", b"malformed"):
        if not re.search(rb"`(stopped=)?" + value + rb"`", marked):
            problems.append(f"SKILL.md no longer offers `stopped={value.decode()}` for the refactor mark")
    assert not problems, "\n".join(problems)


def test_skill_prescribes_an_event_sh_step_added_call_beside_every_add_ledger_step_insertion():
    records = _records_or_fail("the step-added mark")
    problems, insertions = [], 0
    for line in records:
        if not re.search(INSERTION, line):
            continue
        insertions += 1
        if not _calls_event(line, b"step-added"):
            problems.append(f"SKILL.md inserts a step with no `event.sh step-added` beside it: {line[:130].decode(errors='replace')}")
    if not insertions:
        problems.append("SKILL.md prescribes no `$S/add-ledger-step.sh` call — where `event.sh step-added` belongs could not be read")
    assert not problems, "\n".join(problems)


def test_skill_marks_the_refactor_sections_own_plan_insertion_with_an_event_sh_step_added_call_beside_it():
    records = _records_or_fail("the Refactor section's step-added mark")
    _, problems = _mark(records, b"step-added",
                        "grows the plan with the `uncovered-spec` flags beside the refactor-pending clear",
                        INSERTION, rb"clear-refactor-pending\.sh", b"uncovered-spec")
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


def test_skill_writes_the_refactor_mark_with_pass_k_1_for_a_steps_first_pass_one_more_each_time_the_triangulation_path_resumes_the_refactor_loop():
    marked = _marked_refactor("the refactor mark's pass index")
    call = _refactor_call(marked)
    shown = marked[:160].decode(errors="replace")
    problems = []
    if not re.search(rb"(^|" + _SPACE + rb")pass=", call):
        problems.append(f"SKILL.md calls `{call.decode()}` without `pass=` — two passes of one step cannot be told apart")
    if not (re.search(rb"(^|[^0-9])1([^0-9]|$)[^.;]{0,40}first", marked)
            or re.search(rb"first[^.;]{0,60}[^0-9]1([^0-9]|$)", marked)):
        problems.append(f"SKILL.md does not say a step's first refactor pass marks `pass=1`: {shown}")
    if not (re.search(rb"(one more|increments?|\+ ?1)[^.]{0,120}triangulat", marked)
            or re.search(rb"triangulat[^.]{0,160}(one more|increments?|\+ ?1)", marked)):
        problems.append(f"SKILL.md does not say the pass index counts one more each time the triangulation path resumes the refactor loop: {shown}")
    assert not problems, "\n".join(problems)
