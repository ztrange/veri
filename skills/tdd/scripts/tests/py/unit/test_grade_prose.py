"""In-process cases for veri/grade_prose.py, the module grade-prose.sh is a shim over."""
import importlib
import json
import subprocess

import pytest


@pytest.fixture
def grade_prose():
    return importlib.import_module("veri.grade_prose")


def test_a_grader_conf_model_value_that_names_no_version_makes_grade_prose_exit_2_before_anything_is_launched(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({})

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, fake.argvs) == (2, []), (code, fake.argvs, err)


def test_a_grader_conf_model_value_with_a_digit_but_no_version_makes_grade_prose_exit_2_before_anything_is_launched(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-x2\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({})

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, fake.argvs) == (2, []), (code, fake.argvs, err)


def test_the_prompt_grade_prose_renders_carries_the_poc_grader_instructions_with_the_verdict_line_inside_the_grades_block_1874(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    rendered = []

    def refuse(line, **kwargs):
        argv = fake.argvs[-1]
        with open(argv[-1], encoding="utf-8") as f:
            rendered.append(f.read())
        return (2, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=refuse)

    run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    prompt = rendered[0] if rendered else ""
    begin, end = prompt.find("BEGIN GRADES"), prompt.find("END GRADES")
    verdict = prompt.find("VERDICT:", begin)
    assert ("You judge only what the prose states" in prompt, 0 <= begin < verdict < end) == (True, True), prompt


def test_the_prompt_grade_prose_renders_states_that_an_empty_unit_is_graded_fail_on_every_row_without_reading_tools_2062(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    rendered = []

    def refuse(line, **kwargs):
        argv = fake.argvs[-1]
        with open(argv[-1], encoding="utf-8") as f:
            rendered.append(f.read())
        return (2, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=refuse)

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
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, fake.argvs) == (2, []), (code, fake.argvs, err)


def test_a_grades_line_whose_grade_word_is_pass_ish_makes_grade_prose_exit_2_and_append_no_grading_event_1874(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nA1: PASS-ish — nearly\\nVERDICT: PASS\\nEND GRADES"}\n')

    def launch(line, **kwargs):
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)

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


def test_4010_a_units_signature_is_the_value_it_was_before_the_grader_stopped_loading_the_project_claude_md(
        tmp_path, monkeypatch, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.chdir(tmp_path)

    assert grade_prose.signature("REQUIREMENTS.md", "unit.md") == (
        "f361d178d1bf7ebb72a81b0081587b3f694b6e7676453da140311f85bba28073")


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
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "skills/demo/prompts/x.md"], cwd=tmp_path)

    graded = tmp_path / "skills" / "demo" / "GRADED"
    recorded = graded.read_text().split()[:1] if graded.exists() else []
    assert (code, recorded, (tmp_path / "skills" / "demo" / "prompts" / "GRADED").exists()) \
        == (0, ["skills/demo/prompts/x.md"], False), (code, err)


def test_a_full_pass_writes_a_graded_line_naming_the_grader_template_after_unit_signature_date_and_grading_id_2474(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "skills/demo/x.md"], cwd=tmp_path)

    graded = tmp_path / "skills" / "demo" / "GRADED"
    fields = graded.read_text().split() if graded.exists() else []
    template = hashlib.sha256(grade_prose.GRADER_INSTRUCTIONS.encode("utf-8")).hexdigest()
    shape = [code, len(fields) > 4 and fields[0], len(fields) > 4 and bool(re.fullmatch(r"[0-9a-f]{64}", fields[1])),
             len(fields) > 4 and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields[2])),
             len(fields) > 4 and len(fields[4]) >= 7 and template.startswith(fields[4])]
    assert shape == [0, "skills/demo/x.md", True, True, True], (graded.read_text() if graded.exists() else err)


def test_a_rejected_unit_exits_1_writes_no_graded_line_and_leaves_a_record_keyed_by_the_unit_and_its_signature_2121(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nA1: FAIL - not stated\\nVERDICT: REJECT\\nEND GRADES"}\n')

    def launch(line, **kwargs):
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)
    monkeypatch.chdir(tmp_path)
    sig = grade_prose.signature("REQUIREMENTS.md", "unit.md")

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    inputs = {"unit.md", "REQUIREMENTS.md", "grader.conf", "grade-prose.log"}
    records = [f for f in tmp_path.rglob("*") if f.is_file() and f.name not in inputs
               and "unit.md" in f.read_text(errors="ignore") and sig in f.read_text(errors="ignore")]
    assert (code, (tmp_path / "unit.md").parent.joinpath("GRADED").exists(), len(records) > 0) \
        == (1, False, True), (code, [str(r) for r in records], err)


def test_a_pass_on_unchanged_text_after_a_reject_exits_1_names_the_reject_and_writes_no_graded_line_2121(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(replies[run[0]])
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)
    run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)
    run[0] = "second"

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, (tmp_path / "GRADED").exists(), "REJECT" in out + err) == (1, False, True), (code, out, err)


def test_a_pass_after_a_reject_and_a_change_of_the_text_exits_0_and_signs_the_new_text_2121(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(replies[run[0]])
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)
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
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        with open(argv[-1], encoding="utf-8") as f:
            prompts.append(f.read())
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["--owed"], cwd=tmp_path)

    assert (code, [("Unit: skills/demo/x.md" in p, "A1: The widget is blue." in p) for p in prompts]) \
        == (0, [(True, True)]), (code, prompts, err)


