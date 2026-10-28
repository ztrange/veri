"""In-process cases for veri/stale_rows.py, the module stale-rows.sh is a shim over."""
import importlib
import json

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


def test_main_2462_with_no_issue_argument_prints_a_usage_line_naming_the_script_and_exits_2(run_cli):
    stale_rows = importlib.import_module("veri.stale_rows")

    code, out, err = run_cli(stale_rows, [])

    assert (code, out, "usage: stale-rows.sh" in err) == (2, "", True)


def test_main_2462_grades_through_grade_proses_prompt_and_turns_its_grades_block_into_the_exit(
        tmp_path, monkeypatch, run_cli):
    import subprocess
    stale_rows = importlib.import_module("veri.stale_rows")
    grade_prose = importlib.import_module("veri.grade_prose")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "skills" / "marked.md").write_text("The marked unit says green.\n")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(stale_rows.github, "gh_issue_view", lambda number, field: ISSUE)
    monkeypatch.setattr(stale_rows, "default_branch_text",
                        lambda unit: "The marked unit says green.\n", raising=False)
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setenv("PATH", "")
    prompts = []

    def fake_launch(name, prompt, *args, env=None):
        with open(prompt, encoding="utf-8") as f:
            prompts.append(f.read())
        reply = ("BEGIN GRADES\nM1: FAIL — says green, not blue\nVERDICT: REJECT\nEND GRADES\n")
        (tmp_path / ".tdd" / "grade-prose.log").write_text(
            json.dumps({"type": "result", "result": reply}) + "\n")
        return subprocess.CompletedProcess([name], 0)

    monkeypatch.setattr(grade_prose.leaf, "launch", fake_launch)

    code, out, _ = run_cli(stale_rows, ["2462"], cwd=tmp_path)

    first = prompts[0] if prompts else ""
    assert (code, out, "Unit: skills/marked.md" in first, "The marked unit says green." in first,
            "M1: The marked unit says blue." in first, "U1" in first) == (
        1, "2462\tM1\tskills/marked.md\tM1: FAIL — says green, not blue\n", True, True, True, False)


@pytest.mark.parametrize("body", [
    "## Requirements\n\n"
    "### skills/unmarked.md\n\n"
    "| ID | Requirement | Why |\n|---|---|---|\n"
    "| U1 | The unmarked unit says red. | because |\n",
    "## What happened\n\nNothing here lists requirements.\n",
], ids=["all-units-unmarked", "no-requirements-section"])
def test_main_2462_exits_3_with_no_row_and_no_grader_call_when_no_unit_is_marked(
        monkeypatch, run_cli, body):
    stale_rows = importlib.import_module("veri.stale_rows")
    monkeypatch.setattr(stale_rows.github, "gh_issue_view", lambda number, field: body)
    asked = []

    def fake_grade(unit, rows):
        asked.append(unit)
        return 1, "U1: FAIL — says pink\n"

    monkeypatch.setattr(stale_rows, "grade", fake_grade)

    code, out, _ = run_cli(stale_rows, ["2462"])

    assert (code, out, asked) == (3, "", [])


def test_main_2462_exits_2_naming_the_marked_unit_on_stderr_when_the_grader_gives_no_verdict(
        monkeypatch, run_cli):
    stale_rows = importlib.import_module("veri.stale_rows")
    monkeypatch.setattr(stale_rows.github, "gh_issue_view", lambda number, field: ISSUE)
    asked = []

    def fake_grade(unit, rows):
        asked.append(unit)
        return 2, ""

    monkeypatch.setattr(stale_rows, "grade", fake_grade)

    code, out, err = run_cli(stale_rows, ["2462"])

    assert (code, out, "skills/marked.md" in err, asked) == (2, "", True, ["skills/marked.md"])


