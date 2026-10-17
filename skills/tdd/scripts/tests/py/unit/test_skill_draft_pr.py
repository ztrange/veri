"""Cases for what skills/tdd/SKILL.md tells the conductor about readying the draft PR, and where it pushes the branch."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

DRAFT_PR = "### 4. Draft PR"
PLAN = "### 2. Scope & plan → the ledger"
GREEN = "#### Green — minimum implementation (developer leaf), then verify-green (blind)"
REFACTOR = "#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"

_UPPER = {c: c + 32 for c in range(ord("A"), ord("Z") + 1)}


def _lower(text):
    return text.translate(_UPPER)


def _lines(heading, stop_at_any_hash=False):
    section = importlib.import_module("skill_sections").section(SKILL, heading)
    lines = section.splitlines()[1:]
    if stop_at_any_hash:
        for i, line in enumerate(lines):
            if line.startswith("#"):
                return lines[:i]
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


def record_number(records, pattern):
    return next((n for n, r in enumerate(records, 1) if re.search(pattern, r)), None)


def any_line(lines, pattern):
    return any(re.search(pattern, line) for line in lines)


def draft_pr():
    return _records(_lines(DRAFT_PR))


def test_draft_prs_step_readies_the_pr_against_the_already_pushed_branch_with_no_push_of_its_own():
    pushes = first_record(draft_pr(), re.escape("git push"))
    assert not pushes, f"Draft PR step still pushes the branch itself: {pushes[:120]}"


def test_green_pass_and_verify_refactor_pass_both_push_the_branch_at_the_two_points_that_write_the_ledger():
    problems = []
    for heading in (GREEN, REFACTOR):
        record = first_record(_records(_lines(heading, True)), r"^ *- \*\*pass")
        if not record:
            problems.append(f"no PASS branch under {heading!r} to read")
        elif "push-branch.sh" not in record:
            problems.append(f"{heading!r} PASS branch never runs push-branch.sh: {record[:120]}")
    assert not problems, problems


def test_draft_prs_step_runs_detect_test_command_tier_all_command_exactly_once_as_the_only_full_suite_gate():
    records = draft_pr()
    assert (
        any_line(records, r"detect-test-command\.sh --tier all")
        and any_line(records, re.escape("exactly once"))
        and any_line(records, _word("only"))
    ), "Draft PR step never runs detect-test-command.sh --tier all's command exactly once as the only full-suite gate"


def test_draft_prs_step_adds_a_repair_step_to_the_ledger_on_a_red_full_run_rather_than_bailing():
    records = draft_pr()
    repair = first_record(records, re.escape("repair step"), _word("red"), re.escape("ledger"))
    assert repair, "Draft PR step has no record adding a repair step to the ledger on a red full run"
    problems = []
    if not (any_line(records, re.escape("unit-tier test")) and any_line(records, _word("gap"))):
        problems.append("never says a unit-tier test is added when the red full run exposes a gap")
    if not any_line(records, r"verifier[^.]*full command"):
        problems.append("never says the repair step's verifier judges the fix against the full command")
    assert not problems, problems


def test_draft_prs_step_bails_on_a_second_red_full_run_after_a_repair_step_naming_every_suite_still_red():
    second = first_record(draft_pr(), _word("bail"), r"second red|red again", re.escape("repair step"))
    assert second, "Draft PR step has no record bailing on a second red full run after a repair step"
    assert re.search(r"every (suite still red|red suite|failing suite|still-red suite)", second), (
        f"bails on a second red full run without naming every suite still red: {second[:120]}"
    )


def test_draft_prs_step_puts_refactor_owed_render_output_in_the_pr_body_and_omits_the_section_on_exit_3():
    records = draft_pr()
    render = first_record(records, re.escape("refactor-owed.sh render"))
    assert render, "Draft PR step never runs refactor-owed.sh render"
    problems = []
    if not re.search(r"issue-[^ ]*refactor-owed\.md", render):
        problems.append(f"runs refactor-owed.sh render without naming the run's refactor-owed file: {render[:120]}")
    if "body" not in render:
        problems.append(f"renders the owed section without putting it in the PR body: {render[:120]}")
    if not first_record(records, re.escape("refactor-owed"), r"exits? 3", r"omit|left out|leaves it out|no section|nothing"):
        problems.append("never says an exit 3 from refactor-owed.sh render leaves the section out")
    assert not problems, problems


def test_draft_prs_step_copies_the_ledgers_owed_steps_bullets_into_the_pr_body_under_owed_steps():
    owed = [r for r in draft_pr() if "owed steps" in r]
    assert owed, "Draft PR step never mentions the ledger's ## Owed steps section"
    problems = []
    if not any_line(owed, re.escape(".tdd/issue-<n>.md")):
        problems.append("speaks of ## Owed steps without naming the run's .tdd/issue-<n>.md ledger")
    if not any_line(owed, re.escape("body")):
        problems.append("never puts the ## Owed steps bullets in the PR body")
    assert not problems, problems


def test_scope_and_plan_step_pushes_and_opens_the_draft_pr_after_the_plan_commit_before_the_plan_comment():
    records = _records(_lines(PLAN))
    pr_at = record_number(records, re.escape("gh api repos/{owner}/{repo}/pulls -f draft=true"))
    assert pr_at, "Scope & plan step never opens the draft PR"
    pr_record = records[pr_at - 1]
    problems = []
    if "draft=true" not in pr_record:
        problems.append(f"opens the PR without draft=true: {pr_record[:120]}")
    if "closes #<n>" not in pr_record:
        problems.append(f"opens the PR without Closes #<n> in its body: {pr_record[:120]}")
    if not re.search(r"wip|work in progress", pr_record):
        problems.append(f"opens the PR without a title marking the work in progress: {pr_record[:120]}")
    if not any_line(records, re.escape("push-branch.sh")):
        problems.append("never runs push-branch.sh")
    commit_at = record_number(records, re.escape("plan: scope #<n> into"))
    comment_at = record_number(records, re.escape("mirror the plan"))
    if commit_at is None or comment_at is None:
        problems.append("no longer has both the plan commit and the Plan comment to place the PR between")
    else:
        if not commit_at < pr_at:
            problems.append(f"opens the PR at record {pr_at}, before the plan commit at record {commit_at}")
        if not pr_at < comment_at:
            problems.append(f"opens the PR at record {pr_at}, after the Plan comment at record {comment_at}")
    assert not problems, problems


def test_green_pass_branch_updates_the_pr_body_with_the_ledgers_done_of_total_step_count():
    record = first_record(_records(_lines(GREEN, True)), r"^ *- \*\*pass")
    assert record, "no PASS branch under the Green section to read"
    assert "gh api -x patch" in record, "Green PASS branch never edits the PR"
    problems = []
    if "-f body=" not in record:
        problems.append(f"edits the PR without a body field: {record[:120]}")
    if ".tdd/issue-<n>.md" not in record:
        problems.append(f"edits the PR body without naming the ledger as where the count is read from: {record[:120]}")
    if not re.search(r"<done> of <total>|[0-9]+ of [0-9]+|done of|of how many", record):
        problems.append(f"edits the PR body without a done-of-total step count: {record[:120]}")
    assert not problems, problems


def test_draft_prs_step_creates_no_pr_it_retitles_and_rewrites_the_open_one_and_marks_it_ready_for_review():
    commands = _commands(_lines(DRAFT_PR))
    problems = []
    if not any_line(commands, r"^gh api -x patch .*-f title="):
        problems.append("never edits the PR with a title")
    if not any_line(commands, r"^gh api -x patch .*-f body="):
        problems.append("never edits the PR with a body")
    if not any_line(commands, r"^[^#]*gh_pr_ready"):
        problems.append("never runs gh_pr_ready")
    creates = next((c for c in commands if re.search(r"^gh api repos/[{]owner[}]/[{]repo[}]/pulls -f", c)), "")
    if creates:
        problems.append(f"still creates a PR: {creates[:120]}")
    assert not problems, problems
