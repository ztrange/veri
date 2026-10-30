"""Cases for which suites still read SKILL.md's steps 1, 2, 2b and 2c by their content."""
import pathlib
import re
import warnings

import pytest

import skill_sections

TESTS_PY = pathlib.Path(__file__).resolve().parent.parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
HEADINGS = (
    "### 1. Read the issue, enter the issue's worktree, capture the spec (or resume)",
    "### 2. Scope & plan → the ledger",
    "### 2b. Start comment",
    "### 2c. Verify the plan (blind)",
)

ALLOWED = {
    "test_skill_timeout.py::test_954_skill_md_makes_the_leaf_timeout_sh_call_that_records_tdd_issue_n_timeout_after_step_1_2_has_entered_the_issue_s_worktree_not_from_the_caller_s_checkout_where_preflight_runs":
        "the line order of two SKILL.md lines",
    "test_skill_leaf_launch.py": "whole-file launch-line audits, the verdict-plan line included",
    "test_skill_leaf_env.py": "runs every SKILL.md launch line through supervise.sh against a stub",
    "test_affected_suites.py::test_on_the_real_skill_md_and_suites_a_one_section_edit_selects_the_suites_reading_that_section_through_a_slicing_helper_and_every_suite_reading_skill_md_any_other_way_and_not_a_suite_slicing_only_other_sections":
        "uses step 2c's heading as an edit target",
    "test_skill_inline_ledger_reads.py::test_skill_md_spells_none_of_the_inline_current_step_last_done_and_criterion_k_pipelines_reading_each_through_ledger_steps_sh_current_last_done_and_criterion_k":
        "a whole-file negative pattern audit",
    "test_skill_guard_subject_paragraph.py::test_skill_md_guard_subject_paragraph_names_a_pytest_guard_suite_and_conftest_and_says_the_path_is_matched_exactly_1775":
        "no PL row yet",
    "test_skill_suite_runs.py::test_1568_skill_md_runs_suite_reported_sh_develop_transform_after_the_refactor_kind_transform_leaf_and_before_its_blind_transform_verifier":
        "no PL row yet",
    "test_skill_refactor_kind.py::test_skill_md_says_a_diff_checked_step_in_a_refactor_kind_run_runs_develop_diff_then_verify_diff_and_never_cover_or_transform_1915":
        "carried by PL27; reads step 2's refactor-kind paragraph",
    "test_skill_draft_pr.py::test_worktree_step_no_longer_says_the_draft_pr_is_opened_once_every_step_is_green":
        "no PL row yet",
    "test_skill_preflight.py::test_skill_md_s_worktree_guard_prose_says_the_lock_is_taken_in_preflight_step_3_before_the_baseline_and_never_in_step_1_2":
        "carried by PF5; reads step 1's worktree guard paragraph for `preflight step 3`",
}


def _flat(text):
    return " ".join(skill_sections.plain_lower(text).split())


def _sections_and_rest():
    text = SKILL_MD.read_text(encoding="utf-8")
    inside = [skill_sections.section_of(text, heading, str(SKILL_MD)) for heading in HEADINGS]
    rest = text
    for block in inside:
        rest = rest.replace(block, "\n")
    return _flat("\n".join(inside)), _flat(rest)


def _only_in_sections(literal, inside, rest):
    """A literal a case could only have copied from steps 1, 2, 2b or 2c: a heading, or three or more
    words, as text or as a pattern, that those sections carry and no other part of SKILL.md does. Three
    matches test_skill_cost_check_readers.py's rule (#2114's review: four words let a three-word pin
    through). A one- or two-word literal reads as script vocabulary or a case's own label."""
    if literal in HEADINGS:
        return True
    flat = _flat(literal)
    if len(flat.split(" ")) < 3:
        return False
    if flat in inside and flat not in rest:
        return True
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pattern = re.compile(flat, re.I)
    except Exception:
        return False
    return bool(pattern.search(inside)) and not pattern.search(rest)


_STRING_ASSIGN = re.compile(r"(?:[A-Za-z_]\w*\s*=\s*)+[rRbBuU]{0,2}(\"|')[\s\S]*\1\Z")


def _readers(walk, inside, rest):
    definitions = walk.definitions
    defs = {d.name: d for d in definitions if d.segment.startswith("def ")}
    consts = {
        d.name: d.literals[0]
        for d in definitions
        if d.name not in defs and len(d.literals) == 1 and not d.names and _STRING_ASSIGN.match(d.segment)
    }

    def mentions_skill(fn, seen):
        if fn.name in seen:
            return False
        seen.add(fn.name)
        for name in fn.names:
            if name.startswith("SKILL") or name == "skill_sections":
                return True
            if name in defs and mentions_skill(defs[name], seen):
                return True
        return False

    def reads(fn, seen):
        if fn.name in seen:
            return False
        seen.add(fn.name)
        if any(name in consts and _only_in_sections(consts[name], inside, rest) for name in fn.names):
            return True
        if any(_only_in_sections(value, inside, rest) for value in fn.constants):
            return True
        return any(name in defs and reads(defs[name], seen) for name in fn.names)

    return [name for name, fn in defs.items() if name.startswith("test_") and reads(fn, set()) and mentions_skill(fn, set())]


@pytest.mark.tree_audit("every test module under tests/py, parsed for the cases that read SKILL.md's steps 1, 2, 2b and 2c")
def test_every_remaining_case_reading_skill_md_s_read_the_issue_scope_and_plan_start_comment_and_verify_the_plan_sections_by_content_is_a_mechanical_fact_case(tests_py_index):
    inside, rest = _sections_and_rest()
    strays = []
    for entry in tests_py_index:
        path = entry.path
        rel = str(path.relative_to(TESTS_PY))
        if path == pathlib.Path(__file__).resolve() or rel in ALLOWED or path.name in ALLOWED:
            continue
        if "SKILL" not in entry.text:
            continue
        for name in _readers(entry.walk, inside, rest):
            if f"{rel}::{name}" not in ALLOWED and f"{path.name}::{name}" not in ALLOWED:
                strays.append(f"{rel}::{name}")
    assert strays == [], "cases read steps 1, 2, 2b or 2c by content and are neither mechanical nor allow-listed:\n" + "\n".join(strays)
