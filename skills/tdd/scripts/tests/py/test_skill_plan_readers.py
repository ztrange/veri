"""Cases for which suites still read SKILL.md's steps 1, 2, 2b and 2c by their content."""
import ast
import pathlib
import warnings

import pytest

import skill_sections

TESTS_PY = pathlib.Path(__file__).resolve().parent
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
    "test_skill_draft_pr.py::test_worktree_step_no_longer_says_the_draft_pr_is_opened_once_every_step_is_green":
        "no PL row yet",
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
    if literal in HEADINGS:
        return True
    flat = _flat(literal)
    if len(flat.split(" ")) < 4:
        return False
    if flat in inside and flat not in rest:
        return True
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import re
            pattern = re.compile(flat, re.I)
    except Exception:
        return False
    return bool(pattern.search(inside)) and not pattern.search(rest)


def _skipped(fn):
    skip = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Assert) and node.msg is not None:
            skip.update(id(n) for n in ast.walk(node.msg))
        if isinstance(node, ast.JoinedStr):
            skip.update(id(n) for n in ast.walk(node))
    return skip


def _readers(tree, inside, rest):
    defs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    consts = {
        target.id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
        for target in node.targets if isinstance(target, ast.Name)
    }

    def mentions_skill(fn, seen):
        if fn.name in seen:
            return False
        seen.add(fn.name)
        for node in ast.walk(fn):
            if isinstance(node, ast.Name) and (node.id.startswith("SKILL") or node.id == "skill_sections"):
                return True
            if isinstance(node, ast.Name) and node.id in defs and mentions_skill(defs[node.id], seen):
                return True
        return False

    def reads(fn, seen):
        if fn.name in seen:
            return False
        seen.add(fn.name)
        skip = _skipped(fn)
        for node in ast.walk(fn):
            if isinstance(node, ast.Name) and node.id in consts and _only_in_sections(consts[node.id], inside, rest):
                return True
            if (isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in skip
                    and _only_in_sections(node.value, inside, rest)):
                return True
            if isinstance(node, ast.Name) and node.id in defs and reads(defs[node.id], seen):
                return True
        return False

    return [name for name, fn in defs.items() if name.startswith("test_") and reads(fn, set()) and mentions_skill(fn, set())]


@pytest.mark.tree_audit("every test module under tests/py, parsed for the cases that read SKILL.md's steps 1, 2, 2b and 2c")
def test_every_remaining_case_reading_skill_md_s_read_the_issue_scope_and_plan_start_comment_and_verify_the_plan_sections_by_content_is_a_mechanical_fact_case():
    inside, rest = _sections_and_rest()
    strays = []
    for path in sorted(TESTS_PY.rglob("test_*.py")):
        rel = str(path.relative_to(TESTS_PY))
        if path == pathlib.Path(__file__).resolve() or rel in ALLOWED or path.name in ALLOWED:
            continue
        source = path.read_text(encoding="utf-8")
        if "SKILL" not in source:
            continue
        for name in _readers(ast.parse(source), inside, rest):
            if f"{rel}::{name}" not in ALLOWED and f"{path.name}::{name}" not in ALLOWED:
                strays.append(f"{rel}::{name}")
    assert strays == [], "cases read steps 1, 2, 2b or 2c by content and are neither mechanical nor allow-listed:\n" + "\n".join(strays)
