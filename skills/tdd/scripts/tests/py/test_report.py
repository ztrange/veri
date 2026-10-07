"""In-process cases for veri/report.py, the reader of KEY: value lines off a leaf report."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture
def report():
    return importlib.import_module("veri.report")


def test_report_read_keeps_each_keys_last_value_omits_an_unseen_key_and_matches_only_key_colon_space_at_column_0_first_key_first(report):
    answers = {
        "last wins": report.report_read("COVERED: no\nCOVERED: yes\n", ("COVERED", "PROOF")),
        "near misses": report.report_read(" COVERED: yes\n\tCOVERED: yes\nCOVERED:yes\ncovered: yes\n", ("COVERED",)),
        "two spaces": report.report_read("COVERED:  yes\n", ("COVERED",)),
        "first key first": report.report_read("PROOF: NONE: no caller\n", ("PROOF: NONE", "PROOF")),
        "first key first, reversed": report.report_read("PROOF: NONE: no caller\n", ("PROOF", "PROOF: NONE")),
    }

    assert answers == {
        "last wins": {"COVERED": "yes"},
        "near misses": {},
        "two spaces": {"COVERED": " yes"},
        "first key first": {"PROOF: NONE": "no caller"},
        "first key first, reversed": {"PROOF": "NONE: no caller"},
    }


def test_report_read_splits_on_newline_only_keeps_a_carriage_return_reads_an_unterminated_last_line_and_answers_an_empty_text_with_an_empty_dict(report):
    answers = {
        "crlf": report.report_read("COVERED: yes\r\n", ("COVERED",)),
        "vertical tab": report.report_read("COVERED: a\vPROOF: b\n", ("COVERED", "PROOF")),
        "form feed": report.report_read("COVERED: a\fPROOF: b\n", ("COVERED", "PROOF")),
        "file separator": report.report_read("COVERED: a\x1cPROOF: b\n", ("COVERED", "PROOF")),
        "next line": report.report_read("COVERED: a\x85PROOF: b\n", ("COVERED", "PROOF")),
        "line separator": report.report_read("COVERED: a\u2028PROOF: b\n", ("COVERED", "PROOF")),
        "unterminated": report.report_read("MUTATION: x\nCOVERED: yes", ("COVERED",)),
        "empty": report.report_read("", ("COVERED",)),
    }

    assert answers == {
        "crlf": {"COVERED": "yes\r"},
        "vertical tab": {"COVERED": "a\vPROOF: b"},
        "form feed": {"COVERED": "a\fPROOF: b"},
        "file separator": {"COVERED": "a\x1cPROOF: b"},
        "next line": {"COVERED": "a\x85PROOF: b"},
        "line separator": {"COVERED": "a\u2028PROOF: b"},
        "unterminated": {"COVERED": "yes"},
        "empty": {},
    }


def test_report_read_drops_nul_bytes_before_parsing_so_a_nul_in_a_value_or_a_key_reads_as_if_absent_issue_1089(report):
    answers = report.report_read("CAUGHT_BY: a\0b\nCOV\0ERED: y\0es\n", ("COVERED", "CAUGHT_BY"))

    assert answers == {"CAUGHT_BY": "ab", "COVERED": "yes"}


def test_report_read_with_optional_space_matches_key_colon_with_or_without_a_space_and_removes_at_most_one_and_the_option_is_keyword_only_and_off_by_default(report):
    answers = {
        "no space": report.report_read("PREDICATE:x\n", ("PREDICATE",), optional_space=True),
        "one space": report.report_read("PREDICATE: x\n", ("PREDICATE",), optional_space=True),
        "two spaces": report.report_read("PREDICATE:  x\n", ("PREDICATE",), optional_space=True),
        "default, no space": report.report_read("PREDICATE:x\n", ("PREDICATE",)),
    }

    assert answers == {
        "no space": {"PREDICATE": "x"},
        "one space": {"PREDICATE": "x"},
        "two spaces": {"PREDICATE": " x"},
        "default, no space": {},
    }
    with pytest.raises(TypeError):
        report.report_read("PREDICATE:x\n", ("PREDICATE",), True)


def test_report_read_with_terminated_only_leaves_an_unterminated_last_line_unread_reads_it_by_default_is_keyword_only_and_combines_with_optional_space(report):
    answers = {
        "unterminated last": report.report_read("PREDICATE: a\nPREDICATE: b", ("PREDICATE",), terminated_only=True),
        "only line unterminated": report.report_read("PREDICATE: a", ("PREDICATE",), terminated_only=True),
        "default, unterminated last": report.report_read("PREDICATE: a\nPREDICATE: b", ("PREDICATE",)),
        "both options": report.report_read(
            "PREDICATE:a\nPREDICATE:  b\nPREDICATE:c", ("PREDICATE",), optional_space=True, terminated_only=True
        ),
    }

    assert answers == {
        "unterminated last": {"PREDICATE": "a"},
        "only line unterminated": {},
        "default, unterminated last": {"PREDICATE": "b"},
        "both options": {"PREDICATE": " b"},
    }
    with pytest.raises(TypeError):
        report.report_read("PREDICATE: a", ("PREDICATE",), False, True)
