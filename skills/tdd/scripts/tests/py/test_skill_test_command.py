"""What skills/tdd/SKILL.md tells the conductor about the run's test command, read as text."""
import pathlib
import re

import skill_sections

SKILL = pathlib.Path(__file__).resolve().parents[2].parent / "SKILL.md"

PREFLIGHT = "### 0. Preflight — baseline checks (bail before any cycle)"
DETECTING = "## Detecting the test command"
PLAN = "### 2. Scope & plan → the ledger"


def at(text, pattern):
    return next((n for n, line in enumerate(text.splitlines(), 1) if re.search(pattern, line)), None)


def items(text):
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
        elif rec:
            rec = rec + " " + line
    if rec:
        records.append(rec)
    return [r.lower() for r in records]


def test_skill_md_detects_the_run_s_test_command_from_the_issue_body_in_preflight_gives_it_to_every_leaf_and_names_it_in_the_plan_comment():
    pre = skill_sections.section(SKILL, PREFLIGHT)
    detect_at = at(pre, r"detect-test-command\.sh")
    body_at = at(pre, r"gh api repos/[{]owner[}]/[{]repo[}]/issues/<n> -q [.]body")
    assert detect_at is not None, "preflight never names detect-test-command.sh, so the baseline runs a command from nowhere"
    detect_line = pre.splitlines()[detect_at - 1]
    assert "--issue" in detect_line, f"preflight detects the test command without --issue, so the issue's own line cannot answer: {detect_line}"
    assert body_at is not None, "preflight never reads the issue body (no gh api read of issues/<n>), so there is no body file to pass as --issue"
    assert body_at < detect_at, f"preflight reads the issue body at line {body_at}, after detecting the test command at line {detect_at}"

    detecting = skill_sections.section(SKILL, DETECTING)
    assert at(detecting, "--issue") is not None, "'Detecting the test command' never names --issue, so <test-cmd> is detected without the issue's line"

    plan_items = [r for r in items(skill_sections.section(SKILL, PLAN)) if re.search("plan.*comment", r)]
    assert plan_items, "'Scope & plan' has no numbered item posting the plan comment"
    assert re.search("test command", plan_items[0]), f"the plan-comment item never names the test command: {plan_items[0][:120]}"


def test_skill_md_s_preflight_baseline_runs_and_times_detect_test_command_sh_tier_fast_s_command():
    baseline = [r for r in items(skill_sections.section(SKILL, PREFLIGHT)) if "baseline" in r and re.search("time it", r)]
    assert baseline, "preflight has no numbered item that runs and times the baseline"
    assert re.search(r"detect-test-command\.sh --tier fast", baseline[0]), \
        f"the baseline item never runs detect-test-command.sh --tier fast: {baseline[0][:120]}"


def test_1037_section_given_a_dotted_heading_starts_at_the_dotted_heading_not_at_the_wildcard_match(tmp_path):
    fixture = tmp_path / "SKILL.md"
    fixture.write_text("### runXsh\nwrong\n### run.sh\nright\n### end\n")
    assert skill_sections.section(fixture, "### run.sh") == "### run.sh\nright\n"
