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


def test_prose_owed_sh_prints_an_orphan_for_a_unit_in_a_graded_file_outside_skills_that_no_list_names_2025(tmp_path, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    (tmp_path / "operator").mkdir()
    (tmp_path / "operator" / "GRADED").write_text("operator/GONE.md deadbeef g1\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out.split("\n")[:-1]) == (1, ["operator/GONE.md (orphan)"]), (code, out, err)


def test_prose_owed_sh_after_a_units_text_or_its_requirement_rows_change_prints_that_unit_and_only_that_unit_2474(tmp_path, monkeypatch, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    grade_prose = importlib.import_module("veri.grade_prose")
    one, two = "skills/demo/one.md", "skills/demo/two.md"
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / one).write_text("The widget is blue.\n")
    (tmp_path / two).write_text("The gadget is red.\n")

    def table(unit, claim):
        return "## %s\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | %s | because |\n\n" % (unit, claim)

    def write_list(claim_two):
        (tmp_path / "REQUIREMENTS.md").write_text(table(one, "The widget is blue.") + table(two, claim_two))

    write_list("The gadget is red.")
    monkeypatch.chdir(tmp_path)
    sigs = {u: grade_prose.signature("REQUIREMENTS.md", u) for u in (one, two)}
    (tmp_path / "skills" / "demo" / "GRADED").write_text("".join("%s %s g1\n" % (u, s) for u, s in sigs.items()))
    assert run_cli(prose_owed, [str(tmp_path)])[:2] == (0, "")

    (tmp_path / one).write_text("The widget is green.\n")
    code, out, err = run_cli(prose_owed, [str(tmp_path)])
    assert (code, out.split()) == (1, [one]), (code, out, err)

    (tmp_path / one).write_text("The widget is blue.\n")
    write_list("The gadget is round.")
    code, out, err = run_cli(prose_owed, [str(tmp_path)])
    assert (code, out.split()) == (1, [two]), (code, out, err)


def test_prose_owed_sh_stays_at_exit_0_after_an_edit_to_the_grader_instructions_2474(tmp_path, monkeypatch, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    # prose_owed does `import grade_prose`, so its grader is a different module object
    # from veri.grade_prose: sign and patch through the one it actually calls.
    grade_prose = prose_owed.grade_prose
    unit = "skills/demo/one.md"
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / unit).write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## %s\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n" % unit)
    monkeypatch.chdir(tmp_path)
    grade_prose.record_graded(unit, grade_prose.signature("REQUIREMENTS.md", unit), "g1")
    assert run_cli(prose_owed, [str(tmp_path)])[:2] == (0, "")

    monkeypatch.setattr(grade_prose, "GRADER_INSTRUCTIONS",
                        grade_prose.GRADER_INSTRUCTIONS + "\nAlso weigh the prose's brevity.\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])
    assert (code, out) == (0, ""), (code, out, err)

    # The exit 0 above is only worth having if this gate is live on this very unit:
    # exit 0 is also what an empty sweep returns, so prove the unit is being graded.
    (tmp_path / unit).write_text("The widget is green.\n")
    code, out, err = run_cli(prose_owed, [str(tmp_path)])
    assert (code, out.split()) == (1, [unit]), (code, out, err)


def test_prose_owed_sh_prints_an_orphan_for_a_unit_in_a_root_graded_file_that_no_list_names_2674(tmp_path, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    (tmp_path / "GRADED").write_text("CLAUDE.md deadbeef g1\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out.split("\n")[:-1]) == (1, ["CLAUDE.md (orphan)"]), (code, out, err)


def test_prose_owed_sh_prints_an_orphan_for_a_unit_in_a_docs_adr_graded_file_that_no_list_names_2674(tmp_path, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "docs" / "adr" / "GRADED").write_text("docs/adr/0001-gone.md deadbeef g1\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out.split("\n")[:-1]) == (1, ["docs/adr/0001-gone.md (orphan)"]), (code, out, err)


def test_prose_owed_sh_prints_a_unit_listed_in_docs_adr_requirements_with_no_graded_signature_2674(tmp_path, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "docs" / "adr" / "0001-demo.md").write_text("The widget is blue.\n")
    (tmp_path / "docs" / "adr" / "REQUIREMENTS.md").write_text(
        "## docs/adr/0001-demo.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out.split()) == (1, ["docs/adr/0001-demo.md"]), (code, out, err)


def test_prose_owed_sh_prints_a_unit_listed_in_a_requirements_file_three_levels_deep_with_no_graded_signature_2674(tmp_path, run_cli):
    import importlib

    prose_owed = importlib.import_module("veri.prose_owed")
    (tmp_path / "docs" / "x" / "y").mkdir(parents=True)
    (tmp_path / "docs" / "x" / "y" / "note.md").write_text("The widget is blue.\n")
    (tmp_path / "docs" / "x" / "y" / "REQUIREMENTS.md").write_text(
        "## docs/x/y/note.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")

    code, out, err = run_cli(prose_owed, [str(tmp_path)])

    assert (code, out.split()) == (1, ["docs/x/y/note.md"]), (code, out, err)
