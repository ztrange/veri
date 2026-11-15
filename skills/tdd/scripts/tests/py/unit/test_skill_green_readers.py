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
    "test_skill_leaf_launch.py": "parses the document's launch lines and runs the leaf-launch guard over them, Green's among them",
    "test_skill_leaf_env.py": "runs every launch line against a stub claude and checks what the leaf saw",
    "unit/test_skill_suite_runs.py::test_698_case_1_passes_on_a_skill_md_whose_green_section_and_refactor_loop_name_no_full_suite_run":
        "mutates a fixture copy and checks the helper; asserts nothing about Green's text",
    "unit/test_skill_suite_runs.py::test_991_doc_text_given_the_from_regex_5_starts_at_the_line_5_y_not_at_5x_y":
        "tests the doc_text helper on a scratch file",
    "unit/test_skill_tests_frozen.py::test_green_and_revising_handle_check_exit_2_as_a_system_failure_bail_never_a_reject":
        "asserts REVISE.md's sentence, not Green's",
    "unit/test_skill_tests_frozen.py::test_revising_routes_a_revise_green_wrong_test_report_through_wrong_test_route_never_a_report_missing_bail":
        "asserts REVISE.md's sentence, not Green's",
    "unit/test_skill_refactor_kind.py::test_skill_md_puts_mutation_parity_sh_s_report_into_the_pr_body_as_the_pairs_table_and_each_row_it_reports_owed_under_owed_by_a_human":
        "no CY row: document-wide; searches every mutation-parity.sh in the document",
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
    "unit/test_skill_tests_frozen.py::test_every_tests_frozen_record_and_check_names_the_record_by_path_over_the_step_text_and_red_defines_the_key":
        "names the Green heading only to exclude it",
    "unit/test_skill_tests_frozen.py::test_every_reroute_re_record_in_green_passes_the_steps_own_red_case_and_routes_its_refusal_to_verify_red_reason":
        "asserts the Green subsection's reroute re-record commands and their --red-case refusal routing (CY120)",
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
