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


ROWS = "| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"


def heading_tree(root):
    (root / "unit.md").write_text("# Unit\nintro\n## Two words, 100% sure\nThe widget is blue.\n## Other\nelse\n")
    (root / "REQUIREMENTS.md").write_text("## %s\n\n%s\n## unit.md\n\n%s" % (HEADING_UNIT, ROWS, ROWS))


def test_4016_prose_owed_reads_a_signed_heading_unit_back_as_owing_nothing_and_an_orphan_one_by_its_heading(
        tmp_path, monkeypatch, run_cli, grade_prose):
    owed = importlib.import_module("veri.prose_owed")
    heading_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    signed = [grade_prose.signature("REQUIREMENTS.md", unit) for unit in (HEADING_UNIT, "unit.md")]
    (tmp_path / "GRADED").write_text("%s %s 2026-01-01 g1 t1\nunit.md %s 2026-01-01 g2 t1\n"
                                     "unit.md#Gone%%20heading cafe 2026-01-01 g3 t1\n" % (ENCODED, signed[0], signed[1]))

    code, out, err = run_cli(owed, [str(tmp_path)])

    assert (code, out) == (1, "unit.md#Gone heading (orphan)\n"), err


def test_4016_a_whole_file_units_graded_line_stays_byte_for_byte_and_owes_nothing_when_a_heading_unit_is_signed_beside_it(
        tmp_path, monkeypatch, grade_prose):
    heading_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    whole = "unit.md %s 2026-01-01 g2 t1\n" % grade_prose.signature("REQUIREMENTS.md", "unit.md")
    (tmp_path / "GRADED").write_text(whole)

    grade_prose.record_graded(HEADING_UNIT, grade_prose.signature("REQUIREMENTS.md", HEADING_UNIT), "g1")

    lines = (tmp_path / "GRADED").read_text().splitlines(keepends=True)
    assert (lines[0], grade_prose.owed_listed()) == (whole, ([], []))
