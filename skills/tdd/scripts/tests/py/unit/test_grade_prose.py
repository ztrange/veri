"""In-process cases for veri/grade_prose.py, the module grade-prose.sh is a shim over."""
import importlib
import json
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


def test_the_prompt_grade_prose_renders_fails_a_row_naming_a_file_section_or_identifier_unless_the_prose_names_it_2443(grade_prose):
    prompt = " ".join(grade_prose.prompt("unit.md", "prose", "X1\tThe prose cites `README.md`.").split())

    assert "A requirement row that names a concrete artefact (a file, a section heading or an identifier) FAILS when the prose does not name that artefact too" in prompt, prompt


def test_a_fenced_hash_line_equal_to_the_units_heading_never_starts_its_section_1874(grade_prose):
    text = "# Intro\n```\n## unit.md\nfenced body\n```\ntext\n## unit.md\nreal body\n"
    assert grade_prose.section(text, "unit.md") == "## unit.md\nreal body\n"


def test_a_unit_headed_section_with_a_tilde_fence_holding_a_hash_line_is_one_section_ending_at_the_next_real_heading_1978(grade_prose):
    text = "## unit.md\nbefore\n~~~\n# fenced\n~~~\nafter\n## next\nother\n"
    assert grade_prose.section(text, "unit.md") == "## unit.md\nbefore\n~~~\n# fenced\n~~~\nafter\n"


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


def test_a_units_signature_changes_when_the_grader_conf_model_changes_1725(
        tmp_path, monkeypatch, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    conf = tmp_path / "skills" / "tdd" / "grader.conf"
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.chdir(tmp_path)

    def signed(model):
        conf.write_text("model=%s\n" % model)
        return grade_prose.signature("REQUIREMENTS.md", "unit.md")

    assert signed("opus-4") != signed("sonnet-4")


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


def test_a_full_pass_writes_a_graded_line_naming_the_grader_template_after_unit_signature_date_and_grading_id_2474(
        tmp_path, monkeypatch, run_cli, grade_prose):
    import hashlib
    import re

    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "x.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/x.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
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

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "skills/demo/x.md"], cwd=tmp_path)

    graded = tmp_path / "skills" / "demo" / "GRADED"
    fields = graded.read_text().split() if graded.exists() else []
    template = hashlib.sha256(grade_prose.GRADER_INSTRUCTIONS.encode("utf-8")).hexdigest()
    shape = [code, len(fields) > 4 and fields[0], len(fields) > 4 and bool(re.fullmatch(r"[0-9a-f]{64}", fields[1])),
             len(fields) > 4 and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields[2])),
             len(fields) > 4 and len(fields[4]) >= 7 and template.startswith(fields[4])]
    assert shape == [0, "skills/demo/x.md", True, True, True], (graded.read_text() if graded.exists() else err)


def test_a_rejected_unit_exits_1_writes_no_graded_line_and_leaves_a_record_keyed_by_the_unit_and_its_signature_2121(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nA1: FAIL - not stated\\nVERDICT: REJECT\\nEND GRADES"}\n')

    def launch(argv, *a, **k):
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)
    monkeypatch.chdir(tmp_path)
    sig = grade_prose.signature("REQUIREMENTS.md", "unit.md")

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    inputs = {"unit.md", "REQUIREMENTS.md", "grader.conf", "grade-prose.log"}
    records = [f for f in tmp_path.rglob("*") if f.is_file() and f.name not in inputs
               and "unit.md" in f.read_text(errors="ignore") and sig in f.read_text(errors="ignore")]
    assert (code, (tmp_path / "unit.md").parent.joinpath("GRADED").exists(), len(records) > 0) \
        == (1, False, True), (code, [str(r) for r in records], err)


def test_a_pass_on_unchanged_text_after_a_reject_exits_1_names_the_reject_and_writes_no_graded_line_2121(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = {
        "first": '{"type":"result","subtype":"success","is_error":false,"result":'
                 '"BEGIN GRADES\\nA1: FAIL - not stated\\nVERDICT: REJECT\\nEND GRADES"}\n',
        "second": '{"type":"result","subtype":"success","is_error":false,"result":'
                  '"BEGIN GRADES\\nA1: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n'}
    run = ["first"]

    def launch(argv, *a, **k):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(replies[run[0]])
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)
    run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)
    run[0] = "second"

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, (tmp_path / "GRADED").exists(), "REJECT" in out + err) == (1, False, True), (code, out, err)


