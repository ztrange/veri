"""Cases for which suites still read SKILL.md's `#### The step's cost check` subsection by its content."""
import ast
import pathlib
import re

import pytest

TESTS_PY = pathlib.Path(__file__).resolve().parent

MARKERS = (
    "The step's cost check", "cost check", "develop-over-budget", "step-over-budget",
    "over-budget-answer", "at=over-budget",
)

ALLOWED = {
    "test_skill_leaf_env.py": "runs the subsection's launch lines against a stub claude",
    "test_skill_event_marks.py::test_the_exit_3_case_still_names_a_mark_planted_in_the_exit_3_branch_by_its_line":
        "plants a mark in a copy of the subsection and checks the guard names it",
    "unit/test_skill_green_split.py::test_1281_skill_md_s_three_split_add_ledger_step_calls_pass_no_criterion_and_say_a_split_keeps_its_anchor_s_criterion_the_uncovered_spec_call_passes_criterion_k_read_from_the_issue_s_numbered_acceptance_criteria_one_call_per_criterion_bailing_on_exit_2":
        "carves the subsection out by its heading to read the other add-ledger-step call sites",
    "unit/test_skill_green_split.py::test_1379_skill_md_s_every_add_ledger_step_sh_call_site_says_its_exit_2_bails_with_cause_step_add_refused_and_bailing_lists_that_cause_as_a_system_failure":
        "carves the subsection out by its heading to read the other add-ledger-step call sites",
}


def _readers(path):
    text = path.read_text(encoding="utf-8")
    if "SKILL" not in text:
        return []
    tree = ast.parse(text)
    own = [
        n for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.Assign))
    ]
    segments = {}
    for node in own:
        if isinstance(node, ast.FunctionDef):
            segments[node.name] = ast.get_source_segment(text, node)
        else:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    segments[target.id] = ast.get_source_segment(text, node.value)
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
        return "\n".join(segments[n] for n in seen)

    return sorted(
        name for name in segments
        if name.startswith("test_")
        and any(m in reach(name) for m in MARKERS)
        and re.search(r"\bSKILL\b|skill_lines|skill_sections", reach(name))
    )


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_cost_check_subsection_by_its_content_is_on_the_mechanical_allow_list():
    stray = []
    for path in sorted(TESTS_PY.rglob("test_*.py")):
        if path == pathlib.Path(__file__).resolve():
            continue
        rel = str(path.relative_to(TESTS_PY))
        if rel in ALLOWED:
            continue
        stray += [f"{rel}::{name}" for name in _readers(path) if f"{rel}::{name}" not in ALLOWED
                  and f"{path.name}::{name}" not in ALLOWED]
    assert stray == [], "cases read the cost-check subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
