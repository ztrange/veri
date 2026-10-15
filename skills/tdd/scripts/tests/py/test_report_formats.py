"""In-process cases for veri/report_formats.py, the parser of a develop prompt's declared report formats."""
import importlib

import pytest


@pytest.fixture
def report_formats():
    return importlib.import_module("veri.report_formats")


def test_parse_reads_each_declared_format_refuses_none_and_a_required_format_without_suite_and_never_reads_an_outcome_line(report_formats):
    declared = (
        "Report.\n"
        "REPORT-FORMAT green | keys IMPL_PATH: SUITE: | suite required\n"
        "REPORT-FORMAT split | keys SPLIT: | suite exempt: a split runs no tests\n"
    )
    revise = "OUTCOME: revised\nREPORT-FORMAT revise | keys OUTCOME: SUITE: | suite required\n"

    assert report_formats.parse(declared) == [
        {"name": "green", "keys": ["IMPL_PATH:", "SUITE:"], "suite": "required", "reason": ""},
        {"name": "split", "keys": ["SPLIT:"], "suite": "exempt", "reason": "a split runs no tests"},
    ]
    assert [f["name"] for f in report_formats.parse(revise)] == ["revise"]
    for text in ("OUTCOME: revised\nSUITE: ran\n",
                 "REPORT-FORMAT green | keys IMPL_PATH: | suite required\n"):
        with pytest.raises(ValueError):
            report_formats.parse(text)
