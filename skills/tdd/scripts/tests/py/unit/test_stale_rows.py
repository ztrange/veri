"""In-process cases for veri/stale_rows.py, the module stale-rows.sh is a shim over."""
import importlib

import pytest

ISSUE = (
    "## Requirements\n\n"
    "### skills/marked.md\n\n"
    "As is: these rows describe the unit's current text.\n\n"
    "| ID | Requirement | Why |\n|---|---|---|\n"
    "| M1 | The marked unit says blue. | because |\n\n"
    "### skills/unmarked.md\n\n"
    "| ID | Requirement | Why |\n|---|---|---|\n"
    "| U1 | The unmarked unit says red. | because |\n"
)


@pytest.mark.parametrize("graded, code, out", [
    ({"skills/marked.md": (1, "M1: FAIL — says green\n")},
     1, "2462\tM1\tskills/marked.md\tM1: FAIL — says green\n"),
    ({"skills/marked.md": (0, "")}, 0, ""),
])
def test_main_2462_grades_only_the_marked_units_rows_and_reports_the_failing_one(
        monkeypatch, run_cli, graded, code, out):
    stale_rows = importlib.import_module("veri.stale_rows")
    monkeypatch.setattr(stale_rows.github, "gh_issue_view", lambda number, field: ISSUE)
    asked = []

    def fake_grade(unit, rows):
        asked.append((unit, rows))
        return graded[unit]

    monkeypatch.setattr(stale_rows, "grade", fake_grade)

    got = run_cli(stale_rows, ["2462"])

    assert (got[0], got[1], [unit for unit, _ in asked]) == (code, out, ["skills/marked.md"])
    assert "U1" not in "".join(rows for _, rows in asked)


def test_main_2462_exits_1_when_an_earlier_marked_unit_fails_and_a_later_one_passes(
        monkeypatch, run_cli):
    stale_rows = importlib.import_module("veri.stale_rows")
    body = (
        "## Requirements\n\n"
        "### skills/first.md\n\n"
        "As is: these rows describe the unit's current text.\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| F1 | The first unit says blue. | because |\n\n"
        "### skills/second.md\n\n"
        "As is: these rows describe the unit's current text.\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| S1 | The second unit says green. | because |\n\n"
        "### skills/unmarked.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| U1 | The unmarked unit says red. | because |\n"
    )
    monkeypatch.setattr(stale_rows.github, "gh_issue_view", lambda number, field: body)
    graded = {"skills/first.md": (1, "F1: FAIL — says yellow\n"),
              "skills/second.md": (0, ""),
              "skills/unmarked.md": (1, "U1: FAIL — says pink\n")}
    asked = []

    def fake_grade(unit, rows):
        asked.append(unit)
        return graded[unit]

    monkeypatch.setattr(stale_rows, "grade", fake_grade)

    got = run_cli(stale_rows, ["2462"])

    assert (got[0], got[1], sorted(asked)) == (
        1, "2462\tF1\tskills/first.md\tF1: FAIL — says yellow\n",
        ["skills/first.md", "skills/second.md"])