def test_a_grader_reply_with_no_grades_block_is_retried_once_by_default_and_a_valid_second_reply_exits_0_2062(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, len(launched)) == (0, 2), (code, len(launched), err)


def test_with_two_retries_a_grader_that_never_writes_a_grades_block_is_launched_three_times_then_exits_2_with_the_same_message_2062(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":"I will Read the file."}\n')
        return (0, "", "")

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "2")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, len(launched), err.strip()) == (
        2, 3, "grade-prose.sh: no verdict obtained: the reply has no BEGIN GRADES block"), (code, len(launched), err)


def test_a_non_integer_no_verdict_retries_makes_grade_prose_exit_2_naming_the_variable_and_launch_no_grader_2071(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        return (0, "", "")

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "abc")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, "VERI_NO_VERDICT_RETRIES" in err, "Traceback" in err, launched) == (2, True, False, []), (
        code, err, launched)


def test_a_negative_no_verdict_retries_makes_grade_prose_exit_2_naming_the_variable_and_launch_no_grader_2071(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        return (0, "", "")

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "-1")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, "VERI_NO_VERDICT_RETRIES" in err, "Traceback" in err, launched) == (2, True, False, []), (
        code, err, launched)


def test_a_line_indented_four_spaces_that_starts_with_backticks_is_text_so_a_real_heading_after_it_still_ends_the_section_1978(grade_prose):
    text = "## unit.md\nbefore\n    ```\nafter\n## next\nother\n"
    assert grade_prose.section(text, "unit.md") == "## unit.md\nbefore\n    ```\nafter\n"


def test_grade_prose_and_requirements_read_fences_through_the_markdown_sections_reader_1978_4016(
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

    for name in ("fenced_lines",):
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

    assert (through_grade_prose, set(calls)) == ({"fenced_lines"}, {"fenced_lines"}), (
        through_grade_prose, set(calls))


def test_in_a_file_with_no_fence_a_hash_run_with_no_space_after_it_ends_a_units_own_text_1978_4016(grade_prose):
    text = "## unit.md\nbody\n###deep\nkept\n##next\nother\n"
    assert grade_prose.section(text, "unit.md") == "## unit.md\nbody\n"
    spaceless = "##unit.md\nbody\n#tag\nother\n"
    assert grade_prose.section(spaceless, "unit.md") == "##unit.md\nbody\n"


def test_a_crlf_files_unit_text_is_byte_identical_to_what_main_produced_before_the_section_reader_1978(tmp_path, grade_prose):
    (tmp_path / "unit.md").write_bytes(b"## unit.md\r\nbody\r\n## next\r\nother\r\n")
    assert grade_prose.unit_text(str(tmp_path / "unit.md") + "#unit.md") == "## unit.md\nbody\n"


def test_a_file_with_no_final_newline_has_a_unit_text_byte_identical_to_what_main_produced_with_no_newline_added_1978(tmp_path, grade_prose):
    (tmp_path / "unit.md").write_bytes(b"## unit.md\nbody\n## next\nother")
    (tmp_path / "last.md").write_bytes(b"## first\nx\n## last.md\nbody")
    assert grade_prose.unit_text(str(tmp_path / "unit.md") + "#unit.md") == "## unit.md\nbody\n"
    assert grade_prose.unit_text(str(tmp_path / "last.md") + "#last.md") == "## last.md\nbody"


def test_a_grades_block_naming_every_id_once_with_two_rows_swapped_out_of_file_order_is_a_pass_verdict_2208(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = (tmp_path / ".tdd" / "events.jsonl")
    graded = tmp_path / "GRADED"
    import json
    verdicts = [json.loads(line).get("verdict") for line in events.read_text().splitlines()] if events.exists() else None
    assert (code, "PASS" in verdicts if verdicts is not None else None,
            graded.read_text().split()[:1] if graded.exists() else []) == (0, True, ["unit.md"]), (code, err)


def test_a_grades_block_naming_every_id_once_with_a_fail_row_swapped_out_of_file_order_is_a_reject_verdict_2208(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    import json
    events = tmp_path / ".tdd" / "events.jsonl"
    records = [json.loads(line) for line in events.read_text().splitlines()] if events.exists() else []
    verdicts = [r.get("verdict") for r in records]
    assert (code, out.strip(), verdicts) == (1, "A2: FAIL - not round", ["REJECT"]), (code, out, err)


def test_a_grades_block_that_leaves_out_one_requirement_id_makes_grade_prose_exit_2_naming_it_as_missing_and_append_no_grading_event_2208(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        if len(launched) > 1:
            (tmp_path / ".tdd" / "grade-prose.log").write_text(
                '{"type":"result","subtype":"success","is_error":false,"result":'
                '"BEGIN GRADES\\nVERDICT: PASS\\nEND GRADES"}\n')
        return (0, "", "")

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    assert (code, "grading" in (events.read_text() if events.exists() else ""),
            "missing" in err and "A3" in err) == (2, False, True), (code, err)


def test_with_no_verdict_retries_0_a_first_reply_leaving_out_one_requirement_id_launches_the_grader_once_and_exits_2_naming_it_missing_2215(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        rows = "A1: PASS - ok\\nA3: PASS - ok" if len(launched) == 1 else "A2: PASS - ok"
        (tmp_path / ".tdd" / "grade-prose.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":'
            '"BEGIN GRADES\\n' + rows + '\\nVERDICT: PASS\\nEND GRADES"}\n')
        return (0, "", "")

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in (events.read_text().splitlines() if events.exists() else [])]
    assert (code, "PASS" in verdicts) == (0, True), (code, err)


def test_a_grades_block_naming_one_requirement_id_twice_makes_grade_prose_exit_2_naming_it_as_repeated_and_append_no_grading_event_2208(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    assert (code, "grading" in (events.read_text() if events.exists() else ""),
            "repeated" in err and "A2" in err) == (2, False, True), (code, err)


def test_a_grades_block_grading_every_wanted_id_and_an_id_outside_the_list_exits_0_with_the_on_list_verdict_naming_the_off_list_id_on_stderr_3295(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nA3: PASS - ok\\nA9: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n'])
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in (events.read_text().splitlines() if events.exists() else [])]
    assert (code, verdicts, "A9" in err, len(launched)) == (0, ["PASS"], True, 1), (code, err)


def test_a_first_reply_leaving_out_one_requirement_id_is_followed_by_a_second_grader_launch_for_that_row_only_and_the_merged_passes_exit_0_2215(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        with open(argv[-1], encoding="utf-8") as f:
            prompts.append(f.read())
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

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
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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
    empty = ('{"type":"result","subtype":"success","is_error":false,"result":'
             '"BEGIN GRADES\\nVERDICT: PASS\\nEND GRADES"}\n')
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, empty))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    assert (code, "missing" in err and "A2" in err, events.exists()) == (2, True, False), (code, err)


def test_a_follow_up_reply_grading_the_missing_id_and_an_id_outside_its_list_keeps_the_merged_on_list_verdict_naming_the_off_list_id_3295(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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
                    '"BEGIN GRADES\\nA2: PASS - ok\\nA9: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n'])
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in (events.read_text().splitlines() if events.exists() else [])]
    assert (code, verdicts, "A9" in err, len(launched)) == (0, ["PASS"], True, 2), (code, err)


def test_an_off_list_row_graded_fail_beside_wanted_rows_all_graded_pass_leaves_the_verdict_pass_and_exits_0_3295(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nA3: PASS - ok\\nA9: FAIL - bad\\nVERDICT: PASS\\nEND GRADES"}\n'])
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in (events.read_text().splitlines() if events.exists() else [])]
    assert (code, verdicts, "A9" in err, len(launched)) == (0, ["PASS"], True, 1), (code, err)


def test_a_grades_block_missing_a_wanted_id_while_grading_an_off_list_id_exits_2_naming_the_missing_id_and_appends_no_grading_event_3295(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
        "| A3 | The widget is small. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - ok\\nA3: PASS - ok\\nA9: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n',
                    '{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nVERDICT: PASS\\nEND GRADES"}\n'])
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in (events.read_text().splitlines() if events.exists() else [])]
    assert (code, "missing requirement IDs A2" in err, verdicts) == (2, True, []), (code, err)


