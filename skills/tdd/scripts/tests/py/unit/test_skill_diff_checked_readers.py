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
    "test_skill_leaf_launch.py": "parses the document's launch lines and runs the leaf-launch guard over them, the develop-diff and verdict-diff lines among them",
    "test_skill_leaf_env.py": "runs every launch line against a stub claude and checks what the leaf saw",
    "test_suite_reported_process.py": "runs suite-reported.sh, which the subsection calls",
    "test_build_develop_prompt_process.py": "runs build-develop-prompt.sh, which the subsection calls",
    "test_verify_process.py": "runs the verifier script the subsection calls",
    "test_prompt_test_tiers.py": "checks the tiers a rendered prompt names",
    "unit/test_build_develop_prompt.py": "unit cases of build-develop-prompt.sh",
    "unit/test_build_verify_prompt.py": "unit cases of build-verify-prompt.sh",
    "unit/test_ledger.py": "unit cases of the ledger helper",
    "unit/test_skill_verify_step.py": "no CY row: document-wide; verify.sh calls only",
    "unit/test_skill_stopping.py": "no CY row: document-wide stop-check cases",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_into_the_revise_loop_points_at_revise_md_1855":
        "no CY row: document-wide site list",
    "test_skill_leaf_env.py::test_907_the_revise_diff_prompt_line": "runs build-develop-prompt.sh revise diff from REVISE.md",
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
