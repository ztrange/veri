"""In-process cases for veri/skill_edit_step.py, the module skill-edit-step.sh is a shim over."""
import importlib


def test_apply_adds_the_issue_rows_the_units_list_lacks_at_its_end_and_no_row_the_issue_does_not_state(tmp_path):
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    requirements = importlib.import_module("veri.requirements")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n\n"
        "## other.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| B1 | Other. | o |\n")
    (tmp_path / "issue.md").write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A3 | The widget is shiny. | gloss |\n\n"
        "### other.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| B2 | Not ours. | n |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), str(tmp_path / "unit.md"))

    ids = [row.split("\t")[0] for row in requirements.claims(str(tmp_path / "REQUIREMENTS.md"), "unit.md").splitlines()]
    assert ids == ["A1", "A2", "A3"], ids


def test_apply_rewords_a_row_the_list_already_holds_in_place_keeping_its_id_and_position(tmp_path):
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n"
        "| A3 | The widget is shiny. | gloss |\n")
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget is square. | corners |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), str(tmp_path / "unit.md"))

    rows = [l for l in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("| A")]
    assert rows == [
        "| A1 | The widget is blue. | because |",
        "| A2 | The widget is square. | corners |",
        "| A3 | The widget is shiny. | gloss |",
    ], rows


def test_apply_drops_the_row_an_issue_marks_dropped_and_renumbers_no_other_row(tmp_path):
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n"
        "| A3 | The widget is shiny. | gloss |\n")
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | (dropped) | no longer wanted |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), str(tmp_path / "unit.md"))

    rows = [l for l in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("| A")]
    assert rows == [
        "| A1 | The widget is blue. | because |",
        "| A3 | The widget is shiny. | gloss |",
    ], rows
