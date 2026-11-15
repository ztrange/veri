"""Cases for which suites still read SKILL.md's `#### A ⟦phases: …⟧ step — each listed phase, a developer leaf then a blind verifier` subsection by its content."""
import pathlib
import re
import sys

import pytest

import subsection_readers

TESTS_PY = pathlib.Path(__file__).resolve().parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
PHASED_MD = SKILL_MD.with_name("PHASED.md")
PREFIX = "#### A `⟦phases: …⟧` step"
HEADING = "#### A `⟦phases: …⟧` step — each listed phase, a developer leaf then a blind verifier"

MARKERS = (
    "next-phase", "--phase-owed", "--phase <phase>", "production-frozen.sh", "no-product-caller.sh",
)

ALLOWED = {
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_into_the_revise_loop_points_at_revise_md_1855":
        "document-wide site list",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_into_the_pin_points_at_pin_md_1852":
        "document-wide site list",
    "unit/test_skill_event_files.py::test_every_line_sending_the_run_to_stopping_points_at_stopping_md_1716":
        "document-wide site list",
    "unit/test_skill_event_files.py::test_the_guard_reports_no_misplaced_bail_pointer_in_the_real_skill_md_2075":
        "document-wide site list",
    "unit/test_skill_event_files.py::test_the_guard_reports_no_unpointed_send_in_the_real_skill_md_2075":
        "document-wide site list",
    "unit/test_skill_event_files.py::test_the_send_scoped_placement_check_finds_no_misplaced_pointer_in_skill_md_or_any_event_file_2339":
        "document-wide site list",
    "test_skill_leaf_launch.py": "launch lines are Launching a leaf instances",
    "test_skill_leaf_env.py": "launch lines are Launching a leaf instances",
    "test_ledger_steps.py": "script suite", "test_tick_ledger.py": "script suite", "test_next_unchecked.py": "script suite",
    "test_transform_touches_tests.py": "script suite", "test_production_frozen_process.py": "script suite",
    "test_no_product_caller_process.py": "script suite", "test_tests_frozen_process.py": "script suite",
    "test_suite_reported_process.py": "script suite", "test_prompt_test_tiers.py": "script suite",
    "test_build_develop_prompt.py": "script suite", "test_build_verify_prompt.py": "script suite",
    "unit/test_metrics.py": "the phases fixtures",
}


SPEC = subsection_readers.Subsection(HEADING, MARKERS, PREFIX)


def _subsection_and_rest():
    return subsection_readers.flat(PHASED_MD.read_text(encoding="utf-8")), subsection_readers.flat(SKILL_MD.read_text(encoding="utf-8"))


def _other_docs():
    return subsection_readers.other_docs(SKILL_MD, exclude=(PHASED_MD,))


def _readers(entry, subsection, rest, docs):
    return subsection_readers.readers(entry, subsection, rest, SPEC, docs)


def stray_cases(entries, allowed):
    subsection, rest = _subsection_and_rest()
    return subsection_readers.stray_cases(entries, allowed, SPEC, subsection, rest, TESTS_PY, __file__, _other_docs())


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_phases_step_subsection_by_its_content_is_on_the_mechanical_allow_list(tests_py_index):
    stray = stray_cases(tests_py_index, ALLOWED)
    assert stray == [], "cases read the phased-step subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)


def test_2220_sweep_flags_a_case_reading_the_phases_step_subsection_until_it_is_on_the_allow_list(tmp_path, monkeypatch):
    from conftest import TestFile
    module = tmp_path / "test_synthetic_reader.py"
    module.write_text(
        'SKILL_MD = "SKILL.md"\n\n\n'
        'def test_reads_the_phases_step():\n'
        '    assert "--phase-owed" in SKILL_MD\n',
        encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "TESTS_PY", tmp_path)
    monkeypatch.setattr(sys.modules[__name__], "_other_docs", dict)
    entries = [TestFile(module)]
    key = "test_synthetic_reader.py::test_reads_the_phases_step"

    assert stray_cases(entries, {}) == [key]
    assert stray_cases(entries, {key: "mechanical: synthetic"}) == []
