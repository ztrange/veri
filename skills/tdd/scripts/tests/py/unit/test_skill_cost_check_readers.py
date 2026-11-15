"""Cases for which suites still read SKILL.md's `#### The step's cost check` subsection by its content."""
import pathlib

import pytest

import subsection_readers

TESTS_PY = pathlib.Path(__file__).resolve().parent.parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
HEADING = "#### The step's cost check"

MARKERS = (
    "The step's cost check", "cost check", "develop-over-budget", "step-over-budget",
    "over-budget-answer", "at=over-budget",
)

ALLOWED = {
    "test_skill_leaf_env.py": "runs the subsection's launch lines against a stub claude",
    "test_skill_event_marks.py::test_the_exit_3_case_still_names_a_mark_planted_in_the_exit_3_branch_by_its_line":
        "plants a mark in a copy of the subsection and checks the guard names it",
    "unit/test_skill_green_split.py::test_1281_skill_md_s_three_split_add_ledger_step_calls_pass_no_criterion_and_say_a_split_keeps_its_anchor_s_criterion_the_uncovered_spec_call_passes_criterion_k_read_from_the_issue_s_numbered_acceptance_criteria_one_call_per_criterion_bailing_on_exit_2":
        "reads the subsection's own instead-of add-ledger-step call, the one statement of the split",
    "unit/test_skill_green_split.py::test_1379_skill_md_s_every_add_ledger_step_sh_call_site_says_its_exit_2_bails_with_cause_step_add_refused":
        "carves the subsection out by its heading to read the other add-ledger-step call sites",
}


SPEC = subsection_readers.Subsection(HEADING, MARKERS)


def _subsection_and_rest():
    return subsection_readers.cut_subsection(SKILL_MD.read_text(encoding="utf-8"), HEADING)


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_cost_check_subsection_by_its_content_is_on_the_mechanical_allow_list(tests_py_index):
    subsection, rest = _subsection_and_rest()
    stray = subsection_readers.stray_cases(tests_py_index, ALLOWED, SPEC, subsection, rest, TESTS_PY, __file__)
    assert stray == [], "cases read the cost-check subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
