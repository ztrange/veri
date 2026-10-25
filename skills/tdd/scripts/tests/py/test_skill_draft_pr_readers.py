"""Cases for which suites still read SKILL.md's `### 4. Draft PR` section by its content."""
import pathlib
import re

import pytest

TESTS_PY = pathlib.Path(__file__).resolve().parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
PREFIX = "### 4. Draft"
HEADING = "### 4. Draft PR"

MARKERS = (HEADING, "gh_pr_ready", "rebased-tip-red")

ALLOWED = {
    "test_skill_ci_conflict.py::test_a_green_ci_wait_in_either_ci_block_bails_no_ci_red_and_appends_no_ci_repair_step_with_or_without_one_in_the_ledger":
        "runs both CI blocks under bash against stubs",
    "test_skill_ci_conflict.py::test_the_block_run_after_the_metrics_push_bails_nothing_on_a_conflict_the_first_time_and_ci_conflict_once_the_marker_exists":
        "runs the post-metrics-push block under bash against stubs",
    "test_skill_leaf_env.py::test_753_the_structural_pass_in_skill_md_spells_the_transform_verifiers_launch_line_and_run_with_every_ledger_step_ticked_it_hands_its_verifier_the_last_done_steps_text_as_step_byte_identical":
        "runs the unit's launch lines against a stub ledger",
    "unit/test_skill_criterion_finished.py::test_495_every_instruction_that_names_the_last_ticked_step_reads_it_from_ledger_steps_records_spelling_no_checkbox_pattern":
        "whole-document audit of ledger reads",
    "unit/test_skill_draft_pr.py::test_draft_prs_step_readies_the_pr_against_the_already_pushed_branch_with_no_push_of_its_own":
        "absence: no line of the unit runs git push",
    "unit/test_skill_draft_pr.py::test_skill_md_reaches_the_default_branch_the_issue_and_the_pr_through_the_helper_or_gh_api_never_gh_repo_issue_pr":
        "whole-document ban on gh repo/issue/pr subcommands",
    "unit/test_skill_draft_pr.py::test_bailing_cause_token_list_names_rebased_tip_red_and_classifies_it_as_a_process_failure":
        "reads BAIL.md, another unit",
    "unit/test_skill_draft_pr.py::test_guardrails_invariant_about_opening_the_pr_names_the_branchs_own_full_run_again_after_each_suite_repair_step_and_the_extra_run_on_the_rebased_tip_when_sub_step_1_rebased_the_branch":
        "reads the Guardrails, another unit",
    "unit/test_skill_metrics.py::test_566_skill_md_bailing_sub_step_4_makes_the_metrics_commit_only_on_a_metrics_sh_exit_of_0_and_otherwise_the_bailed_comment_carries_the_failed_render_and_its_exit_code":
        "reads BAIL.md, another unit",
    "unit/test_skill_metrics.py::test_566_skill_md_bailing_sub_step_4_on_a_non_zero_metrics_sh_exit_does_not_stop_the_bail_it_goes_on_to_sub_step_5_push_and_sub_step_6_bailed_comment":
        "reads BAIL.md, another unit",
    "unit/test_skill_metrics.py::test_626_skill_md_bailing_section_marks_the_bail_with_its_cause_and_classification_before_rendering_the_metrics_report_it_commits":
        "reads BAIL.md, another unit",
    "unit/test_skill_metrics.py::test_626_skill_md_bailing_section_writes_the_bail_mark_before_rendering_the_metrics_report_it_commits":
        "reads BAIL.md, another unit",
    "unit/test_skill_suite_runs.py::test_skill_md_names_no_full_suite_run_inside_a_step_s_cycle":
        "reads the Refactor loop, another unit",
}


def _flat(text):
    return " ".join(text.split())


def _section_and_rest():
    text = SKILL_MD.read_text(encoding="utf-8")
    start = text.index(HEADING)
    following = re.search(r"^#{1,3} ", text[start + len(HEADING):], re.M)
    stop = start + len(HEADING) + following.start() if following else len(text)
    return _flat(text[start:stop]), _flat(text[:start] + "\n" + text[stop:])


def _names_the_heading(literal):
    return literal.startswith(PREFIX) and HEADING.startswith(literal)


def _only_in_section(literal, section, rest):
    flat = _flat(literal)
    return len(flat.split(" ")) >= 3 and flat in section and flat not in rest


def _readers(entry, section, rest):
    text = entry.text
    if "SKILL" not in text:
        return []
    definitions = entry.walk.definitions
    segments = {d.name: d.segment for d in definitions}
    literals = {d.name: d.strings for d in definitions}
    reads = {d.name: set(d.names) for d in definitions}
    calls = {
        name: {o for o in segments if o != name and re.search(r"\b%s\b" % re.escape(o), src)}
        for name, src in segments.items()
    }

    def reach(name):
        seen, todo = {name}, [name]
        while todo:
            for other in calls[todo.pop()] - seen:
                seen.add(other)
                todo.append(other)
        return seen

    def reads_the_section(names):
        source = "\n".join(segments[n] for n in names)
        return any(m in source for m in MARKERS) or any(
            _names_the_heading(s) or _only_in_section(s, section, rest) for n in names for s in literals[n])

    return sorted(
        name for name in segments
        if name.startswith("test_")
        and reads_the_section(reach(name))
        and any(re.fullmatch(r"SKILL(?:_MD)?|skill_lines", i) for n in reach(name) for i in reads[n])
    )


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_draft_pr_section_by_its_content_is_a_kept_mechanical_case(tests_py_index):
    section, rest = _section_and_rest()
    stray = []
    for entry in tests_py_index:
        path = entry.path
        if path == pathlib.Path(__file__).resolve():
            continue
        rel = str(path.relative_to(TESTS_PY))
        if rel in ALLOWED:
            continue
        stray += [f"{rel}::{name}" for name in _readers(entry, section, rest) if f"{rel}::{name}" not in ALLOWED]
    assert stray == [], "cases read the Draft PR section by content and are neither kept nor allow-listed:\n" + "\n".join(stray)
