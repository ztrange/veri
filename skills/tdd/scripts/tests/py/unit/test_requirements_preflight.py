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
