"""Cases for which suites still read SKILL.md's `#### Green — minimum implementation (developer leaf), then verify-green (blind)` subsection by its content."""
import pathlib

import pytest

import subsection_readers

TESTS_PY = pathlib.Path(__file__).resolve().parent.parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
PREFIX = "#### Green"
HEADING = "#### Green — minimum implementation (developer leaf), then verify-green (blind)"

MARKERS = (
    HEADING, "wrong-test-route.sh", "red-contradicted", "red-supersede",
)

ALLOWED = {
    "unit/test_skill_green_split.py::test_1558_skill_md_runs_every_replaces_case_survivors_sh_occurrence_before_the_verify_green_launch_it_gates_on_the_green_path_and_the_pin_path_alike":
        "no CY row: document-wide; orders the first survivors run against the verify-green launch line",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_to_stopping_points_at_stopping_md_1716":
        "names the Green heading only to exclude it",
    "unit/test_skill_event_files.py::test_every_line_launching_the_reconcile_leaf_points_at_reconcile_md_1716":
        "names the Green heading only to exclude it",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_into_the_revise_loop_points_at_revise_md_1855":
        "names the Green heading only to exclude it",
    "unit/test_skill_green_superseded.py::test_2254_a_green_report_naming_a_superseded_case_alone_goes_through_wrong_test_route_to_a_free_red_contradicted_reroute":
        "asserts the Green subsection's SUPERSEDED: routing text",
    "unit/test_skill_diff_checked_readers.py::test_every_remaining_case_reading_the_diff_checked_subsection_by_its_content_is_on_the_mechanical_allow_list":
        "mechanical: the sibling audit's own MARKERS and heading literals, asserting nothing about Green's text",
}


SPEC = subsection_readers.Subsection(HEADING, MARKERS, PREFIX)


def _subsection_and_rest():
    return subsection_readers.cut_subsection(SKILL_MD.read_text(encoding="utf-8"), HEADING)


def _readers(entry, subsection, rest):
    return subsection_readers.readers(entry, subsection, rest, SPEC)


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_green_subsection_by_its_content_is_on_the_mechanical_allow_list(tests_py_index):
    subsection, rest = _subsection_and_rest()
    stray = subsection_readers.stray_cases(tests_py_index, ALLOWED, SPEC, subsection, rest, TESTS_PY, __file__)
    assert stray == [], "cases read the Green subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
    lost = subsection_readers.lost_cases(tests_py_index, ALLOWED, SPEC, subsection, rest, TESTS_PY, __file__)
    assert lost == [], "allow-listed entries no longer read the Green subsection:\n" + "\n".join(lost)
