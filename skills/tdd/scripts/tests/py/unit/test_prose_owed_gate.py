"""The make unit gate for prose grades, read as the Makefile's text."""
import re
from pathlib import Path

MAKEFILE = Path(__file__).resolve().parents[6] / "Makefile"


def recipe(targets):
    lines, inside = [], False
    for line in MAKEFILE.read_text().split("\n"):
        if line.startswith(targets + ":"):
            inside = True
        elif inside and line.startswith("\t"):
            lines.append(line)
        elif inside and line.strip():
            break
    return "\n".join(lines).replace("\\\n", " ")


def test_make_unit_fails_naming_each_unit_prose_owed_sh_prints_when_it_prints_anything():
    text = recipe("test unit")
    assert text, "the Makefile has no 'test unit' recipe"
    run = re.search(r"skills/tdd/scripts/prose-owed\.sh \. *(?P<tail>[^;]*);", text)
    assert run, "the unit recipe never runs prose-owed.sh on the repository root"
    assert re.fullmatch(r"\|\| *fail=1 *", run["tail"]), "a non-zero prose-owed.sh exit does not fail the run, or its output is redirected: %r" % run["tail"]
    assert "SUITES FAILED" in text and "exit 1" in text, "a failed leg does not end the recipe red"


def test_prose_owed_sh_run_in_process_with_process_launches_spied_records_no_launch(tmp_path, monkeypatch, run_cli):
    import importlib
    import subprocess

    prose_owed = importlib.import_module("veri.prose_owed")
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    launched = []
    monkeypatch.setattr(subprocess, "run", lambda argv, *a, **k: launched.append(argv))
    monkeypatch.setattr(subprocess, "Popen", lambda argv, *a, **k: launched.append(argv))

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out.split(), launched) == (1, ["skills/demo/SKILL.md"], []), (code, out, launched, err)


def test_prose_owed_sh_given_a_list_repeating_an_id_exits_2_naming_the_list_and_the_duplicate_1911(tmp_path, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A1 | The widget is round. | because |\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert code == 2 and "REQUIREMENTS.md" in err and "duplicate ID" in err, (code, out, err)


def test_prose_owed_sh_given_a_list_whose_header_lacks_a_column_exits_2_naming_the_list_and_the_defect_1911(tmp_path, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n| ID | Requirement |\n|---|---|\n| A1 | The widget is blue. |\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert code == 2 and "REQUIREMENTS.md" in err and "header lacks a column" in err, (code, out, err)


def test_prose_owed_sh_reads_a_nested_units_signature_from_the_skills_graded_file_1911(tmp_path, monkeypatch, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    grade_prose = importlib.import_module("veri.grade_prose")
    (tmp_path / "skills" / "demo" / "prompts").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "prompts" / "x.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/prompts/x.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    monkeypatch.chdir(tmp_path)
    sig = grade_prose.signature("REQUIREMENTS.md", "skills/demo/prompts/x.md")
    (tmp_path / "skills" / "demo" / "GRADED").write_text("skills/demo/prompts/x.md %s g1\n" % sig)

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out) == (0, ""), (code, out, err)


def test_prose_owed_sh_prints_a_unit_listed_only_in_a_requirements_list_beside_it_with_no_graded_line_1911(tmp_path, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "skills" / "demo" / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out.split()) == (1, ["skills/demo/SKILL.md"]), (code, out, err)


def test_prose_owed_sh_given_a_list_written_as_a_table_without_leading_or_trailing_pipes_prints_the_unsigned_unit_and_exits_1_1931(tmp_path, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\nID | Requirement | Why\n---|---|---\nA1 | The widget is blue. | because\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out.split()) == (1, ["skills/demo/SKILL.md"]), (code, out, err)


def test_prose_owed_sh_reads_a_table_indented_by_three_spaces_as_the_same_list_1931(tmp_path, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n   | ID | Requirement | Why |\n   |---|---|---|\n   | A1 | The widget is blue. | because |\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out.split()) == (1, ["skills/demo/SKILL.md"]), (code, out, err)


def test_prose_owed_sh_reads_a_requirements_list_beside_a_nested_unit_and_prints_the_unsigned_unit_1931(tmp_path, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    (tmp_path / "skills" / "demo" / "prompts").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "prompts" / "P.md").write_text("The widget is blue.\n")
    (tmp_path / "skills" / "demo" / "prompts" / "REQUIREMENTS.md").write_text(
        "## skills/demo/prompts/P.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out.split()) == (1, ["skills/demo/prompts/P.md"]), (code, out, err)


def test_prose_owed_sh_prints_a_graded_unit_outside_skills_after_its_prose_changes_by_one_byte_2025(tmp_path, monkeypatch, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    grade_prose = importlib.import_module("veri.grade_prose")
    (tmp_path / "operator").mkdir()
    (tmp_path / "operator" / "PRINCIPLES.md").write_text("The widget is blue.\n")
    (tmp_path / "operator" / "REQUIREMENTS.md").write_text(
        "## operator/PRINCIPLES.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    monkeypatch.chdir(tmp_path)
    sig = grade_prose.signature("operator/REQUIREMENTS.md", "operator/PRINCIPLES.md")
    (tmp_path / "operator" / "GRADED").write_text("operator/PRINCIPLES.md %s g1\n" % sig)
    (tmp_path / "operator" / "PRINCIPLES.md").write_text("The widget is blue!\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out.split()) == (1, ["operator/PRINCIPLES.md"]), (code, out, err)
