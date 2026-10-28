"""What skills/tdd/SKILL.md tells a conductor to do with the run's hard timeout, read as text."""
import pathlib
import re

import skill_sections

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

def test_954_skill_md_makes_the_leaf_timeout_sh_call_that_records_tdd_issue_n_timeout_after_step_1_2_has_entered_the_issue_s_worktree_not_from_the_caller_s_checkout_where_preflight_runs():
    preflight = SKILL.with_name("PREFLIGHT.md").read_text().splitlines()
    lines = SKILL.read_text().splitlines()
    entered = next((i for i, l in enumerate(preflight, 1) if re.search(r'issue-worktree\.sh <n> .*cd "\$wt"', l)), None)
    recording = [i for i, l in enumerate(lines, 1) if re.search(r"VERI_ISSUE=<n>.*leaf-timeout\.sh", l)]
    early = [i for i, l in enumerate(preflight, 1) if re.search(r"VERI_ISSUE=<n>.*leaf-timeout\.sh", l)
             and (entered is None or i < entered)]
    assert entered is not None, "no PREFLIGHT.md line enters the worktree with issue-worktree.sh"
    assert recording, "no leaf-timeout.sh call in SKILL.md carries VERI_ISSUE=<n>, the one that records the settled timeout"
    assert not early, f"a leaf-timeout.sh call at PREFLIGHT.md line {early} runs before the worktree is entered (line {entered})"


def test_1037_section_given_a_dotted_heading_starts_at_the_dotted_heading_not_at_the_wildcard_match(tmp_path):
    fixture = tmp_path / "SKILL.md"
    fixture.write_text("### runXsh\nwrong\n### run.sh\nright\n### end\n")
    assert skill_sections.section(fixture, "### run.sh") == "### run.sh\nright\n"
