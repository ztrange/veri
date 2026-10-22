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


def test_the_prompt_grade_prose_renders_states_that_an_empty_unit_is_graded_fail_on_every_row_without_reading_tools_2062(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("")
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

    prompt = " ".join((rendered[0] if rendered else "").split())
    assert "empty unit is graded FAIL on every requirement row without using any reading tool" in prompt, prompt


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


def test_a_units_signature_changes_when_the_grader_prompt_template_changes_and_when_the_grader_conf_model_changes_1725(
        tmp_path, monkeypatch, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    conf = tmp_path / "skills" / "tdd" / "grader.conf"
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.chdir(tmp_path)

    def signed(model, template):
        conf.write_text("model=%s\n" % model)
        monkeypatch.setattr(grade_prose, "GRADER_INSTRUCTIONS", template)
        return grade_prose.signature("REQUIREMENTS.md", "unit.md")

    base = signed("sonnet-4", "Grade the prose.")
    assert (signed("sonnet-4", "Grade the prose, strictly.") != base,
            signed("opus-4", "Grade the prose.") != base) == (True, True)


def test_a_pass_on_a_nested_unit_records_its_signature_in_the_skills_graded_and_writes_no_graded_beside_the_unit_1911(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "skills" / "demo" / "prompts").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "prompts" / "x.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/prompts/x.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nA1: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n')

    def launch(argv, *a, **k):
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "skills/demo/prompts/x.md"], cwd=tmp_path)

    graded = tmp_path / "skills" / "demo" / "GRADED"
    recorded = graded.read_text().split()[:1] if graded.exists() else []
    assert (code, recorded, (tmp_path / "skills" / "demo" / "prompts" / "GRADED").exists()) \
        == (0, ["skills/demo/prompts/x.md"], False), (code, err)


def test_owed_grades_a_unit_listed_only_in_the_requirements_md_beside_it_with_that_lists_requirements_1911(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "x.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "skills" / "demo" / "REQUIREMENTS.md").write_text(
        "## skills/demo/x.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nA1: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n')
    prompts = []

    def launch(argv, *a, **k):
        with open(argv[-1], encoding="utf-8") as f:
            prompts.append(f.read())
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["--owed"], cwd=tmp_path)

    assert (code, [("Unit: skills/demo/x.md" in p, "A1: The widget is blue." in p) for p in prompts]) \
        == (0, [(True, True)]), (code, prompts, err)


def test_a_grader_reply_with_no_grades_block_is_retried_once_by_default_and_a_valid_second_reply_exits_0_2062(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":"I will Read the file."}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS — blue\\nVERDICT: PASS\\nEND GRADES"}\n'])
    launched = []

    def launch(argv, *a, **k):
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, len(launched)) == (0, 2), (code, len(launched), err)


def test_with_two_retries_a_grader_that_never_writes_a_grades_block_is_launched_three_times_then_exits_2_with_the_same_message_2062(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    launched = []

    def launch(argv, *a, **k):
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":"I will Read the file."}\n')
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "2")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, len(launched), err.strip()) == (
        2, 3, "grade-prose.sh: no verdict obtained: the reply has no BEGIN GRADES block"), (code, len(launched), err)