def test_main_2462_grades_the_marked_unit_as_it_reads_on_the_default_branch_not_the_working_tree(
        tmp_path, monkeypatch, run_cli):
    import subprocess
    stale_rows = importlib.import_module("veri.stale_rows")
    grade_prose = importlib.import_module("veri.grade_prose")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "skills" / "marked.md").write_text("The working tree says green.\n")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(stale_rows.github, "gh_issue_view", lambda number, field: ISSUE)
    monkeypatch.setattr(stale_rows, "default_branch_text",
                        lambda unit: "The default branch says blue.\n", raising=False)
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setenv("PATH", "")
    prompts = []

    def fake_launch(name, prompt, *args, env=None):
        with open(prompt, encoding="utf-8") as f:
            prompts.append(f.read())
        if "The default branch says blue." in prompts[-1]:
            reply = "BEGIN GRADES\nM1: PASS — says blue\nVERDICT: PASS\nEND GRADES\n"
        else:
            reply = "BEGIN GRADES\nM1: FAIL — says green\nVERDICT: REJECT\nEND GRADES\n"
        (tmp_path / ".tdd" / "grade-prose.log").write_text(
            json.dumps({"type": "result", "result": reply}) + "\n")
        return subprocess.CompletedProcess([name], 0)

    monkeypatch.setattr(grade_prose.leaf, "launch", fake_launch)

    code, out, _ = run_cli(stale_rows, ["2462"], cwd=tmp_path)

    first = prompts[0] if prompts else ""
    assert (code, out, "The default branch says blue." in first,
            "The working tree says green." in first) == (0, "", True, False)


def test_main_2462_regrades_only_when_the_marked_rows_or_the_units_default_branch_text_change(
        tmp_path, monkeypatch, run_cli):
    stale_rows = importlib.import_module("veri.stale_rows")
    issue = [ISSUE]
    unit_text = ["The marked unit says green.\n"]
    monkeypatch.setattr(stale_rows.github, "gh_issue_view", lambda number, field: issue[0])
    monkeypatch.setattr(stale_rows, "default_branch_text", lambda unit: unit_text[0], raising=False)
    asked = []

    def fake_grade(unit, rows):
        asked.append((unit, rows))
        return 1, "M1: FAIL — says green\n"

    monkeypatch.setattr(stale_rows, "grade", fake_grade)
    (tmp_path / ".tdd").mkdir()

    first = run_cli(stale_rows, ["2462"], cwd=tmp_path)
    again = run_cli(stale_rows, ["2462"], cwd=tmp_path)
    calls_after_again = len(asked)
    issue[0] = ISSUE.replace("says blue", "says teal")
    run_cli(stale_rows, ["2462"], cwd=tmp_path)
    calls_after_rows = len(asked)
    unit_text[0] = "The marked unit says blue.\n"
    run_cli(stale_rows, ["2462"], cwd=tmp_path)

    assert (first[:2] == again[:2], calls_after_again, calls_after_rows, len(asked)) == (
        True, 1, 2, 3)


def test_main_2462_regrades_after_a_no_verdict_result_rather_than_caching_it(
        tmp_path, monkeypatch, run_cli):
    stale_rows = importlib.import_module("veri.stale_rows")
    monkeypatch.setattr(stale_rows.github, "gh_issue_view", lambda number, field: ISSUE)
    monkeypatch.setattr(stale_rows, "default_branch_text", lambda unit: "The marked unit says blue.\n")
    answers = [(2, ""), (0, "")]
    asked = []

    def fake_grade(unit, rows):
        asked.append(unit)
        return answers.pop(0)

    monkeypatch.setattr(stale_rows, "grade", fake_grade)
    (tmp_path / ".tdd").mkdir()

    first = run_cli(stale_rows, ["2462"], cwd=tmp_path)
    second = run_cli(stale_rows, ["2462"], cwd=tmp_path)

    assert (first[0], second[0], len(asked)) == (2, 0, 2)


def test_main_2462_caches_a_file_heading_unit_so_a_second_call_on_an_unchanged_issue_makes_no_grader_call(
        tmp_path, monkeypatch, run_cli):
    stale_rows = importlib.import_module("veri.stale_rows")
    issue = ISSUE.replace("### skills/marked.md\n", "### skills/marked.md#Some heading\n")

    def default_text(file):
        if "#" in file:
            raise RuntimeError("git show cannot read %s" % file)
        return "The marked unit says green.\n"

    monkeypatch.setattr(stale_rows.github, "gh_issue_view", lambda number, field: issue)
    monkeypatch.setattr(stale_rows, "default_branch_text", default_text)
    asked = []

    def fake_grade(unit, rows):
        asked.append(unit)
        return 1, "M1: FAIL — says green\n"

    monkeypatch.setattr(stale_rows, "grade", fake_grade)
    (tmp_path / ".tdd").mkdir()

    first = run_cli(stale_rows, ["2462"], cwd=tmp_path)
    again = run_cli(stale_rows, ["2462"], cwd=tmp_path)

    assert (first[:2] == again[:2], len(asked)) == (True, 1)