def test_a_fail_row_in_the_follow_up_reply_makes_the_merged_verdict_reject_with_that_row_printed_and_no_graded_line_2215(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    import json
    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in events.read_text().splitlines()] if events.exists() else []
    assert (code, out.strip(), verdicts, (tmp_path / "GRADED").exists()) == (
        1, "A2: FAIL - not round", ["REJECT"], False), (code, out, err)


def test_a_fail_row_in_the_first_reply_makes_the_merged_verdict_reject_when_the_follow_up_passes_2215(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)

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
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, len(launched)) == (0, 2), (code, len(launched), err)


def test_a_first_reply_whose_grades_block_grades_every_wanted_id_plus_an_off_list_id_is_accepted_with_exactly_one_grader_launch_3295(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nA1: PASS - blue\\nZ9: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n'])
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in (events.read_text().splitlines() if events.exists() else [])]
    assert (code, len(launched), verdicts) == (0, 1, ["PASS"]), (code, len(launched), err)


def test_a_first_reply_whose_grades_block_carries_a_grade_word_other_than_pass_or_fail_relaunches_the_grader_and_a_well_formed_second_reply_exits_0_2300(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, len(launched)) == (0, 2), (code, len(launched), err)


def test_a_first_reply_with_text_after_end_grades_relaunches_the_grader_and_a_well_formed_second_reply_exits_0_2300(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
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

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, len(launched)) == (0, 2), (code, len(launched), err)


def test_with_two_retries_a_grader_whose_every_reply_names_one_requirement_id_twice_is_launched_three_times_then_exits_2_with_the_same_message_2300(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":'
            '"BEGIN GRADES\\nA1: PASS - blue\\nA1: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n')
        return (0, "", "")

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "2")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    assert (code, len(launched), "GRADES block names requirement IDs repeated" in err and "A1" in err,
            "grading" in (events.read_text() if events.exists() else "")) == (2, 3, True, False), (
        code, len(launched), err)


