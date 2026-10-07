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
