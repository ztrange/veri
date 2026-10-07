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
