"""Cases for which suites still read SKILL.md's `#### Red — one failing test (developer leaf), then verify-red (blind)` subsection by its content."""
import pathlib

import pytest

import subsection_readers

TESTS_PY = pathlib.Path(__file__).resolve().parent.parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
PREFIX = "#### Red"
HEADING = "#### Red — one failing test (developer leaf), then verify-red (blind)"

MARKERS = (
    HEADING, "red-prediction.md", "red-divergence.sh", "develop-replaces-report", "unreplaced-cases.sh",
)

ALLOWED = {
    "test_skill_leaf_launch.py": "runs the leaf-launch guard over the document's launch lines, Red's among them",
    "test_skill_leaf_env.py": "runs every launch line against a stub claude and checks what the leaf saw",
    "unit/test_skill_red_untestable.py::test_window_given_a_dotted_start_pattern_starts_at_the_dotted_line_not_at_the_wildcard_match":
        "tests heading_window on a scratch file; goes with the helper, not Red's prose",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_into_the_pin_points_at_pin_md_1852":
        "names the Red heading only to exclude it",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_into_the_revise_loop_points_at_revise_md_1855":
        "names the Red heading only to exclude it",
}


SPEC = subsection_readers.Subsection(HEADING, MARKERS, PREFIX)


def _subsection_and_rest():
    return subsection_readers.cut_subsection(SKILL_MD.read_text(encoding="utf-8"), HEADING)


def _readers(entry, subsection, rest):
    return subsection_readers.readers(entry, subsection, rest, SPEC)


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_red_subsection_by_its_content_is_on_the_mechanical_allow_list(tests_py_index):
    subsection, rest = _subsection_and_rest()
    stray = subsection_readers.stray_cases(tests_py_index, ALLOWED, SPEC, subsection, rest, TESTS_PY, __file__)
    assert stray == [], "cases read the Red subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
