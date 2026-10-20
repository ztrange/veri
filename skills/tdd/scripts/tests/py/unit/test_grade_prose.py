"""In-process cases for veri/grade_prose.py, the module grade-prose.sh is a shim over."""
import importlib
import subprocess

import pytest


@pytest.fixture
def grade_prose():
    return importlib.import_module("veri.grade_prose")


def test_a_grader_conf_model_value_that_names_no_version_makes_grade_prose_exit_2_before_anything_is_launched(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    launched = []
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", lambda argv, *a, **k: launched.append(argv))

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, launched) == (2, []), (code, launched, err)


def test_a_grader_conf_model_value_with_a_digit_but_no_version_makes_grade_prose_exit_2_before_anything_is_launched(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-x2\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    launched = []
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", lambda argv, *a, **k: launched.append(argv))

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, launched) == (2, []), (code, launched, err)


def test_the_prompt_grade_prose_renders_carries_the_poc_grader_instructions_with_the_verdict_line_inside_the_grades_block_1874(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    rendered = []

    def refuse(argv, *a, **k):
        with open(argv[-1], encoding="utf-8") as f:
            rendered.append(f.read())
        return subprocess.CompletedProcess(argv, 2)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", refuse)

    run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    prompt = rendered[0] if rendered else ""
    begin, end = prompt.find("BEGIN GRADES"), prompt.find("END GRADES")
    verdict = prompt.find("VERDICT:", begin)
    assert ("You judge only what the prose states" in prompt, 0 <= begin < verdict < end) == (True, True), prompt


def test_a_fenced_hash_line_equal_to_the_units_heading_never_starts_its_section_1874(grade_prose):
    text = "# Intro\n```\n## unit.md\nfenced body\n```\ntext\n## unit.md\nreal body\n"
    assert grade_prose.section(text, "unit.md") == "## unit.md\nreal body\n"


def test_a_unit_with_no_requirements_list_in_the_requirements_file_makes_grade_prose_exit_2_before_anything_is_launched_1874(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## other.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nVERDICT: PASS\\nEND GRADES"}\n')
    launched = []

    def launch(argv, *a, **k):
        launched.append(argv)
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, launched) == (2, []), (code, launched, err)


def test_a_grades_line_whose_grade_word_is_pass_ish_makes_grade_prose_exit_2_and_append_no_grading_event_1874(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nA1: PASS-ish — nearly\\nVERDICT: PASS\\nEND GRADES"}\n')

    def launch(argv, *a, **k):
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    written = "".join(p.read_text() for p in (tmp_path / ".tdd").iterdir()
                      if p.is_file() and p.name != "grade-prose.log")
    assert (code, "grading" in written) == (2, False), (code, written, err)


def test_a_units_signature_changes_when_its_text_changes_and_not_when_only_a_why_cell_changes_1725(
        tmp_path, monkeypatch, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.chdir(tmp_path)

    def signed(prose, why):
        (tmp_path / "unit.md").write_text(prose)
        (tmp_path / "REQUIREMENTS.md").write_text(
            "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | %s |\n" % why)
        return grade_prose.signature("REQUIREMENTS.md", "unit.md")

    base = signed("The widget is painted a deep blue.\n", "because")
    assert (signed("The widget is painted a deep blue.\n", "a different reason") == base,
            signed("The widget is painted a deep red.\n", "because") != base) == (True, True)


def test_a_units_signature_changes_when_any_id_cell_or_any_requirement_cell_of_its_list_changes_1725(
        tmp_path, monkeypatch, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.chdir(tmp_path)

    def signed(first_id, first_req, second_id, second_req):
        (tmp_path / "REQUIREMENTS.md").write_text(
            "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
            "| %s | %s | because |\n| %s | %s | because |\n" % (first_id, first_req, second_id, second_req))
        return grade_prose.signature("REQUIREMENTS.md", "unit.md")

    base = signed("A1", "The widget is blue.", "A2", "The widget is round.")
    changed = [signed("B1", "The widget is blue.", "A2", "The widget is round."),
               signed("A1", "The widget is red.", "A2", "The widget is round."),
               signed("A1", "The widget is blue.", "B2", "The widget is round."),
               signed("A1", "The widget is blue.", "A2", "The widget is square.")]
    assert [s != base for s in changed] == [True] * 4