def test_a_pass_after_a_reject_and_a_change_of_the_text_exits_0_and_signs_the_new_text_2121(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = {
        "first": '{"type":"result","subtype":"success","is_error":false,"result":'
                 '"BEGIN GRADES\\nA1: FAIL - not stated\\nVERDICT: REJECT\\nEND GRADES"}\n',
        "second": '{"type":"result","subtype":"success","is_error":false,"result":'
                  '"BEGIN GRADES\\nA1: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n'}
    run = ["first"]

    def launch(argv, *a, **k):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(replies[run[0]])
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)
    monkeypatch.chdir(tmp_path)
    run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)
    run[0] = "second"
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue, stated plainly as blue.\n")
    new_sig = grade_prose.signature("REQUIREMENTS.md", "unit.md")

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    graded = tmp_path / "GRADED"
    line = graded.read_text().split() if graded.exists() else []
    assert (code, line[:2]) == (0, ["unit.md", new_sig]), (code, out, err)


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


def test_a_non_integer_no_verdict_retries_makes_grade_prose_exit_2_naming_the_variable_and_launch_no_grader_2071(
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
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "abc")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, "VERI_NO_VERDICT_RETRIES" in err, "Traceback" in err, launched) == (2, True, False, []), (
        code, err, launched)


def test_a_negative_no_verdict_retries_makes_grade_prose_exit_2_naming_the_variable_and_launch_no_grader_2071(
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
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "-1")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, "VERI_NO_VERDICT_RETRIES" in err, "Traceback" in err, launched) == (2, True, False, []), (
        code, err, launched)


def test_a_line_indented_four_spaces_that_starts_with_backticks_is_text_so_a_real_heading_after_it_still_ends_the_section_1978(grade_prose):
    text = "## unit.md\nbefore\n    ```\nafter\n## next\nother\n"
    assert grade_prose.section(text, "unit.md") == "## unit.md\nbefore\n    ```\nafter\n"


def test_grade_prose_and_requirements_read_fences_and_a_units_section_through_the_markdown_sections_reader_1978(
        tmp_path, monkeypatch, grade_prose):
    import markdown_sections
    requirements = importlib.import_module("veri.requirements")
    reader = importlib.import_module("veri.markdown_sections")
    calls = []

    def spy(name):
        def wrapped(*a, **k):
            calls.append(name)
            return getattr(markdown_sections, "_orig_" + name)(*a, **k)
        return wrapped

    for name in ("fenced_lines", "section"):
        original = getattr(markdown_sections, name)
        monkeypatch.setattr(markdown_sections, "_orig_" + name, original, raising=False)
        monkeypatch.setattr(reader, "_orig_" + name, getattr(reader, name), raising=False)
        for owner in (markdown_sections, reader):
            monkeypatch.setattr(owner, name, spy(name))
        for consumer in (grade_prose, requirements):
            if getattr(consumer, name, None) in (original, getattr(reader, "_orig_" + name)):
                monkeypatch.setattr(consumer, name, spy(name))

    (tmp_path / "unit.md").write_text("## unit.md\nbody\n## next\nother\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | blue | because |\n")

    grade_prose.unit_text(str(tmp_path / "unit.md") + "#unit.md")
    through_grade_prose = set(calls)
    calls.clear()
    requirements.units(str(tmp_path / "REQUIREMENTS.md"))
    requirements.claims(str(tmp_path / "REQUIREMENTS.md"), "unit.md")

    assert (through_grade_prose, set(calls)) == ({"section", "fenced_lines"}, {"fenced_lines"}), (
        through_grade_prose, set(calls))


def test_in_a_file_with_no_fence_a_hash_run_with_no_space_after_it_ends_a_section_exactly_where_it_did_before_the_section_reader_1978(grade_prose):
    text = "## unit.md\nbody\n###deep\nkept\n##next\nother\n"
    assert grade_prose.section(text, "unit.md") == "## unit.md\nbody\n###deep\nkept\n"
    spaceless = "##unit.md\nbody\n###deep\nkept\n#tag\nother\n"
    assert grade_prose.section(spaceless, "unit.md") == "##unit.md\nbody\n###deep\nkept\n"


