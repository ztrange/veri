"""Cases for what skills/tdd/SKILL.md tells the conductor about readying the draft PR, and where it pushes the branch."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

DRAFT_PR = "### 4. Draft PR"
GUARDRAILS = "## Guardrails"
ISSUE = "### 1. Read the issue, enter the issue's worktree, capture the spec (or resume)"

_UPPER = {c: c + 32 for c in range(ord("A"), ord("Z") + 1)}


def _lower(text):
    return text.translate(_UPPER)


def _lines(heading):
    section = importlib.import_module("skill_sections").section(SKILL, heading)
    lines = section.splitlines()[1:]
    return lines


def _records(lines):
    out, rec = [], ""
    for line in lines:
        if re.match(r"[0-9]+\. ", line) or re.match(r"\s*- ", line):
            if rec:
                out.append(rec)
            rec = line
        elif not line.strip():
            if rec:
                out.append(rec)
            rec = ""
        elif not rec:
            rec = line
        else:
            rec = rec + " " + line
    if rec:
        out.append(rec)
    return [_lower(re.sub(r"\s+", " ", r)) for r in out]


def _commands(lines):
    out, buf, cont = [], "", False
    for line in lines:
        line = line.lstrip()
        buf = buf + " " + line if cont else line
        if buf.endswith("\\"):
            buf, cont = buf[:-1], True
            continue
        cont = False
        out.append(buf)
    if cont:
        out.append(buf)
    return [_lower(c) for c in out]


def _word(word):
    return rf"(?<!\w){re.escape(word)}(?!\w)"


def first_record(records, *patterns):
    return next((r for r in records if all(re.search(p, r) for p in patterns)), "")


def any_line(lines, pattern):
    return any(re.search(pattern, line) for line in lines)


SUITE_REPAIR_MARK = "⟦suite-repair⟧"


def commands_of(heading):
    return _commands(_lines(heading))


def draft_pr():
    return _records(_lines(DRAFT_PR))


def draft_pr_read():
    records = draft_pr()
    assert records, "SKILL.md has no ### 4. Draft PR section to read"
    return records


def test_draft_prs_step_readies_the_pr_against_the_already_pushed_branch_with_no_push_of_its_own():
    pushes = first_record(draft_pr_read(), re.escape("git push"))
    assert not pushes, f"Draft PR step still pushes the branch itself: {pushes[:120]}"


def test_worktree_step_no_longer_says_the_draft_pr_is_opened_once_every_step_is_green():
    records = _records(_lines(ISSUE))
    assert records, "SKILL.md has no ### 1. Read the issue section to read"
    stale = first_record(records, re.escape("every step is green"))
    assert not stale, f"worktree step still says the draft PR is opened once every step is green: {stale[:120]}"


def test_skill_md_reaches_the_default_branch_the_issue_and_the_pr_through_the_helper_or_gh_api_never_gh_repo_issue_pr():
    docs = (SKILL, SKILL.with_name("PREFLIGHT.md"))
    text = "".join(doc.read_text() for doc in docs)
    problems = []
    for doc in docs:
        for n, line in enumerate(doc.read_text().splitlines(), 1):
            if re.search(r"\bgh (repo view|issue (view|comment)|pr (create|view|edit|ready|comment))\b", line):
                problems.append(f"{doc.name}:{n}:{line}")
    for route in ("gh_pr_ready", "veri/github.py", "gh api ", "default_branch"):
        if route not in text:
            problems.append(f"SKILL.md and PREFLIGHT.md never name {route}")
    assert not problems, problems


def _opening_the_pr_invariant():
    return first_record(_records(_lines(GUARDRAILS)), re.escape("before you open the pr"))


def test_guardrails_invariant_about_opening_the_pr_says_neither_exactly_once_nor_the_only_full_suite_gate():
    invariant = _opening_the_pr_invariant()
    assert invariant, "Guardrails has no invariant about opening the PR to read"
    problems = [
        f'Guardrails invariant still says "{phrase}": {invariant[:160]}'
        for phrase in ("exactly once", "the only full-suite gate")
        if phrase in invariant
    ]
    assert not problems, problems


def test_guardrails_invariant_about_opening_the_pr_names_the_branchs_own_full_run_again_after_each_suite_repair_step_and_the_extra_run_on_the_rebased_tip_when_sub_step_1_rebased_the_branch():
    invariant = _opening_the_pr_invariant()
    assert invariant, "Guardrails has no invariant about opening the PR to read"
    problems = []
    if not first_record([invariant], r"own full(-suite)? (run|gate)"):
        problems.append(f"invariant never names the branch's own full run: {invariant[:160]}")
    if not first_record([invariant], re.escape(SUITE_REPAIR_MARK)):
        problems.append(f"invariant never says the branch's own full run runs again after each {SUITE_REPAIR_MARK} step: {invariant[:160]}")
    if not first_record([invariant], re.escape("rebased tip"), _word("rebased the branch")):
        problems.append(f"invariant never names the extra run on the rebased tip when sub-step 1 rebased the branch: {invariant[:160]}")
    assert not problems, problems