def test_with_three_retries_a_well_formed_grades_block_grading_one_requirement_fail_launches_the_grader_once_for_the_full_list_and_exits_1_naming_it_2304(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n")
    (tmp_path / ".tdd").mkdir()
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        prompt = open(argv[-1], encoding="utf-8").read()
        launched.append(("A1" in prompt, "A2" in prompt))
        (tmp_path / ".tdd" / "grade-prose.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":'
            '"BEGIN GRADES\\nA1: PASS - blue\\nA2: FAIL - not round\\nVERDICT: REJECT\\nEND GRADES"}\n')
        return (0, "", "")

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "3")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    full = [launch for launch in launched if launch == (True, True)]
    others = [launch for launch in launched if launch != (True, True)]
    assert (code, len(full), set(others), out.strip()) == (1, 1, {(False, True)}, "A2: FAIL - not round"), (
        code, launched, out, err)


@pytest.mark.tree_audit("the skills directory, for every skills/v*/GRADED file")
def test_every_committed_graded_line_names_the_grader_template_it_was_signed_under_2474():
    import pathlib
    import re

    root = pathlib.Path(__file__).resolve().parents[6]
    renamed = sorted(root.glob("skills/v*/GRADED"))
    files = [root / "skills" / "tdd" / "GRADED", root / "operator" / "GRADED"] + renamed
    lines = [line for f in files for line in f.read_text().splitlines() if line.strip()]
    unnamed = [line.split()[0] for line in lines
               if len(line.split()) < 5 or not re.fullmatch(r"[0-9a-f]{7,64}", line.split()[4])]
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


@pytest.mark.parametrize("cost, written", [("0.00001", "0.00001"), ("0.0425", "0.0425"),
                                           ("0.032333100000000004", "0.032333100000000004")])
def test_the_grading_event_writes_its_cost_as_a_plain_decimal_with_no_exponent_and_a_typical_cost_as_python_prints_it(
        tmp_path, monkeypatch, run_cli, grade_prose, cost, written):
    leaf = importlib.import_module("veri.leaf")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "one.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## one.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n\n")
    (tmp_path / ".tdd").mkdir()

    def fake_launch(name, *a, **k):
        (tmp_path / ".tdd" / f"{name}.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"total_cost_usd":%s,"result":'
            '"BEGIN GRADES\\nA1: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n' % cost)
        return subprocess.CompletedProcess([name], 0)

    monkeypatch.delenv("VERI_EVENT_STRICT")  # the bytes a real run writes, which never runs strict
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(leaf, "launch", fake_launch)

    code = run_cli(grade_prose, ["REQUIREMENTS.md", "one.md"], cwd=tmp_path)[0]

    gradings = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()
                if json.loads(line).get("event") == "grading"]
    assert (code, [g["cost_usd"] for g in gradings]) == (0, [written])


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


