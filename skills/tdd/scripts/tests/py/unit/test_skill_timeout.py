"""What skills/tdd/SKILL.md tells a conductor to do with the run's hard timeout, read as text."""
import pathlib
import re

import skill_sections

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

PREFLIGHT = "### 0. Preflight — baseline checks (bail before any cycle)"
PLAN = "### 2. Scope & plan → the ledger"

ELAPSED_RE = r"(^|[^a-z])(time|timed|times|timing|elapsed|wall|duration|sec)([^a-z-]|$)"
FULL_RE = r"(^|[^a-z])full(-[a-z]+)?([^a-z-]|$)"


def paragraphs(text):
    records, rec = [], ""
    for line in text.splitlines():
        if re.match(r"[0-9]+\. ", line):
            if rec:
                records.append(rec)
            rec = line
        elif not line.strip():
            if rec:
                records.append(rec)
            rec = ""
        elif not rec:
            rec = line
        else:
            rec = rec + " " + line
    if rec:
        records.append(rec)
    return [r.lower() for r in records]


def claimed(records, *patterns):
    return any(all(re.search(p, r) for p in patterns) for r in records)


def exports_timeout(records):
    return claimed(records, "veri_timeout", "export|every leaf|each leaf|all leaves|every launch|rest of the run")


def test_skill_md_s_preflight_times_the_baseline_run_derives_the_timeout_with_leaf_timeout_sh_and_exports_it_as_VERI_TIMEOUT_for_every_leaf_and_the_plan_comment_states_it_with_the_baseline_it_came_from():
    plan = paragraphs(skill_sections.section(SKILL, PLAN))
    assert claimed(plan, "timeout", "baseline", "comment"), "no plan step has the plan comment state the timeout and the baseline it was derived from"


def test_skill_md_s_preflight_times_the_full_tier_hands_that_measurement_to_leaf_timeout_sh_and_exports_it_as_VERI_TIMEOUT_for_every_leaf_and_the_plan_comment_names_the_tier_the_number_came_from():
    plan = paragraphs(skill_sections.section(SKILL, PLAN))
    assert claimed(plan, "timeout", "comment", FULL_RE + "|tier"), "no plan step has the plan comment name the tier the timeout was derived from"


def test_954_skill_md_makes_the_leaf_timeout_sh_call_that_records_tdd_issue_n_timeout_after_step_1_2_has_entered_the_issue_s_worktree_not_from_the_caller_s_checkout_where_preflight_runs():
    lines = SKILL.read_text().splitlines()
    entered = next((i for i, l in enumerate(lines, 1) if re.search(r'issue-worktree\.sh <n> .*cd "\$wt"', l)), None)
    recording = [i for i, l in enumerate(lines, 1) if re.search(r"VERI_ISSUE=<n>.*leaf-timeout\.sh", l)]
    assert entered is not None, "no step 1.2 line enters the worktree with issue-worktree.sh"
    assert recording, "no leaf-timeout.sh call carries VERI_ISSUE=<n>, the one that records the settled timeout"
    for line in recording:
        assert line > entered, f"the leaf-timeout.sh call at line {line} runs before step 1.2 enters the worktree (line {entered})"


def test_1037_section_given_a_dotted_heading_starts_at_the_dotted_heading_not_at_the_wildcard_match(tmp_path):
    fixture = tmp_path / "SKILL.md"
    fixture.write_text("### runXsh\nwrong\n### run.sh\nright\n### end\n")
    assert skill_sections.section(fixture, "### run.sh") == "### run.sh\nright\n"
