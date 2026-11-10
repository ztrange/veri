"""In-process cases for veri/requirements_preflight.py, the module requirements-preflight.sh is a shim over."""
import importlib


def test_3567_an_issue_whose_requirements_rows_are_all_new_identical_or_reword_marked_exits_0(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n")
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2<reword> | The widget is square. | corners |\n"
        "| A3 | The widget is shiny. | gloss |\n")

    code, out, err = run_cli(requirements_preflight, [str(issue)], cwd=tmp_path)

    assert (code, err) == (0, ""), (code, out, err)


def test_3567_an_issue_with_rows_clashing_across_tables_exits_2_naming_every_clashing_id(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("Unit text.\n")
    (tmp_path / "other.md").write_text("Other text.\n")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n" + head + "| A1 | The widget is blue. | because |\n\n"
        "## other.md\n\n" + head + "| B1 | The gadget is red. | because |\n"
        "| B2 | The gadget is small. | size |\n")

    def issue_with(a_row, b_row):
        path = tmp_path / "issue.md"
        path.write_text(
            "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n" + head + a_row + "\n"
            "| A2 | The widget is round. | shape |\n\n### other.md\n\n" + head + b_row + "\n"
            "| B2<reword> | The gadget is large. | size |\n")
        return path

    clean = issue_with("| A1 | The widget is blue. | because |", "| B1 | The gadget is red. | because |")
    assert run_cli(requirements_preflight, [str(clean)], cwd=tmp_path)[::2] == (0, "")

    clashing = issue_with("| A1 | The widget is green. | because |", "| B1 | The gadget is blue. | because |")
    code, out, err = run_cli(requirements_preflight, [str(clashing)], cwd=tmp_path)

    assert code == 2 and "A1" in err and "B1" in err and "A2" not in err and "B2" not in err, (code, out, err)


def test_3567_a_unit_whose_heading_repeats_in_the_issue_names_each_clashing_id_once(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("Unit text.\n")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n" + head + "| A1 | The widget is blue. | because |\n")
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n" + head +
        "| A1 | The widget is green. | because |\n\n### unit.md\n\n" + head +
        "| A2 | The widget is round. | shape |\n")

    code, out, err = run_cli(requirements_preflight, [str(issue)], cwd=tmp_path)

    assert code == 2 and err.count("A1") == 1 and "A2" not in err, (code, out, err)
