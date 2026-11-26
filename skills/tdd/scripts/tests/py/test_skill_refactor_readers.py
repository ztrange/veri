"""Cases for which suites still read SKILL.md's `#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)` subsection by its content."""
import pathlib
import re
import sys

import pytest

import subsection_readers

TESTS_PY = pathlib.Path(__file__).resolve().parent
SKILL_MD = TESTS_PY.parents[2] / "SKILL.md"
PREFIX = "#### Refactor loop"
HEADING = "#### Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"

MARKERS = (
    HEADING, ".tdd/develop-refactor.out", "refactor-triage.sh", "verify-refactor.log", "nothing left to tidy",
    "uncovered-spec", "beyond-spec", "overfit",
)

ALLOWED = {
    "unit/test_skill_refactor_footer.py::test_skill_md_refactor_section_names_exactly_the_report_lines_the_built_refactor_prompt_asks_the_leaf_for":
        "mechanical: two-sided RESULT:/CANDIDATES:/FLAGS: label parity with the built refactor prompt",
    "unit/test_skill_suite_runs.py::test_1300_skill_md_runs_suite_reported_sh_only_after_a_leaf_whose_prompt_asks_for_a_suite_line_never_after_the_refactor_leaf_or_a_revise_of_red_green_or_refactor":
        "absence assertion; the prose states nothing about it",
    "test_skill_leaf_env.py": "launch lines are Launching a leaf instances",
    "unit/test_refactor_half.py::test_4028_every_inner_call_in_the_ordered_list_is_a_script_the_refactor_loop_section_names":
        "mechanical: each `$S/<script>` refactor-half.py calls is named in the section (PRD 027 FC19), no wording read",
    "unit/test_step_close.py::test_4029_every_inner_call_in_the_ordered_list_is_a_script_the_refactor_loop_section_names":
        "mechanical: each `$S/<script>` step-close.py calls is named in the section (PRD 027 FC19), no wording read",
    "unit/test_skill_green_split.py::test_1281_skill_md_s_three_split_add_ledger_step_calls_pass_no_criterion_and_say_a_split_keeps_its_anchor_s_criterion_the_uncovered_spec_call_passes_criterion_k_read_from_the_issue_s_numbered_acceptance_criteria_one_call_per_criterion_bailing_on_exit_2":
        "mechanical: the one call after the pending-refactor step passes `--criterion <k>`, no wording read; "
        "its <k>, one-call-per-criterion and exit-2 prose is graded (RF29, RF31, CY363)",
}

# A heading named in any case, as a regex or a plain string: `(?i)^#{4}\s+refactor\s+loop`, `#### refactor loop`,
# `refactor loop`. Optional anchors, inline flags, `#` runs and whitespace may lead; `refactor` then `loop` must follow.
HEADING_IN_ANY_CASE = re.compile(
    r"(?:\(\?[a-zA-Z]+\)|\^|\\A|\\?#|\[#\]|\{\d+(?:,\d*)?\}|[+*?]|\s|\\s)*"
    r"refactor(?:\s|\\s|[+*.]|\[ \])+loop",
    re.I)


SPEC = subsection_readers.Subsection(
    HEADING, MARKERS, PREFIX, heading_in_any_case=HEADING_IN_ANY_CASE, path_literal=subsection_readers.SKILL_PATH_LITERAL)


def _subsection_and_rest():
    return subsection_readers.cut_subsection(SKILL_MD.read_text(encoding="utf-8"), HEADING)


def _other_docs():
    return subsection_readers.other_docs(SKILL_MD)


def _readers(entry, subsection, rest, docs):
    return subsection_readers.readers(entry, subsection, rest, SPEC, docs)


def stray_cases(entries, allowed):
    subsection, rest = _subsection_and_rest()
    return subsection_readers.stray_cases(entries, allowed, SPEC, subsection, rest, TESTS_PY, __file__, _other_docs())


def lost_cases(entries, allowed):
    subsection, rest = _subsection_and_rest()
    return subsection_readers.lost_cases(entries, allowed, SPEC, subsection, rest, TESTS_PY, __file__, _other_docs())


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_every_remaining_case_reading_the_refactor_loop_subsection_by_its_content_is_on_the_mechanical_allow_list(tests_py_index):
    stray = stray_cases(tests_py_index, ALLOWED)
    assert stray == [], "cases read the Refactor loop subsection by content and are neither mechanical nor allow-listed:\n" + "\n".join(stray)
    lost = lost_cases(tests_py_index, ALLOWED)
    assert lost == [], "allow-listed entries no longer read the Refactor loop subsection:\n" + "\n".join(lost)


def test_2220_sweep_flags_a_case_reading_the_refactor_loop_subsection_until_it_is_on_the_allow_list(tmp_path, monkeypatch):
    from conftest import TestFile
    module = tmp_path / "test_synthetic_reader.py"
    module.write_text(
        'SKILL_MD = "SKILL.md"\n\n\n'
        'def test_reads_the_triage_step():\n'
        '    assert "refactor-triage.sh" in SKILL_MD\n',
        encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "TESTS_PY", tmp_path)
    monkeypatch.setattr(sys.modules[__name__], "_other_docs", dict)
    entries = [TestFile(module)]
    key = "test_synthetic_reader.py::test_reads_the_triage_step"

    assert stray_cases(entries, {}) == [key]
    assert stray_cases(entries, {key: "mechanical: synthetic"}) == []
