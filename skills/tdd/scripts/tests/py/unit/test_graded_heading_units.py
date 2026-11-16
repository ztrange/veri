"""`file#heading` units in GRADED files (PRD 024.7): a heading holding spaces is one unit field."""
import importlib

import pytest

MODEL = "grader-model-1"
HEADING_UNIT = "unit.md#Two words, 100% sure"
ENCODED = "unit.md#Two%20words,%20100%25%20sure"


@pytest.fixture
def grade_prose(monkeypatch):
    module = importlib.import_module("veri.grade_prose")
    monkeypatch.setattr(module, "grader_model", lambda: MODEL)
    monkeypatch.setattr(module, "grader_conf", lambda: {"model": MODEL})
    return module


def test_4016_signing_a_heading_unit_writes_each_space_as_percent_20_and_each_percent_as_percent_25(
        tmp_path, monkeypatch, grade_prose):
    monkeypatch.chdir(tmp_path)

    grade_prose.record_graded(HEADING_UNIT, "sig", "gid")

    fields = (tmp_path / "GRADED").read_text().split("\n")[0].split(" ")
    assert (len(fields), fields[:2], fields[3]) == (5, [ENCODED, "sig"], "gid")