@pytest.mark.tree_audit("the skills directory, for every skills/v*/GRADED file")
def test_a_confirming_re_grade_reply_with_no_grades_block_is_relaunched_and_a_valid_retry_gets_its_verdict_not_exit_2_2989(
        tmp_path, monkeypatch, run_cli, grade_prose):
    leaf = importlib.import_module("veri.leaf")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    fail = "BEGIN GRADES\\nA1: FAIL - not blue\\nVERDICT: REJECT\\nEND GRADES"
    replies = iter([fail, "I will grep the file first.", fail, fail])

    def fake_launch(name, *a, **k):
        (tmp_path / ".tdd" / f"{name}.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":"%s"}\n' % next(replies))
        return subprocess.CompletedProcess([name], 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(leaf, "launch", fake_launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, out) == (1, "A1: FAIL - not blue\n"), (code, out, err)


@pytest.mark.tree_audit("the skills directory, for every skills/v*/GRADED file")
def test_a_confirming_re_grade_reply_whose_grades_block_repeats_an_id_is_relaunched_and_a_valid_retry_gives_the_verdict_2989(
        tmp_path, monkeypatch, run_cli, grade_prose):
    leaf = importlib.import_module("veri.leaf")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    fail = "BEGIN GRADES\\nA1: FAIL - not blue\\nVERDICT: REJECT\\nEND GRADES"
    twice = "BEGIN GRADES\\nA1: PASS\\nA1: PASS\\nVERDICT: PASS\\nEND GRADES"
    replies = iter([fail, twice, fail, fail])

    def fake_launch(name, *a, **k):
        (tmp_path / ".tdd" / f"{name}.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":"%s"}\n' % next(replies))
        return subprocess.CompletedProcess([name], 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(leaf, "launch", fake_launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert code == 1, (code, out, err)


@pytest.mark.tree_audit("the skills directory, for every skills/v*/GRADED file")
def test_with_two_retries_a_confirming_re_grade_that_never_writes_a_grades_block_is_launched_three_times_then_exits_2_with_the_re_grade_message_2989(
        tmp_path, monkeypatch, run_cli, grade_prose):
    leaf = importlib.import_module("veri.leaf")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    fail = "BEGIN GRADES\\nA1: FAIL - not blue\\nVERDICT: REJECT\\nEND GRADES"
    replies = iter([fail] + ["I will grep the file first."] * 10)
    launched = []

    def fake_launch(name, *a, **k):
        launched.append(name)
        (tmp_path / ".tdd" / f"{name}.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":"%s"}\n' % next(replies))
        return subprocess.CompletedProcess([name], 0)

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "2")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(leaf, "launch", fake_launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, len(launched) - 1, err.strip()) == (
        2, 3,
        "grade-prose.sh: no verdict obtained: the re-grade has no GRADES block for the rows it was asked about"), (
        code, launched, err)


@pytest.mark.tree_audit("the skills directory, for every skills/v*/GRADED file")
def test_with_zero_retries_a_confirming_re_grade_that_never_writes_a_grades_block_is_launched_once_then_exits_2_with_the_re_grade_message_2989(
        tmp_path, monkeypatch, run_cli, grade_prose):
    leaf = importlib.import_module("veri.leaf")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    fail = "BEGIN GRADES\\nA1: FAIL - not blue\\nVERDICT: REJECT\\nEND GRADES"
    replies = iter([fail] + ["I will grep the file first."] * 10)
    launched = []

    def fake_launch(name, *a, **k):
        launched.append(name)
        (tmp_path / ".tdd" / f"{name}.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":"%s"}\n' % next(replies))
        return subprocess.CompletedProcess([name], 0)

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(leaf, "launch", fake_launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, len(launched) - 1, err.strip()) == (
        2, 1,
        "grade-prose.sh: no verdict obtained: the re-grade has no GRADES block for the rows it was asked about"), (
        code, launched, err)


@pytest.mark.tree_audit("the skills directory, for every skills/v*/GRADED file")
def test_the_first_pass_prompt_and_the_confirming_re_grade_prompt_both_tell_the_grader_to_call_no_tool_2989(
        tmp_path, monkeypatch, run_cli, grade_prose):
    leaf = importlib.import_module("veri.leaf")
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    fail = "BEGIN GRADES\\nA1: FAIL - not blue\\nVERDICT: REJECT\\nEND GRADES"
    replies = iter([fail, fail, fail])
    prompts = []

    def fake_launch(name, prompt_path, *a, **k):
        prompts.append(open(prompt_path).read())
        (tmp_path / ".tdd" / f"{name}.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":"%s"}\n' % next(replies))
        return subprocess.CompletedProcess([name], 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(leaf, "launch", fake_launch)

    run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    rule = "Answer from the text given here. Do not call any tool."
    assert [rule in p for p in prompts] == [True, True, True], prompts


def test_a_401_row_unit_whose_relaunch_spends_the_retries_and_omits_a_contiguous_run_is_asked_for_those_rows_only_and_exits_0_with_pass_3091(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    import re
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    ids = ["R%d" % n for n in range(1, 402)]
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        + "".join("| %s | Row %s holds. | because |\n" % (i, i) for i in ids))
    (tmp_path / ".tdd").mkdir()
    skipped = ids[77:99]
    calls = []

    def reply(lines):
        body = "BEGIN GRADES\n" + "".join(line + "\n" for line in lines) + "VERDICT: PASS\nEND GRADES"
        return json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": body}) + "\n"

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        with open(argv[-1], encoding="utf-8") as f:
            asked = re.findall(r"^(R\d+): Row ", f.read(), re.M)
        calls.append(asked)
        if len(calls) == 1:
            out = reply(["%s: PASS - ok" % i for i in ids] + ["R1: PASS - ok"])
        elif len(calls) == 2:
            out = reply(["%s: PASS - ok" % i for i in ids if i not in skipped])
        else:
            out = reply(["%s: PASS - ok" % i for i in asked])
        (tmp_path / ".tdd" / "grade-prose.log").write_text(out)
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in (events.read_text().splitlines() if events.exists() else [])]
    follow_ups = sorted(i for asked in calls[2:] for i in asked)
    assert (code, "PASS" in verdicts, follow_ups) == (0, True, sorted(skipped)), (code, err[:200])


def test_a_missing_rows_follow_up_after_the_relaunches_are_spent_that_still_leaves_rows_ungraded_exits_2_naming_them_and_saying_the_follow_up_was_tried_3091(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    import re
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    ids = ["R%d" % n for n in range(1, 31)]
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        + "".join("| %s | Row %s holds. | because |\n" % (i, i) for i in ids))
    (tmp_path / ".tdd").mkdir()
    skipped = ids[10:14]
    calls = []

    def reply(lines):
        body = "BEGIN GRADES\n" + "".join(line + "\n" for line in lines) + "VERDICT: PASS\nEND GRADES"
        return json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": body}) + "\n"

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        with open(argv[-1], encoding="utf-8") as f:
            asked = re.findall(r"^(R\d+): Row ", f.read(), re.M)
        calls.append(asked)
        if len(calls) == 1:
            out = reply(["%s: PASS - ok" % i for i in ids] + ["R1: PASS - ok"])
        elif len(calls) == 2:
            out = reply(["%s: PASS - ok" % i for i in ids if i not in skipped])
        else:
            out = reply([])
        (tmp_path / ".tdd" / "grade-prose.log").write_text(out)
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, all(i in err for i in skipped), "follow-up" in err and "tried" in err) == (2, True, True), (code, err)


def test_a_grades_block_grading_every_wanted_id_pass_with_a_reason_line_inside_it_exits_0_with_the_pass_verdict_3631(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| R1 | The widget is blue. | because |\n| R2 | The widget is round. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nR1: PASS - ok\\nREASON: The text is fine\\nR2: PASS - ok\\n'
                    'VERDICT: PASS\\nEND GRADES"}\n'])

    def launch(line, **kwargs):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in (events.read_text().splitlines() if events.exists() else [])]
    assert (code, verdicts) == (0, ["PASS"]), (code, verdicts, err)


