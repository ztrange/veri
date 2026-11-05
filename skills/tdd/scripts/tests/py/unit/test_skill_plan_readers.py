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
    "test_skill_timeout.py::test_2966_skill_md_step_1_6_places_the_claim_before_preflight_s_baseline_and_its_full_suite_lock_wait":
        "no PL row yet",
    "test_skill_timeout.py::test_954_skill_md_makes_the_leaf_timeout_sh_call_that_records_tdd_issue_n_timeout_after_step_1_2_has_entered_the_issue_s_worktree_not_from_the_caller_s_checkout_where_preflight_runs":
        "the line order of two SKILL.md lines",
    "test_skill_leaf_launch.py": "whole-file launch-line audits, the verdict-plan line included",
    "test_skill_leaf_env.py": "runs every SKILL.md launch line through supervise.sh against a stub",
    "test_skill_inline_ledger_reads.py::test_skill_md_spells_none_of_the_inline_current_step_last_done_and_criterion_k_pipelines_reading_each_through_ledger_steps_sh_current_last_done_and_criterion_k":
        "a whole-file negative pattern audit",
    "test_skill_guard_subject_paragraph.py::test_skill_md_guard_subject_paragraph_names_a_pytest_guard_suite_and_conftest_and_says_the_path_is_matched_exactly_1775":
        "no PL row yet",
    "test_skill_suite_runs.py::test_1568_skill_md_runs_suite_reported_sh_develop_transform_after_the_refactor_kind_transform_leaf_and_before_its_blind_transform_verifier":
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


ALLOW_LIST_HOLDERS = (
    ("test_skill_phased_readers.py", "ALLOWED"),
    ("test_skill_refactor_readers.py", "ALLOWED"),
    ("unit/test_skill_plan_readers.py", "ALLOWED"),
    ("unit/test_skill_draft_pr_readers.py", "ALLOWED"),
    ("test_skill_preflight.py", "MECHANICAL_READERS"),
)


def _allow_list_keys(path, variable):
    import ast

    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == variable for t in node.targets):
            value = ast.literal_eval(node.value)
            return list(value)
    raise AssertionError(f"{path} assigns no {variable}")


@pytest.mark.tree_audit("every test module under tests/py, searched for each allow-list entry's case")
def test_every_entry_of_the_reader_allow_lists_names_a_case_that_exists(tests_py_index):
    entries = {str(e.path.relative_to(TESTS_PY)): e.text for e in tests_py_index}
    case_names = [d.name for e in tests_py_index for d in e.walk.definitions if d.segment.startswith("def test_")]
    missing = []
    for holder, variable in ALLOW_LIST_HOLDERS:
        for key in _allow_list_keys(TESTS_PY / holder, variable):
            file_part, sep, case = key.partition("::")
            if sep:
                texts = [t for rel, t in entries.items() if file_part in (rel, rel.rsplit("/", 1)[-1])]
                found = any(f"def {case.rstrip('….')}" in t for t in texts)
            elif file_part.endswith(".py"):
                found = any(file_part in (rel, rel.rsplit("/", 1)[-1]) for rel in entries)
            else:
                found = any(file_part in name for name in case_names)
            if not found:
                missing.append(f"{holder}: {key}")
    assert missing == [], "allow-list entries naming no existing case:\n" + "\n".join(missing)