def test_a_crlf_files_unit_text_is_byte_identical_to_what_main_produced_before_the_section_reader_1978(tmp_path, grade_prose):
    (tmp_path / "unit.md").write_bytes(b"## unit.md\r\nbody\r\n## next\r\nother\r\n")
    assert grade_prose.unit_text(str(tmp_path / "unit.md") + "#unit.md") == "## unit.md\nbody\n"


def test_a_file_with_no_final_newline_has_a_unit_text_byte_identical_to_what_main_produced_with_no_newline_added_1978(tmp_path, grade_prose):
    (tmp_path / "unit.md").write_bytes(b"## unit.md\nbody\n## next\nother")
    (tmp_path / "last.md").write_bytes(b"## first\nx\n## last.md\nbody")
    assert grade_prose.unit_text(str(tmp_path / "unit.md") + "#unit.md") == "## unit.md\nbody\n"
    assert grade_prose.unit_text(str(tmp_path / "last.md") + "#last.md") == "## last.md\nbody"


def test_a_grades_block_naming_every_id_once_with_two_rows_swapped_out_of_file_order_is_a_pass_verdict_2208(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nA1: PASS - ok\\nA3: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n')

    def launch(argv, *a, **k):
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = (tmp_path / ".tdd" / "events.jsonl")
    graded = tmp_path / "GRADED"
    import json
    verdicts = [json.loads(line).get("verdict") for line in events.read_text().splitlines()] if events.exists() else None
    assert (code, "PASS" in verdicts if verdicts is not None else None,
            graded.read_text().split()[:1] if graded.exists() else []) == (0, True, ["unit.md"]), (code, err)


def test_a_grades_block_naming_every_id_once_with_a_fail_row_swapped_out_of_file_order_is_a_reject_verdict_2208(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - ok\\nA3: PASS - ok\\nA2: FAIL - not round\\nVERDICT: REJECT\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA2: FAIL - not round\\nVERDICT: REJECT\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA2: FAIL - not round\\nVERDICT: REJECT\\nEND GRADES"}\n'])

    def launch(argv, *a, **k):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    import json
    events = tmp_path / ".tdd" / "events.jsonl"
    records = [json.loads(line) for line in events.read_text().splitlines()] if events.exists() else []
    verdicts = [r.get("verdict") for r in records]
    assert (code, out.strip(), verdicts) == (1, "A2: FAIL - not round", ["REJECT"]), (code, out, err)


def test_a_grades_block_that_leaves_out_one_requirement_id_makes_grade_prose_exit_2_naming_it_as_missing_and_append_no_grading_event_2208(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n')

    def launch(argv, *a, **k):
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    assert (code, "grading" in (events.read_text() if events.exists() else ""),
            "missing" in err and "A3" in err) == (2, False, True), (code, err)


def test_with_no_verdict_retries_0_a_first_reply_leaving_out_one_requirement_id_launches_the_grader_once_and_exits_2_naming_it_missing_2215(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    launched = []

    def launch(argv, *a, **k):
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":'
            '"BEGIN GRADES\\nA1: PASS - ok\\nA3: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n')
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    assert (code, len(launched), err.strip(), events.exists()) == (
        2, 1, "grade-prose.sh: no verdict obtained: GRADES block is missing requirement IDs A2", False), (
        code, len(launched), err)


def test_a_grades_block_naming_one_requirement_id_twice_makes_grade_prose_exit_2_naming_it_as_repeated_and_append_no_grading_event_2208(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nA2: PASS - ok\\nA3: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n')

    def launch(argv, *a, **k):
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    assert (code, "grading" in (events.read_text() if events.exists() else ""),
            "repeated" in err and "A2" in err) == (2, False, True), (code, err)


def test_a_grades_block_naming_an_id_the_requirements_list_does_not_hold_makes_grade_prose_exit_2_naming_it_as_unknown_and_append_no_grading_event_2208(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nA3: PASS - ok\\nA9: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n')

    def launch(argv, *a, **k):
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    assert (code, "grading" in (events.read_text() if events.exists() else ""),
            "unknown" in err and "A9" in err) == (2, False, True), (code, err)


def test_a_first_reply_leaving_out_one_requirement_id_is_followed_by_a_second_grader_launch_for_that_row_only_and_the_merged_passes_exit_0_2215(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - ok\\nA3: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: FAIL - not blue\\nVERDICT: REJECT\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: FAIL - not blue\\nVERDICT: REJECT\\nEND GRADES"}\n'])
    prompts = []

    def launch(argv, *a, **k):
        with open(argv[-1], encoding="utf-8") as f:
            prompts.append(f.read())
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    import json
    events = (tmp_path / ".tdd" / "events.jsonl")
    follow = prompts[1] if len(prompts) > 1 else ""
    assert (code, len(prompts), "painted a deep blue" in follow, "A2: The widget is round." in follow,
            "A1: The widget is blue." in follow or "A3: The widget is small." in follow,
            "PASS" in [json.loads(line).get("verdict")
                       for line in (events.read_text().splitlines() if events.exists() else [])]) == (
        0, 2, True, True, False, True), (code, len(prompts), err)


def test_a_follow_up_reply_leaving_the_missing_requirement_id_out_again_makes_grade_prose_exit_2_naming_it_after_two_launches_and_append_no_grading_event_2215(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - ok\\nA3: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nVERDICT: PASS\\nEND GRADES"}\n'])
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

    events = tmp_path / ".tdd" / "events.jsonl"
    assert (code, len(launched), err.strip(), events.exists()) == (
        2, 2, "grade-prose.sh: no verdict obtained: GRADES block is missing requirement IDs A2", False), (
        code, len(launched), err)


def test_a_follow_up_reply_naming_an_id_it_was_not_asked_for_makes_grade_prose_exit_2_naming_it_as_unknown_and_append_no_grading_event_2215(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - ok\\nA3: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA9: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n'])

    def launch(argv, *a, **k):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    assert (code, "unknown" in err and "A9" in err, events.exists()) == (2, True, False), (code, err)


def test_a_fail_row_in_the_follow_up_reply_makes_the_merged_verdict_reject_with_that_row_printed_and_no_graded_line_2215(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - ok\\nA3: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA2: FAIL - not round\\nVERDICT: REJECT\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA2: FAIL - not round\\nVERDICT: REJECT\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA2: FAIL - not round\\nVERDICT: REJECT\\nEND GRADES"}\n'])

    def launch(argv, *a, **k):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    import json
    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in events.read_text().splitlines()] if events.exists() else []
    assert (code, out.strip(), verdicts, (tmp_path / "GRADED").exists()) == (
        1, "A2: FAIL - not round", ["REJECT"], False), (code, out, err)


def test_a_fail_row_in_the_first_reply_makes_the_merged_verdict_reject_when_the_follow_up_passes_2215(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: FAIL - not blue\\nA3: PASS - ok\\nVERDICT: REJECT\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: FAIL - not blue\\nVERDICT: REJECT\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: FAIL - not blue\\nVERDICT: REJECT\\nEND GRADES"}\n'])

    def launch(argv, *a, **k):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    import json
    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in events.read_text().splitlines()] if events.exists() else []
    assert (code, out.strip(), verdicts, (tmp_path / "GRADED").exists()) == (
        1, "A1: FAIL - not blue", ["REJECT"], False), (code, out, err)


@pytest.mark.parametrize("char", ["\x0c", "\x85", " "])
def test_a_mid_line_splitlines_separator_stays_inside_its_line_of_the_units_section_2181(grade_prose, char):
    text = "## u\nbefore%safter\nend\n## v\n" % char
    assert grade_prose.section(text, "u") == "## u\nbefore%safter\nend\n" % char


def test_a_first_reply_whose_grades_block_names_one_requirement_id_twice_relaunches_the_grader_and_a_well_formed_second_reply_exits_0_2300(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - blue\\nA1: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n'])
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


def test_a_first_reply_whose_grades_block_names_an_id_the_requirements_list_does_not_hold_relaunches_the_grader_and_a_well_formed_second_reply_exits_0_2300(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - blue\\nZ9: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n'])
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


def test_a_first_reply_whose_grades_block_carries_a_grade_word_other_than_pass_or_fail_relaunches_the_grader_and_a_well_formed_second_reply_exits_0_2300(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: MAYBE - blue\\nVERDICT: PASS\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n'])
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


def test_a_first_reply_with_text_after_end_grades_relaunches_the_grader_and_a_well_formed_second_reply_exits_0_2300(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - blue\\nVERDICT: PASS\\nEND GRADES\\nHope that helps."}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n'])
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


def test_with_two_retries_a_grader_whose_every_reply_names_one_requirement_id_twice_is_launched_three_times_then_exits_2_with_the_same_message_2300(
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
            '{"type":"result","subtype":"success","is_error":false,"result":'
            '"BEGIN GRADES\\nA1: PASS - blue\\nA1: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n')
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "2")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    assert (code, len(launched), "GRADES block names requirement IDs repeated" in err and "A1" in err,
            "grading" in (events.read_text() if events.exists() else "")) == (2, 3, True, False), (
        code, len(launched), err)


def test_with_three_retries_a_well_formed_grades_block_grading_one_requirement_fail_launches_the_grader_once_for_the_full_list_and_exits_1_naming_it_2304(
        tmp_path, monkeypatch, run_cli, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n")
    (tmp_path / ".tdd").mkdir()
    launched = []

    def launch(argv, *a, **k):
        prompt = open(argv[-1], encoding="utf-8").read()
        launched.append(("A1" in prompt, "A2" in prompt))
        (tmp_path / ".tdd" / "grade-prose.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":'
            '"BEGIN GRADES\\nA1: PASS - blue\\nA2: FAIL - not round\\nVERDICT: REJECT\\nEND GRADES"}\n')
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "3")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(subprocess, "run", launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    full = [l for l in launched if l == (True, True)]
    others = [l for l in launched if l != (True, True)]
    assert (code, len(full), set(others), out.strip()) == (1, 1, {(False, True)}, "A2: FAIL - not round"), (
        code, launched, out, err)


@pytest.mark.tree_audit("the skills directory, for every skills/v*/GRADED file")
def test_every_committed_graded_line_names_the_grader_template_it_was_signed_under_2474():
    import pathlib
    import re

    root = pathlib.Path(__file__).resolve().parents[6]
    renamed = sorted(root.glob("skills/v*/GRADED"))
    files = [root / "skills" / "tdd" / "GRADED", root / "operator" / "GRADED"] + renamed
    lines = [l for f in files for l in f.read_text().splitlines() if l.strip()]
    unnamed = [l.split()[0] for l in lines
               if len(l.split()) < 5 or not re.fullmatch(r"[0-9a-f]{7,64}", l.split()[4])]
    assert renamed, "skills/v*/GRADED matched none of the renamed skills' GRADED files"
    assert lines and unnamed == [], unnamed


def test_an_edit_to_the_grader_instructions_leaves_a_units_signature_unchanged_2474(
        tmp_path, monkeypatch, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.chdir(tmp_path)

    before = grade_prose.signature("REQUIREMENTS.md", "unit.md")
    monkeypatch.setattr(grade_prose, "GRADER_INSTRUCTIONS", grade_prose.GRADER_INSTRUCTIONS + "\nA new rule.")
    after = grade_prose.signature("REQUIREMENTS.md", "unit.md")

    assert after == before


def test_grade_prose_records_a_pass_verdict_when_the_shared_leaf_launch_wrapper_answers_with_an_all_pass_reply_2498(
        tmp_path, monkeypatch, run_cli, grade_prose):
    leaf = importlib.import_module("veri.leaf")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()

    def fake_launch(*a, **k):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":'
            '"BEGIN GRADES\\nA1: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n')
        return subprocess.CompletedProcess(list(a), 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(leaf, "launch", fake_launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    graded = tmp_path / "GRADED"
    assert (code, graded.read_text().split()[:1] if graded.exists() else []) == (0, ["unit.md"]), (code, err)


def test_the_prompt_grade_prose_renders_passes_a_row_naming_no_artefact_on_its_meaning_alone_in_any_wording_2443(grade_prose):
    prompt = " ".join(grade_prose.prompt("unit.md", "prose", "X1\tThe widget is blue.").split())

    assert "A row that names no artefact passes on meaning alone, in any wording" in prompt, prompt


def test_two_grading_calls_for_two_units_in_one_tree_each_leave_their_own_cost_readable_afterwards_2609(
        tmp_path, monkeypatch, run_cli, grade_prose):
    leaf = importlib.import_module("veri.leaf")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    table = "\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n\n"
    (tmp_path / "one.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "two.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text("## one.md" + table + "## two.md" + table)
    (tmp_path / ".tdd").mkdir()
    costs = iter(["0.01", "0.02"])

    def fake_launch(name, *a, **k):
        (tmp_path / ".tdd" / f"{name}.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"total_cost_usd":%s,"result":'
            '"BEGIN GRADES\\nA1: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n' % next(costs))
        return subprocess.CompletedProcess([name], 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(leaf, "launch", fake_launch)

    codes = [run_cli(grade_prose, ["REQUIREMENTS.md", unit], cwd=tmp_path)[0] for unit in ("one.md", "two.md")]

    left = sorted({float(json.loads(line)["total_cost_usd"])
                  for log in (tmp_path / ".tdd").glob("*.log") for line in log.read_text().splitlines()})
    assert (codes, left) == ([0, 0], [0.01, 0.02]), (codes, left)


def test_a_row_retry_within_one_grading_call_leaves_the_first_attempts_cost_readable_too_2609(
        tmp_path, monkeypatch, run_cli, grade_prose):
    leaf = importlib.import_module("veri.leaf")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter([("0.01", "A1: PASS - ok\\n"), ("0.02", "A2: PASS - ok\\n")])

    def fake_launch(name, *a, **k):
        cost, grades = next(replies)
        (tmp_path / ".tdd" / f"{name}.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"total_cost_usd":%s,"result":'
            '"BEGIN GRADES\\n%sVERDICT: PASS\\nEND GRADES"}\n' % (cost, grades))
        return subprocess.CompletedProcess([name], 0)

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(leaf, "launch", fake_launch)

    code = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)[0]

    left = sorted({float(json.loads(line)["total_cost_usd"])
                  for log in (tmp_path / ".tdd").glob("*.log") for line in log.read_text().splitlines()})
    assert (code, left) == (0, [0.01, 0.02]), (code, left)


def _costs_left(tmp_path):
    return sorted({float(json.loads(line)["total_cost_usd"])
                   for log in (tmp_path / ".tdd").glob("*.log") for line in log.read_text().splitlines()})


def test_a_no_verdict_first_attempt_and_its_retry_both_leave_their_cost_readable_afterwards_2609(
        tmp_path, monkeypatch, run_cli, grade_prose):
    leaf = importlib.import_module("veri.leaf")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter([("0.01", "no grades here"),
                    ("0.02", "BEGIN GRADES\\nA1: PASS - ok\\nVERDICT: PASS\\nEND GRADES")])

    def fake_launch(name, *a, **k):
        cost, reply = next(replies)
        (tmp_path / ".tdd" / f"{name}.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"total_cost_usd":%s,"result":"%s"}\n'
            % (cost, reply))
        return subprocess.CompletedProcess([name], 0)

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(leaf, "launch", fake_launch)

    code = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)[0]

    left = _costs_left(tmp_path)
    assert (code, left) == (0, [0.01, 0.02]), (code, left)


def test_two_successive_failed_row_retries_in_one_call_both_leave_their_cost_readable_afterwards_2609(
        tmp_path, monkeypatch, run_cli, grade_prose):
    leaf = importlib.import_module("veri.leaf")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    costs = iter(["0.01", "0.02", "0.03"])

    def fake_launch(name, *a, **k):
        (tmp_path / ".tdd" / f"{name}.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"total_cost_usd":%s,"result":'
            '"BEGIN GRADES\\nA1: FAIL - not blue\\nVERDICT: REJECT\\nEND GRADES"}\n' % next(costs))
        return subprocess.CompletedProcess([name], 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(leaf, "launch", fake_launch)

    run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    left = _costs_left(tmp_path)
    assert left == [0.01, 0.02, 0.03], left