def test_a_first_reply_whose_grades_block_grades_every_wanted_id_pass_with_a_reason_line_inside_it_is_accepted_with_exactly_one_grader_launch_3631(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| R1 | The widget is blue. | because |\n| R2 | The widget is round. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nR1: PASS - ok\\nREASON: The text is fine\\nR2: PASS - ok\\n'
                    'VERDICT: PASS\\nEND GRADES"}\n'])
    launched = []

    def launch(line, **kwargs):
        argv = fake.argvs[-1]
        launched.append(argv)
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in (events.read_text().splitlines() if events.exists() else [])]
    assert (code, len(launched), verdicts) == (0, 1, ["PASS"]), (code, len(launched), err)


def test_a_grades_block_grading_one_wanted_id_fail_with_a_reason_line_inside_it_exits_1_with_the_reject_verdict_naming_the_fail_row_3631(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| R1 | The widget is blue. | because |\n| R2 | The widget is round. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nR1: PASS - ok\\nREASON: The text is fine\\nR2: FAIL - not round\\n'
                    'VERDICT: REJECT\\nEND GRADES"}\n'] * 3)

    def launch(line, **kwargs):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.delenv("VERI_NO_VERDICT_RETRIES", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    events = tmp_path / ".tdd" / "events.jsonl"
    verdicts = [json.loads(line).get("verdict") for line in (events.read_text().splitlines() if events.exists() else [])]
    assert (code, out.strip(), verdicts) == (1, "R2: FAIL - not round", ["REJECT"]), (code, out, err)


def test_a_grades_block_grading_a_wanted_id_maybe_beside_a_reason_line_inside_it_exits_2_naming_the_grade_word_maybe_3631(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| R1 | The widget is blue. | because |\n| R2 | The widget is round. | because |\n")
    (tmp_path / ".tdd").mkdir()
    replies = iter(['{"type":"result","subtype":"success","is_error":false,"result":'
                    '"BEGIN GRADES\\nREASON: The text is unclear\\nR1: MAYBE - blue\\nR2: PASS - ok\\n'
                    'VERDICT: PASS\\nEND GRADES"}\n'] * 3)

    def launch(line, **kwargs):
        (tmp_path / ".tdd" / "grade-prose.log").write_text(next(replies, ""))
        return (0, "", "")

    monkeypatch.setenv("VERI_NO_VERDICT_RETRIES", "0")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({}, default=launch)

    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (code, "grade word MAYBE is neither PASS nor FAIL" in err) == (2, True), (code, err)


def test_grade_unit_answers_like_main_for_the_same_path_and_unit_a_versionless_grader_model_exits_2_with_the_same_stderr(
        tmp_path, monkeypatch, run_cli, capfd, grade_prose, fake_processes):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake = fake_processes.answers({})
    monkeypatch.chdir(tmp_path)

    code = grade_prose.grade_unit("REQUIREMENTS.md", "unit.md").code
    captured = capfd.readouterr()
    via_main = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert via_main[0] == code == 2
    assert (captured.out, captured.err) == (via_main[1], via_main[2])
    assert "names no version" in captured.err
    assert fake.calls == []


def _grader_tree(tmp_path, monkeypatch, grade_prose, fake_processes, reply):
    """A tree with one unit and its one-row list, whose grader leaf answers `reply`; returns the prompts it read."""
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The working tree says green.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    prompts = []

    def launch(line, **kwargs):
        with open(line.split()[3], encoding="utf-8") as f:
            prompts.append(f.read())
        (tmp_path / ".tdd" / "grade-prose.log").write_text(json.dumps({"type": "result", "result": reply}) + "\n")
        return (0, "", "")

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    fake_processes.answers({"supervise.sh": launch})
    monkeypatch.chdir(tmp_path)
    return prompts


def test_grade_unit_grades_the_text_its_reader_answers_and_returns_the_failing_rows_without_printing_them(
        tmp_path, monkeypatch, capsys, grade_prose, fake_processes):
    prompts = _grader_tree(tmp_path, monkeypatch, grade_prose, fake_processes,
                           "BEGIN GRADES\nA1: FAIL - says teal\nVERDICT: REJECT\nEND GRADES\n")

    grading = grade_prose.grade_unit("REQUIREMENTS.md", "unit.md", read=lambda file: "The reader says teal.\n")

    first = prompts[0] if prompts else ""
    assert (grading.code, grading.verdict, grading.failing, grading.lines, grading.out) == (
        1, "REJECT", ("A1",), ("A1: FAIL - says teal",), "A1: FAIL - says teal\n")
    assert ("The reader says teal." in first, "The working tree says green." in first) == (True, False)
    assert capsys.readouterr().out == ""


def test_main_renders_grade_units_record_to_the_bytes_grade_prose_printed_a_pass_as_one_empty_line(
        tmp_path, monkeypatch, run_cli, grade_prose, fake_processes):
    _grader_tree(tmp_path, monkeypatch, grade_prose, fake_processes,
                 "BEGIN GRADES\nA1: PASS - blue\nVERDICT: PASS\nEND GRADES\n")

    grading = grade_prose.grade_unit("REQUIREMENTS.md", "unit.md")
    code, out, err = run_cli(grade_prose, ["REQUIREMENTS.md", "unit.md"], cwd=tmp_path)

    assert (grading.code, grading.verdict, grading.failing, grading.lines, grading.out) == (0, "PASS", (), (), "\n")
    assert (code, out) == (0, grading.out), err


def test_in_a_tree_holding_grade_prose_py_a_pass_through_a_non_default_reader_signs_the_text_that_reader_returned_under_the_trees_formula_3891(
        tmp_path, monkeypatch, grade_prose, fake_processes):
    _grader_tree(tmp_path, monkeypatch, grade_prose, fake_processes,
                 "BEGIN GRADES\nA1: PASS - blue\nVERDICT: PASS\nEND GRADES\n")
    tree_module = tmp_path / "skills" / "tdd" / "scripts" / "veri" / "grade_prose.py"
    tree_module.parent.mkdir()
    with open(grade_prose.__file__, encoding="utf-8") as f:
        tree_module.write_text(f.read() + "\n\nSCRIPTS = %r\n_running_stamp = stamp\n\n\ndef stamp(parts):\n"
                               "    return _running_stamp(parts + [\"tree-formula\"])\n"
                               % str(tmp_path / "skills" / "tdd" / "scripts"))
    claims = grade_prose.requirements.claims("REQUIREMENTS.md", "unit.md")
    under_tree_formula = {grade_prose.stamp([text, claims, "sonnet-4", "tree-formula"]): text
                          for text in ("The default branch says blue.\n", "The working tree says green.\n")}

    grading = grade_prose.grade_unit("REQUIREMENTS.md", "unit.md", read=lambda file: "The default branch says blue.\n")

    graded = tmp_path / "GRADED"
    fields = graded.read_text().split() if graded.exists() else []
    signed = under_tree_formula.get(fields[1], fields[1]) if len(fields) > 1 else None
    assert (grading.code, fields[:1], signed) == (0, ["unit.md"], "The default branch says blue.\n")


def _tree_whose_signature_takes_no_text(tmp_path, grade_prose):
    """Gives the tree its own grade_prose.py, signing under its own formula with a signature() that takes no text."""
    tree_module = tmp_path / "skills" / "tdd" / "scripts" / "veri" / "grade_prose.py"
    tree_module.parent.mkdir()
    with open(grade_prose.__file__, encoding="utf-8") as f:
        tree_module.write_text(f.read() + "\n\nSCRIPTS = %r\n\n\ndef signature(path, unit):\n"
                               "    return stamp([unit_text(unit), requirements.claims(path, unit), grader_model(), "
                               "\"tree-formula\"])\n" % str(tmp_path / "skills" / "tdd" / "scripts"))


def test_a_pass_through_the_default_reader_in_a_tree_whose_signature_takes_no_text_still_writes_that_trees_signature_3891(
        tmp_path, monkeypatch, capsys, grade_prose, fake_processes):
    _grader_tree(tmp_path, monkeypatch, grade_prose, fake_processes,
                 "BEGIN GRADES\nA1: PASS - blue\nVERDICT: PASS\nEND GRADES\n")
    _tree_whose_signature_takes_no_text(tmp_path, grade_prose)
    claims = grade_prose.requirements.claims("REQUIREMENTS.md", "unit.md")
    trees = grade_prose.stamp(["The working tree says green.\n", claims, "sonnet-4", "tree-formula"])

    grading = grade_prose.grade_unit("REQUIREMENTS.md", "unit.md")

    graded = tmp_path / "GRADED"
    fields = graded.read_text().split() if graded.exists() else []
    assert (grading.code, fields[:2]) == (0, ["unit.md", trees]), capsys.readouterr().err


def test_a_pass_through_a_non_default_reader_in_a_tree_whose_signature_takes_no_text_exits_2_and_writes_no_signature_3891(
        tmp_path, monkeypatch, capsys, grade_prose, fake_processes):
    _grader_tree(tmp_path, monkeypatch, grade_prose, fake_processes,
                 "BEGIN GRADES\nA1: PASS - blue\nVERDICT: PASS\nEND GRADES\n")
    _tree_whose_signature_takes_no_text(tmp_path, grade_prose)

    grading = grade_prose.grade_unit("REQUIREMENTS.md", "unit.md", read=lambda file: "The default branch says blue.\n")

    err = capsys.readouterr().err
    named = ("signature-formula-disagreement" in err, "unit.md" in err)
    assert (grading.code, grading.out, named, (tmp_path / "GRADED").exists()) == (2, "", (True, True), False), err


def test_4336_convert_reads_each_requirements_md_once_per_call_and_writes_the_signatures_signature_gives(
        tmp_path, monkeypatch, grade_prose):
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.chdir(tmp_path)
    colours = {"a.md": "blue", "b.md": "red", "c.md": "green"}
    for unit, colour in colours.items():
        (tmp_path / unit).write_text("The widget is painted a deep %s.\n" % colour)
    (tmp_path / "REQUIREMENTS.md").write_text("".join(
        "## %s\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is %s. | because |\n\n" % (unit, colour)
        for unit, colour in colours.items()))
    signatures = {unit: grade_prose.signature("REQUIREMENTS.md", unit) for unit in colours}
    (tmp_path / "GRADED").write_text("".join(
        "%s %s 2026-11-18 grading-id 0123456789ab\n" % (unit, sig) for unit, sig in signatures.items()))
    reads = []
    read_lines = grade_prose.requirements.read_lines

    def counted(path):
        reads.append(path)
        return read_lines(path)

    monkeypatch.setattr(grade_prose.requirements, "read_lines", counted)

    grade_prose.convert("REQUIREMENTS.md")

    written = {line.split(" ")[0]: line.split(" ")[1] for line in (tmp_path / "GRADED").read_text().splitlines()}
    literal = {"a.md": "f361d178d1bf7ebb72a81b0081587b3f694b6e7676453da140311f85bba28073",
               "b.md": "bd3a689ff880c6005450fa5f777a1a7ef89c1c534bdc489060f986d6577743e8",
               "c.md": "a8f7db1812d4fa5debc7f7f069a3664c4a2ac29e448f084ef7444045f7135729"}
    assert (reads.count("REQUIREMENTS.md"), written == signatures, written == literal) == (1, True, True), (
        reads, written, signatures)


def test_4336_a_tree_grade_prose_py_byte_equal_to_the_running_module_signs_through_it_once_per_unit_under_convert(
        tmp_path, monkeypatch, grade_prose):
    tree_module = tmp_path / "skills" / "tdd" / "scripts" / "veri" / "grade_prose.py"
    tree_module.parent.mkdir(parents=True)
    with open(grade_prose.__file__, "rb") as f:
        tree_module.write_bytes(f.read())
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.chdir(tmp_path)
    colours = {"a.md": "blue", "b.md": "red", "c.md": "green"}
    for unit, colour in colours.items():
        (tmp_path / unit).write_text("The widget is painted a deep %s.\n" % colour)
    (tmp_path / "REQUIREMENTS.md").write_text("".join(
        "## %s\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is %s. | because |\n\n" % (unit, colour)
        for unit, colour in colours.items()))
    (tmp_path / "GRADED").write_text("".join(
        "%s %s 2026-11-18 grading-id 0123456789ab\n" % (unit, grade_prose.signature("REQUIREMENTS.md", unit))
        for unit in colours))
    signed = []
    signature = grade_prose.signature

    def counted(path, unit, text=None, units=None):
        signed.append(unit)
        return signature(path, unit, text, units)

    monkeypatch.setattr(grade_prose, "signature", counted)

    grade_prose.convert("REQUIREMENTS.md")

    assert (grade_prose.signer() is grade_prose, sorted(signed)) == (True, ["a.md", "b.md", "c.md"]), signed


SIG = " %s 2026-11-19 id prefix\n"


def test_4429_signed_units_decodes_a_heading_unit_and_finds_its_requirements_beside_the_file_named_before_the_hash(
        grade_prose):
    head = {"skills/tdd/GRADED": "skills/tdd/SKILL.md#Two%20words" + SIG % ("a" * 64)
            + "skills/tdd/SKILL.md#100%25%20a/b" + SIG % ("b" * 64)
            + "skills/tdd/SKILL.md#a%2520b" + SIG % ("c" * 64)}

    assert grade_prose.signed_units({}, head) == [
        ("skills/tdd/REQUIREMENTS.md", "skills/tdd/SKILL.md#Two words"),
        ("skills/tdd/REQUIREMENTS.md", "skills/tdd/SKILL.md#100% a/b"),
        ("skills/tdd/REQUIREMENTS.md", "skills/tdd/SKILL.md#a%20b")]


def test_4429_signed_units_lists_a_root_unit_beside_the_root_requirements_and_a_prompt_beside_its_own(grade_prose):
    head = {"GRADED": "README.md" + SIG % "c",
            "skills/tdd/GRADED": "skills/tdd/scripts/prompts/x.md" + SIG % "d"}

    assert grade_prose.signed_units({}, head) == [
        ("REQUIREMENTS.md", "README.md"), ("skills/tdd/scripts/prompts/REQUIREMENTS.md", "skills/tdd/scripts/prompts/x.md")]


def test_4429_signed_units_leaves_out_a_line_the_merge_base_holds_even_duplicated_but_lists_a_re_signed_one_once(
        grade_prose):
    main = "skills/tdd/SKILL.md#Kept%20heading" + SIG % "e"
    base = {"skills/tdd/GRADED": main + "skills/tdd/SKILL.md" + SIG % "f"}
    head = {"skills/tdd/GRADED": main + "skills/tdd/SKILL.md" + SIG % "g" + main + "skills/tdd/SKILL.md" + SIG % "g"}

    assert grade_prose.signed_units(base, head) == [("skills/tdd/REQUIREMENTS.md", "skills/tdd/SKILL.md")]


@pytest.mark.parametrize("argv", [["--signed"], ["--signed", "a", "b"]])
def test_4429_signed_without_exactly_one_base_exits_2_with_its_usage_starting_nothing(run_cli, grade_prose, fake_processes,
                                                                                      argv):
    fake = fake_processes.answers({})

    code, out, err = run_cli(grade_prose, argv)

    assert (code, out, "--signed <base>" in err, fake.argvs) == (2, "", True, []), err


def test_4429_signed_units_lists_no_unit_for_a_blank_line_in_a_graded_file(grade_prose):
    head = {"skills/tdd/GRADED": "\n" + "skills/tdd/SKILL.md" + SIG % "h" + "\n"}

    assert grade_prose.signed_units({}, head) == [("skills/tdd/REQUIREMENTS.md", "skills/tdd/SKILL.md")]
