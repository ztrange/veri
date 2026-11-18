"""Cases for which suites still read DRAFT-PR.md's `## 4. Draft PR` section by its content."""
import pathlib

import pytest

import subsection_readers

TESTS_PY = pathlib.Path(__file__).resolve().parent.parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
DRAFT_PR_MD = SKILL_MD.with_name("DRAFT-PR.md")
PREFIX = "## 4. Draft"
HEADING = "## 4. Draft PR"

MARKERS = (HEADING, "gh_pr_ready", "rebased-tip-red")

ALLOWED = {
    "unit/test_skill_draft_pr.py::test_draft_prs_step_readies_the_pr_against_the_already_pushed_branch_with_no_push_of_its_own":
        "absence: no line of the unit runs git push",
    "test_affected_suites_process.py::test_a_one_section_edit_to_the_real_skill_md_selects_the_pytest_files_that_read_that_section_2980":
        "locates the SKILL.md heading line to aim a one-section diff",
}


SPEC = subsection_readers.Subsection(
    HEADING, MARKERS, PREFIX, source_names=subsection_readers.SKILL_NAMES + r"|DRAFT_PR(?:_MD)?", gate=("SKILL", "DRAFT_PR_MD"))


def _section_and_rest():
    return subsection_readers.flat(DRAFT_PR_MD.read_text(encoding="utf-8")), subsection_readers.flat(SKILL_MD.read_text(encoding="utf-8"))


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_draft_pr_section_by_its_content_is_a_kept_mechanical_case(tests_py_index):
    section, rest = _section_and_rest()
    stray = subsection_readers.stray_cases(tests_py_index, ALLOWED, SPEC, section, rest, TESTS_PY, __file__)
    assert stray == [], "cases read the Draft PR section by content and are neither kept nor allow-listed:\n" + "\n".join(stray)
    lost = subsection_readers.lost_cases(tests_py_index, ALLOWED, SPEC, section, rest, TESTS_PY, __file__)
    assert lost == [], "allow-listed entries no longer read the Draft PR subsection:\n" + "\n".join(lost)
