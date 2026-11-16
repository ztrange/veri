"""Cases for which suites still read SKILL.md's `#### A ⟦diff-checked⟧ step — develop-diff, then verify-diff (blind)` subsection by its content."""
import pathlib

import pytest

import subsection_readers

TESTS_PY = pathlib.Path(__file__).resolve().parent.parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
PREFIX = "#### A `⟦diff-checked⟧` step"
HEADING = "#### A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)"

MARKERS = (
    HEADING, "verdict-diff", "<step-base-sha>", "revise-diff-<k>",
    "git log -1 --format=%H -- .tdd/issue-<n>.md",
)

ALLOWED = {
}


SPEC = subsection_readers.Subsection(HEADING, MARKERS, PREFIX)


def _subsection_and_rest():
    return subsection_readers.cut_subsection(SKILL_MD.read_text(encoding="utf-8"), HEADING)


def _other_docs():
    return subsection_readers.other_docs(SKILL_MD)


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_diff_checked_subsection_by_its_content_is_on_the_mechanical_allow_list(tests_py_index):
    subsection, rest = _subsection_and_rest()
    stray = subsection_readers.stray_cases(tests_py_index, ALLOWED, SPEC, subsection, rest, TESTS_PY, __file__, _other_docs())
    assert stray == [], "cases read the diff-checked subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
    lost = subsection_readers.lost_cases(tests_py_index, ALLOWED, SPEC, subsection, rest, TESTS_PY, __file__, _other_docs())
    assert lost == [], "allow-listed entries no longer read the diff-checked subsection:\n" + "\n".join(lost)
