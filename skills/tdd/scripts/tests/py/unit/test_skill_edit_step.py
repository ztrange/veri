"""In-process cases for veri/skill_edit_step.py, the module skill-edit-step.sh is a shim over."""
import importlib
import json


def test_apply_adds_the_issue_rows_the_units_list_lacks_at_its_end_and_no_row_the_issue_does_not_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "other.md").write_text("Other unit.\n")
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    requirements = importlib.import_module("veri.requirements")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n\n"
        "## other.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| B1 | Other. | o |\n")
    (tmp_path / "issue.md").write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A3 | The widget is shiny. | gloss |\n\n"
        "### other.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| B2 | Not ours. | n |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    ids = [row.split("\t")[0] for row in requirements.claims(str(tmp_path / "REQUIREMENTS.md"), "unit.md").splitlines()]
    assert ids == ["A1", "A2", "A3"], ids


def test_apply_rewords_a_row_the_list_already_holds_in_place_keeping_its_id_and_position(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n"
        "| A3 | The widget is shiny. | gloss |\n")
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget is square. | corners |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [l for l in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("| A")]
    assert rows == [
        "| A1 | The widget is blue. | because |",
        "| A2 | The widget is square. | corners |",
        "| A3 | The widget is shiny. | gloss |",
    ], rows


def test_apply_drops_the_row_an_issue_marks_dropped_and_renumbers_no_other_row(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n"
        "| A3 | The widget is shiny. | gloss |\n")
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | (dropped) | no longer wanted |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [l for l in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("| A")]
    assert rows == [
        "| A1 | The widget is blue. | because |",
        "| A3 | The widget is shiny. | gloss |",
    ], rows


def test_apply_leaves_the_list_byte_for_byte_when_the_issue_has_no_requirements_section_or_none_for_the_unit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "other.md").write_text("Other unit.\n")
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    original = (
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n\n"
        "## other.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| B1 | Other. | o |\n")
    bodies = [
        "## Problem\n\nNothing stated here.\n",
        "## Requirements\n\n### other.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| B2 | Not ours. | n |\n",
    ]
    for body in bodies:
        (tmp_path / "REQUIREMENTS.md").write_bytes(original.encode())
        (tmp_path / "issue.md").write_text(body)

        skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

        assert (tmp_path / "REQUIREMENTS.md").read_bytes() == original.encode(), body


def test_apply_creates_a_new_unit_empty_and_its_section_in_a_requirements_list_it_creates(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md (new)\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    assert (tmp_path / "unit.md").read_bytes() == b""
    rows = [l for l in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("|")]
    assert rows[2:] == [
        "| A1 | The widget is blue. | because |",
        "| A2 | The widget is round. | shape |",
    ], rows
    assert "## unit.md" in (tmp_path / "REQUIREMENTS.md").read_text().splitlines()


def test_apply_keeps_the_sections_of_an_existing_requirements_list_when_it_creates_a_new_unit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    other = ("## other.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
             "| B1 | The gadget hums. | sound |\n")
    (tmp_path / "REQUIREMENTS.md").write_text(other)
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md (new)\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    text = (tmp_path / "REQUIREMENTS.md").read_text()
    assert text.startswith(other), text
    assert "## unit.md" in text.splitlines(), text
    assert "| A1 | The widget is blue. | because |" in text.splitlines(), text


def test_a_veri_skill_edit_budget_that_is_not_a_whole_number_of_at_least_one_exits_2_before_any_grading_or_launch_and_the_shim_header_names_it(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    from conftest import SCRIPTS
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    calls = []
    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: calls.append("grade") or (1, "A1: FAIL - no\n"))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: calls.append("author") or 0)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: calls.append("guard") or 0)
    fake = types.SimpleNamespace(
        run=lambda cmd, **kw: calls.append(" ".join(cmd[:2])) or subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""),
        PIPE=subprocess.PIPE)
    monkeypatch.setattr(skill_edit_step, "subprocess", fake)

    codes = {}
    for budget in ["", "0", "-1", "two", "1.5"]:
        codes[budget] = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"],
                                env={"VERI_SKILL_EDIT_BUDGET": budget})[0]

    header = (SCRIPTS / "skill-edit-step.sh").read_text().split("exec ")[0]
    assert (codes, calls, "VERI_SKILL_EDIT_BUDGET" in header) \
        == ({b: 2 for b in ["", "0", "-1", "two", "1.5"]}, [], True), (codes, calls)


def test_a_guard_exit_2_exits_the_step_2_signing_nothing_and_committing_nothing(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    grades = iter([(1, "A1: FAIL - no\n"), (0, "")])
    gits = []
    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: next(grades))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: 0)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 2)
    fake = types.SimpleNamespace(
        run=lambda cmd, **kw: gits.append(cmd[:2]) or subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""),
        PIPE=subprocess.PIPE)
    monkeypatch.setattr(skill_edit_step, "subprocess", fake)

    code = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])[0]

    assert (code, [g for g in gits if g[1] in ("add", "commit")], (tmp_path / "GRADED").exists()) == (2, [], False), (code, gits)


def test_the_author_attempts_follow_veri_skill_edit_budget_alone_whatever_the_other_five_budgets_say(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    authors = []
    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (1, "A1: FAIL - no\n"))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: authors.append(a) or 0)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)
    fake = types.SimpleNamespace(
        run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""),
        PIPE=subprocess.PIPE)
    monkeypatch.setattr(skill_edit_step, "subprocess", fake)
    others = {"REVISE_BUDGET": "7", "VERI_STUCK_RETRIES": "8", "VERI_NO_VERDICT_RETRIES": "9",
              "VERI_REFACTOR_BUDGET": "10", "VERI_STEP_GROWTH": "11"}

    code = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"],
                   env={**others, "VERI_SKILL_EDIT_BUDGET": "2"})[0]

    assert (code, len(authors)) == (1, 2), (code, len(authors))


def test_apply_reads_no_rows_for_a_unit_below_the_root_under_a_heading_holding_only_its_basename_1959(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    original = (
        "## SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    (tmp_path / "sub" / "REQUIREMENTS.md").write_bytes(original.encode())
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget is round. | shape |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "sub/SKILL.md")

    assert (tmp_path / "sub" / "REQUIREMENTS.md").read_bytes() == original.encode()


def test_apply_adds_the_rows_under_a_repo_relative_path_heading_to_the_list_beside_a_unit_below_the_root_1959(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "skills" / "vdev").mkdir(parents=True)
    (tmp_path / "skills" / "vdev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").write_text(
        "## skills/vdev/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### skills/vdev/SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget is round. | shape |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/vdev/SKILL.md")

    rows = [l for l in (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("| A")]
    assert rows == [
        "| A1 | The widget is blue. | because |",
        "| A2 | The widget is round. | shape |",
    ], rows


def test_apply_reads_no_rows_for_a_unit_under_a_heading_naming_a_different_units_repo_relative_path_1959(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "skills" / "vdev").mkdir(parents=True)
    (tmp_path / "skills" / "vdev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    original = (
        "## SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").write_bytes(original.encode())
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### skills/other/SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget is round. | shape |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/vdev/SKILL.md")

    assert (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").read_bytes() == original.encode()


def test_a_unit_with_no_requirements_list_run_against_an_issue_with_no_requirements_section_is_left_unchanged_and_exits_3_1959(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    fake = types.SimpleNamespace(
        run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""),
        PIPE=subprocess.PIPE)
    monkeypatch.setattr(skill_edit_step, "subprocess", fake)

    code = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])[0]

    assert (code, (tmp_path / "unit.md").read_bytes()) == (3, b"The widget is painted a deep blue.\n")


def test_apply_makes_the_issue_rows_the_new_list_beside_a_unit_with_no_requirements_list_1959(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "skills" / "vdev").mkdir(parents=True)
    (tmp_path / "skills" / "vdev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### skills/vdev/SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/vdev/SKILL.md")

    rows = [l for l in (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("| A")]
    assert rows == ["| A1 | The widget is blue. | because |"], rows


def test_a_unit_with_no_table_whose_requirements_list_holds_only_another_units_section_run_against_an_issue_stating_no_rows_for_it_exits_3_leaving_the_list_byte_identical_1959(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "skills" / "vdev").mkdir(parents=True)
    (tmp_path / "skills" / "vdev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    original = ("## skills/other/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| B1 | The gadget is red. | colour |\n")
    (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").write_text(original)
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    fake = types.SimpleNamespace(
        run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""),
        PIPE=subprocess.PIPE)
    monkeypatch.setattr(skill_edit_step, "subprocess", fake)

    code, _, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "skills/vdev/SKILL.md"])

    assert (code, (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").read_bytes()) == (3, original.encode()), err


def test_apply_appends_the_issue_rows_as_a_new_section_beside_a_list_holding_only_another_units_section_1959(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "skills" / "vdev").mkdir(parents=True)
    (tmp_path / "skills" / "vdev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    other = ("## skills/other/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
             "| B1 | The gadget is red. | colour |\n")
    listing = tmp_path / "skills" / "vdev" / "REQUIREMENTS.md"
    listing.write_text(other)
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### skills/vdev/SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/vdev/SKILL.md")

    text = listing.read_text()
    assert text.startswith(other), text
    assert "## skills/vdev/SKILL.md" in text.splitlines(), text
    assert "| A1 | The widget is blue. | because |" in text.splitlines(), text


def test_apply_moves_a_units_own_table_into_a_list_holding_only_another_units_section_leaving_that_section_unchanged_1959(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "skills" / "vdev").mkdir(parents=True)
    unit = tmp_path / "skills" / "vdev" / "SKILL.md"
    unit.write_text(
        "Prose.\n\n## Requirements\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    other = ("## skills/other/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
             "| B1 | The gadget is red. | colour |\n")
    listing = tmp_path / "skills" / "vdev" / "REQUIREMENTS.md"
    listing.write_text(other)
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/vdev/SKILL.md")

    text = listing.read_text()
    assert text.startswith(other), text
    assert "## skills/vdev/SKILL.md" in text.splitlines(), text
    assert "| A1 | The widget is blue. | because |" in text.splitlines(), text
    assert "## Requirements" not in unit.read_text().splitlines(), unit.read_text()


def test_a_guard_rejected_attempts_edits_to_the_unit_are_reset_before_the_next_author_attempt_1959(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    unit = tmp_path / "unit.md"
    unit.write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    seen = []

    def author(*a):
        seen.append(unit.read_text())
        unit.write_text("Edited by attempt %d.\n" % len(seen))
        return 0

    def guard(argv):
        print("stray.md")
        return 0

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (1, "A1: FAIL - no\n"))
    monkeypatch.setattr(skill_edit_step, "_author", author)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", guard)
    fake = types.SimpleNamespace(
        run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""),
        PIPE=subprocess.PIPE)
    monkeypatch.setattr(skill_edit_step, "subprocess", fake)

    run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"], env={"VERI_SKILL_EDIT_BUDGET": "2"})

    assert seen == ["The widget is painted a deep blue.\n"] * 2, seen


def test_a_list_already_passing_the_grader_launches_no_author_commits_the_list_and_graded_and_exits_3_1959(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    launched = []
    commands = []

    def run(cmd, **kw):
        commands.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: launched.append(a) or 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step, "subprocess",
                        types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert launched == [], launched
    assert len(commits) == 1 and "REQUIREMENTS.md" in commits[0], commands
    assert any(p.endswith("GRADED") or "GRADED" in p for p in commits[0]), commits
    assert code == 3, (code, out, err)


def test_an_added_step_on_a_unit_graded_pass_before_any_author_ran_exits_2_naming_the_step_launching_and_committing_nothing_2063(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    launched = []
    commands = []
    events = []

    def run(cmd, **kw):
        commands.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: launched.append(a) or 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: events.append(a))
    monkeypatch.setattr(skill_edit_step, "subprocess",
                        types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))
    step = "map each grade to the mode stop-run.sh accepts"

    code, out, err = run_cli(skill_edit_step, ["--added", step, str(tmp_path / "issue.md"), "unit.md"])
    usage = run_cli(skill_edit_step, [])[2]

    commits = [c for c in commands if c[:2] in (["git", "add"], ["git", "commit"])]
    assert (code, step in err, launched, events, commits, (tmp_path / "GRADED").exists(), "--added" in usage) \
        == (2, True, [], [], [], False, True), (code, err, launched, events, commits, usage)


def test_an_added_step_stating_a_row_new_to_the_list_on_a_unit_graded_pass_launches_no_author_commits_the_row_and_graded_and_exits_3_2513(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    prose = "The widget is painted a deep blue and round.\n"
    (tmp_path / "unit.md").write_text(prose)
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | shape |\n")
    launched = []
    commands = []

    def run(cmd, **kw):
        commands.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: launched.append(a) or 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step, "subprocess",
                        types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, ["--added", "add the round row", str(tmp_path / "issue.md"), "unit.md"])

    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert launched == [], launched
    assert (tmp_path / "unit.md").read_text() == prose
    assert "A2" in (tmp_path / "REQUIREMENTS.md").read_text()
    assert len(commits) == 1 and "REQUIREMENTS.md" in commits[0] and any("GRADED" in p for p in commits[0]), commands
    assert code == 3, (code, out, err)


def test_an_added_step_stating_only_rows_the_list_already_carries_on_a_unit_graded_pass_exits_2_naming_the_step_leaving_list_unit_and_graded_unmodified_2583(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    prose = "The widget is painted a deep blue.\n"
    listing = "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"
    (tmp_path / "unit.md").write_text(prose)
    (tmp_path / "REQUIREMENTS.md").write_text(listing)
    (tmp_path / "issue.md").write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    launched = []
    commands = []

    def run(cmd, **kw):
        commands.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: launched.append(a) or 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step, "subprocess",
                        types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))
    step = "restate the blue row"

    code, out, err = run_cli(skill_edit_step, ["--added", step, str(tmp_path / "issue.md"), "unit.md"])

    commits = [c for c in commands if c[:2] in (["git", "add"], ["git", "commit"])]
    assert (code, step in err, launched, commits, (tmp_path / "GRADED").exists()) == (2, True, [], [], False), \
        (code, err, launched, commits)
    assert (tmp_path / "REQUIREMENTS.md").read_text() == listing
    assert (tmp_path / "unit.md").read_text() == prose


def test_an_added_step_on_a_unit_whose_grade_fails_first_runs_its_author_attempt_commits_the_list_graded_and_unit_and_exits_0_2063(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    launched = []
    commands = []
    grades = [(1, "A1: FAIL - no\n"), (0, "")]

    def run(cmd, **kw):
        commands.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: grades.pop(0))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: launched.append(a) or 0)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step, "subprocess",
                        types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, ["--added", "map each grade to a mode", str(tmp_path / "issue.md"), "unit.md"])

    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert len(launched) == 1 and code == 0, (code, err, launched)
    assert len(commits) == 1 and all(any(n in p for p in commits[0]) for n in ("REQUIREMENTS.md", "GRADED", "unit.md")), commands


def test_the_author_prompt_names_every_pin_file_and_tells_it_to_update_the_checksum_or_verbatim_pins_there_2232(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    prompts = []

    def run(cmd, **kw):
        if cmd[0].endswith("supervise.sh"):
            prompts.append(open(cmd[3]).read())
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(subprocess, "run", run)
    for pins in (["tests/test_alpha.py", "tests/test_beta.py"], []):
        grades = iter([(1, "A1: FAIL - no\n"), (0, "")])
        monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: next(grades))
        run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md", *pins])

    with_pins, without = prompts
    assert (all(p in with_pins for p in ["tests/test_alpha.py", "tests/test_beta.py", "checksum", "verbatim"]),
            "tests/test_" in without) == (True, False), (with_pins, without)


def test_a_rejected_attempts_edits_to_a_pin_file_are_reset_with_the_unit_so_the_committed_pin_matches_the_committed_unit_2232(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is blue.\n")
    (tmp_path / "pin.py").write_text("PINNED = 'The widget is blue.'\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget hums. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    committed = []
    grades = [(1, "A1: FAIL - silent\n"), (1, "A1: FAIL - red is wrong\n"), (0, "")]
    attempts = iter([
        lambda: ((tmp_path / "unit.md").write_text("The widget is red.\n"),
                 (tmp_path / "pin.py").write_text("PINNED = 'The widget is red.'\n")),
        lambda: (tmp_path / "unit.md").write_text((tmp_path / "unit.md").read_text() + "It hums.\n"),
    ])

    def run(cmd, **kw):
        if cmd[:2] == ["git", "commit"]:
            committed.append(((tmp_path / "unit.md").read_text(), (tmp_path / "pin.py").read_text()))
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: grades.pop(0))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: next(attempts)() and 0)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step, "subprocess",
                        types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md", "pin.py"])

    assert (code, committed) == (0, [("The widget is blue.\nIt hums.\n", "PINNED = 'The widget is blue.'\n")]), (code, err)


def test_an_added_step_on_a_unit_no_requirements_list_claims_exits_2_naming_the_step_launching_and_committing_nothing_2236(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    launched = []
    commands = []

    def run(cmd, **kw):
        commands.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: launched.append(a) or 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step, "subprocess",
                        types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))
    step = "map each grade to the mode stop-run.sh accepts"

    code, out, err = run_cli(skill_edit_step, ["--added", step, str(tmp_path / "issue.md"), "unit.md"])

    commits = [c for c in commands if c[:2] in (["git", "add"], ["git", "commit"])]
    assert (code, step in err, launched, commits) == (2, True, [], []), (code, err, launched, commits)


def _next_case_2262(tmp_path, monkeypatch, list_rows, issue_rows, heading="unit.md"):
    """A unit, its list holding list_rows (None: no list), and an issue stating issue_rows under heading.

    A heading ending " (new)" names a unit that does not exist yet, so no unit.md is written.
    """
    monkeypatch.chdir(tmp_path)
    if not heading.endswith(" (new)"):
        (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    table = "| ID | Requirement | Why |\n|---|---|---|\n"
    if list_rows is not None:
        (tmp_path / "REQUIREMENTS.md").write_text("## unit.md\n\n" + table + "".join(r + "\n" for r in list_rows))
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### %s\n\n" % heading + table + "".join(r + "\n" for r in issue_rows))
    return importlib.import_module("veri.skill_edit_step")


def test_apply_gives_a_prefix_next_row_the_next_free_number_for_its_prefix_and_copies_a_numbered_row_as_is_2262(tmp_path, monkeypatch):
    skill_edit_step = _next_case_2262(
        tmp_path, monkeypatch,
        ["| PL3 | The widget is blue. | because |",
         "| PL7 | The widget is round. | shape |",
         "| CY9 | The widget is old. | age |"],
        ["| PL<next> | The widget is shiny. | gloss |",
         "| CY12 | The widget is heavy. | weight |"])
    requirements = importlib.import_module("veri.requirements")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    ids = [row.split("\t")[0] for row in requirements.claims(str(tmp_path / "REQUIREMENTS.md"), "unit.md").splitlines()]
    assert ids == ["PL3", "PL7", "CY9", "PL8", "CY12"], ids


def test_apply_numbers_two_next_rows_of_one_prefix_in_issue_order_as_max_plus_1_then_max_plus_2_2262(tmp_path, monkeypatch):
    skill_edit_step = _next_case_2262(
        tmp_path, monkeypatch,
        ["| PL3 | The widget is blue. | because |",
         "| PL7 | The widget is round. | shape |"],
        ["| PL<next> | The widget is shiny. | gloss |",
         "| PL<next> | The widget is heavy. | weight |"])

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("| PL")]
    assert [row.split(" | ")[0] for row in rows] == ["| PL3", "| PL7", "| PL8", "| PL9"], rows
    assert ["shiny" in rows[2], "heavy" in rows[3]] == [True, True], rows


def test_apply_numbers_a_prefix_next_row_1_when_the_list_holds_no_row_of_that_prefix_including_a_list_it_creates_2262(tmp_path, monkeypatch):
    skill_edit_step = _next_case_2262(
        tmp_path, monkeypatch,
        None,
        ["| PL<next> | The widget is shiny. | gloss |"],
        heading="unit.md (new)")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [l for l in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("|")]
    assert rows[2:] == ["| PL1 | The widget is shiny. | gloss |"], rows


def test_apply_numbers_a_prefix_next_row_1_when_the_unit_exists_but_no_requirements_list_claims_it_2262(tmp_path, monkeypatch):
    skill_edit_step = _next_case_2262(
        tmp_path, monkeypatch,
        None,
        ["| PL<next> | The widget is shiny. | gloss |"])

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [l for l in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("|")]
    assert rows[2:] == ["| PL1 | The widget is shiny. | gloss |"], rows


def test_an_issue_row_whose_id_is_neither_prefix_digits_nor_prefix_next_exits_2_naming_the_id_and_leaves_the_list_byte_identical_2262(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| PL3 | The widget is blue. | because |\n")
    (tmp_path / "REQUIREMENTS.md").write_text(original)
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| PLsoon | The widget is shiny. | gloss |\n")

    def run(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step, "subprocess",
                        types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "PLsoon" in err, (tmp_path / "REQUIREMENTS.md").read_text()) == (2, True, original), (code, err)


def test_an_issue_with_rows_under_a_unit_heading_outside_requirements_exits_2_naming_the_unit_leaving_list_unit_and_graded_unchanged_2856(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "other.md").write_text("Other prose.\n")
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| PL3 | The widget is blue. | because |\n")
    (tmp_path / "REQUIREMENTS.md").write_text(original)
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### other.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| OT1 | Other is prose. | because |\n\n"
        "## unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| PL4 | The widget is shiny. | gloss |\n")

    def run(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step, "subprocess",
                        types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "unit.md" in err and "not under ## Requirements" in err,
            (tmp_path / "REQUIREMENTS.md").read_text(), (tmp_path / "unit.md").read_text(),
            (tmp_path / "GRADED").exists()) == (
        2, True, original, "The widget is painted a deep blue.\n", False), (code, err)


def test_an_issue_with_a_requirements_row_under_no_unit_heading_exits_2_naming_the_problem_leaving_list_unit_and_graded_unchanged_2856(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| PL3 | The widget is blue. | because |\n")
    (tmp_path / "REQUIREMENTS.md").write_text(original)
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| PL4 | The widget is shiny. | gloss |\n")

    def run(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step, "subprocess",
                        types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "under no ### unit heading" in err,
            (tmp_path / "REQUIREMENTS.md").read_text(), (tmp_path / "unit.md").read_text(),
            (tmp_path / "GRADED").exists()) == (
        2, True, original, "The widget is painted a deep blue.\n", False), (code, err)


def test_an_issue_with_a_requirements_section_but_no_heading_for_the_stepped_unit_exits_2_naming_the_unit_leaving_list_unit_and_graded_unchanged_2856(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "other.md").write_text("Other prose.\n")
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| PL3 | The widget is blue. | because |\n")
    (tmp_path / "REQUIREMENTS.md").write_text(original)
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### other.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| OT1 | Other is prose. | because |\n")

    def run(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step, "subprocess",
                        types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "unit.md" in err,
            (tmp_path / "REQUIREMENTS.md").read_text(), (tmp_path / "unit.md").read_text(),
            (tmp_path / "GRADED").exists()) == (
        2, True, original, "The widget is painted a deep blue.\n", False), (code, err)


def test_apply_numbers_a_prefix_next_row_past_the_max_over_the_lists_ids_and_the_issues_own_explicit_ids_2262(tmp_path, monkeypatch):
    skill_edit_step = _next_case_2262(
        tmp_path, monkeypatch,
        ["| PL5 | The widget is blue. | because |"],
        ["| PL<next> | The widget is shiny. | gloss |",
         "| PL7 | The widget is heavy. | weight |"])
    requirements = importlib.import_module("veri.requirements")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    ids = [row.split("\t")[0] for row in requirements.claims(str(tmp_path / "REQUIREMENTS.md"), "unit.md").splitlines()]
    assert ids == ["PL5", "PL8", "PL7"], ids


def test_an_issue_whose_rows_for_one_unit_resolve_to_the_same_id_twice_exits_2_naming_the_id_and_leaves_the_list_byte_identical_2262(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| PL3 | The widget is blue. | because |\n")
    (tmp_path / "REQUIREMENTS.md").write_text(original)
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| PL7 | The widget is shiny. | gloss |\n"
        "| PL7 | The widget is heavy. | weight |\n")

    def run(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step, "subprocess",
                        types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (tmp_path / "REQUIREMENTS.md").read_text() == original, (code, err)
    assert (code, "PL7" in err) == (2, True), (code, err)


def test_apply_still_rewords_a_list_row_when_the_issue_states_its_explicit_id_beside_a_prefix_next_row_2262(tmp_path, monkeypatch):
    skill_edit_step = _next_case_2262(
        tmp_path, monkeypatch,
        ["| PL5 | The widget is blue. | because |"],
        ["| PL<next> | The widget is shiny. | gloss |",
         "| PL5 | The widget is deep blue. | because |"])
    requirements = importlib.import_module("veri.requirements")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = requirements.claims(str(tmp_path / "REQUIREMENTS.md"), "unit.md").splitlines()
    assert rows == ["PL5\tThe widget is deep blue.", "PL6\tThe widget is shiny."], rows


def test_apply_writes_a_prefix_next_rows_other_cells_byte_for_byte_keeping_an_escaped_pipe_2262(tmp_path, monkeypatch):
    skill_edit_step = _next_case_2262(
        tmp_path, monkeypatch,
        ["| PL5 | The widget is blue. | because |"],
        ["| PL<next> | The widget shows a\\|b. | gloss\\|shine |"])

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [l for l in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("| PL")]
    assert rows == ["| PL5 | The widget is blue. | because |",
                    "| PL6 | The widget shows a\\|b. | gloss\\|shine |"], rows


def test_apply_numbers_a_prefix_next_row_past_the_issues_explicit_ids_when_the_unit_exists_but_no_requirements_list_claims_it_2262(tmp_path, monkeypatch):
    skill_edit_step = _next_case_2262(
        tmp_path, monkeypatch,
        None,
        ["| PL<next> | The widget is shiny. | gloss |",
         "| PL1 | The widget is heavy. | weight |"])

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [l for l in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("| PL")]
    assert rows == ["| PL2 | The widget is shiny. | gloss |",
                    "| PL1 | The widget is heavy. | weight |"], rows


def test_apply_numbers_a_prefix_next_row_past_the_issues_explicit_ids_in_a_list_it_creates_under_a_new_heading_2262(tmp_path, monkeypatch):
    skill_edit_step = _next_case_2262(
        tmp_path, monkeypatch,
        None,
        ["| PL<next> | The widget is shiny. | gloss |",
         "| PL1 | The widget is heavy. | weight |"],
        heading="unit.md (new)")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [l for l in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("| PL")]
    assert rows == ["| PL2 | The widget is shiny. | gloss |",
                    "| PL1 | The widget is heavy. | weight |"], rows


def test_a_refused_attempts_edit_to_a_file_the_guard_names_is_restored_so_the_next_attempt_is_accepted_with_the_file_unchanged_2281(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is blue.\n")
    (tmp_path / "stray_test.py").write_text("ORIGINAL = 1\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget hums. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    grades = [(1, "A1: FAIL - silent\n"), (0, "")]
    attempts = iter([
        lambda: ((tmp_path / "unit.md").write_text("The widget hums.\n"),
                 (tmp_path / "stray_test.py").write_text("EDITED = 1\n")),
        lambda: (tmp_path / "unit.md").write_text("The widget hums.\n"),
    ])
    guarded = []

    def guard(argv):
        guarded.append(argv)
        if len(guarded) == 1:
            print("stray_test.py")
        return 0

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: grades.pop(0))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: next(attempts)() and 0)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", guard)
    monkeypatch.setattr(skill_edit_step, "subprocess", types.SimpleNamespace(
        run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""), PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, (tmp_path / "stray_test.py").read_text()) == (0, "ORIGINAL = 1\n"), (code, err)


def test_exhausted_author_attempts_exit_1_with_the_tree_as_before_the_run_requirements_list_included_2281(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is blue.\n")
    (tmp_path / "stray_test.py").write_text("ORIGINAL = 1\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget hums. | because |\n")
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget glows. | light |\n")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}

    def author(*a):
        (tmp_path / "unit.md").write_text("The widget hums.\n")
        (tmp_path / "stray_test.py").write_text("EDITED = 1\n")
        return 0

    def guard(argv):
        print("stray_test.py")
        return 0

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (1, "A2: FAIL - dark\n"))
    monkeypatch.setattr(skill_edit_step, "_author", author)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", guard)
    monkeypatch.setattr(skill_edit_step, "subprocess", types.SimpleNamespace(
        run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""), PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    after = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert (code, after) == (1, before), (code, err)


def test_a_guard_refusal_never_deletes_a_tdd_file_the_guard_names_that_it_holds_no_snapshot_for_2281(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget hums. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-9-added.md").write_text("an untracked added ledger\n")
    (tmp_path / ".tdd" / "issue-9.md").write_text("a dirty ledger\n")
    before = {p.name: p.read_bytes() for p in (tmp_path / ".tdd").iterdir()}

    def guard(argv):
        print(".tdd/issue-9-added.md")
        print(".tdd/issue-9.md")
        return 0

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (1, "A1: FAIL - silent\n"))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: 0)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", guard)
    monkeypatch.setattr(skill_edit_step, "subprocess", types.SimpleNamespace(
        run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""), PIPE=subprocess.PIPE))

    run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"], env={"VERI_SKILL_EDIT_BUDGET": "1"})

    after = {p.name: p.read_bytes() for p in (tmp_path / ".tdd").iterdir()}
    assert after == before, after


def test_a_guard_refusal_removes_a_new_file_the_author_created_and_the_guard_named_beside_a_surviving_tdd_file_2281(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget hums. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-9.md").write_text("a dirty ledger\n")

    def guard(argv):
        print("stray.py")
        print(".tdd/issue-9.md")
        return 0

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (1, "A1: FAIL - silent\n"))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: (tmp_path / "stray.py").write_text("NEW = 1\n") and 0)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", guard)
    monkeypatch.setattr(skill_edit_step, "subprocess", types.SimpleNamespace(
        run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""), PIPE=subprocess.PIPE))

    run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"], env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert ((tmp_path / "stray.py").exists(), (tmp_path / ".tdd" / "issue-9.md").read_text()) == (False, "a dirty ledger\n")


def test_a_guard_refusal_leaves_a_pre_existing_untracked_symlink_the_guard_names_and_still_removes_a_new_file_2281(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget hums. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    (tmp_path / "target").mkdir()
    (tmp_path / "link").symlink_to("target", target_is_directory=True)

    def guard(argv):
        print("link")
        print("stray.py")
        return 0

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (1, "A1: FAIL - silent\n"))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: (tmp_path / "stray.py").write_text("NEW = 1\n") and 0)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", guard)
    monkeypatch.setattr(skill_edit_step, "subprocess", types.SimpleNamespace(
        run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""), PIPE=subprocess.PIPE))

    run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"], env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert ((tmp_path / "link").is_symlink(), (tmp_path / "stray.py").exists()) == (True, False)


def test_a_pass_on_the_unchanged_text_of_a_unit_with_a_recorded_reject_signs_nothing_in_graded_without_an_author_changing_it_2121(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    grade_prose = skill_edit_step.grade_prose
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    sig = grade_prose.signature("REQUIREMENTS.md", "unit.md")
    (tmp_path / ".tdd" / "grade-prose-rejected").write_text("unit.md %s 2026-10-22 earlier\n" % sig)
    authors = []

    def run(cmd, **kw):
        if cmd[0] == "git":
            return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")
        (tmp_path / ".tdd" / "grade-prose.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":'
            '"BEGIN GRADES\\nA1: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n')
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: authors.append(a) or 0)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert (len(authors), (tmp_path / "GRADED").exists()) == (1, False), (code, out, err, authors)


def test_a_change_step_on_a_unit_already_graded_pass_launches_an_author_whose_prompt_names_the_change_and_commits_the_unit_list_and_graded_when_the_unit_grades_pass_after_it_2340(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n- a merge is in flight;\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    change = "delete the bullet - a merge is in flight;"
    prompts = []
    commands = []

    def run(cmd, **kw):
        commands.append(cmd)
        if cmd[0].endswith("supervise.sh"):
            prompts.append(open(cmd[3]).read())
            (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(subprocess, "run", run)

    code, out, err = run_cli(skill_edit_step, ["--change", change, str(tmp_path / "issue.md"), "unit.md"])

    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert code == 0 and len(prompts) == 1 and change in prompts[0], (code, err, prompts)
    assert len(commits) == 1 and all(any(n in p for p in commits[0]) for n in ("REQUIREMENTS.md", "GRADED", "unit.md")), commands


def test_a_run_given_no_change_whose_unit_grades_fail_sends_its_author_a_prompt_without_a_change_to_make_line_2340(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    prompts = []
    grades = [(1, "A1: FAIL - no\n"), (0, "")]

    def run(cmd, **kw):
        if cmd[0].endswith("supervise.sh"):
            prompts.append(open(cmd[3]).read())
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: grades.pop(0))
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(subprocess, "run", run)

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert code == 0 and len(prompts) == 1 and "Change to make:" not in prompts[0], (code, err, prompts)


def test_a_change_step_whose_every_author_attempt_leaves_the_prose_unchanged_spends_the_whole_budget_commits_nothing_and_exits_1_2340(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n- a merge is in flight;\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    authors = []
    commits = []

    def run(cmd, **kw):
        if cmd[0].endswith("supervise.sh"):
            authors.append(cmd)
        if cmd[:2] == ["git", "commit"]:
            commits.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(subprocess, "run", run)

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               str(tmp_path / "issue.md"), "unit.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "2"})

    after = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert (code, len(authors), len(commits), after) == (1, 2, 0, before), (code, err)


def test_an_added_step_given_a_change_on_a_unit_graded_pass_before_any_author_ran_launches_its_author_and_commits_instead_of_exiting_2_2340(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n- a merge is in flight;\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    authors = []
    commits = []

    def run(cmd, **kw):
        if cmd[0].endswith("supervise.sh"):
            authors.append(cmd)
            (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
        if cmd[:2] == ["git", "commit"]:
            commits.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(subprocess, "run", run)

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "--added", "drop the stale bullet",
                                               str(tmp_path / "issue.md"), "unit.md"])

    assert (code, len(authors), len(commits)) == (0, 1, 1), (code, err, authors, commits)


def test_a_run_given_no_change_on_a_unit_graded_pass_launches_no_author_commits_only_the_list_and_graded_and_exits_3_2340(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n- a merge is in flight;\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    launched = []
    commands = []

    def run(cmd, **kw):
        commands.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: launched.append(a) or 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step, "subprocess", types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    adds = [c[2:] for c in commands if c[:2] == ["git", "add"]]
    assert launched == [] and code == 3, (code, out, err, launched)
    assert len(adds) == 1 and sorted(adds[0]) == sorted(["REQUIREMENTS.md", "GRADED"]), adds


def test_a_change_step_on_a_unit_already_graded_pass_grades_the_authors_edit_though_the_up_front_passs_own_graded_write_is_uncommitted_2490(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    skill_edit_guard = skill_edit_step.skill_edit_guard
    leaf = importlib.import_module("veri.leaf")
    grade_prose = skill_edit_step.grade_prose
    original = "The widget is painted a deep blue.\n- a merge is in flight;\n"
    edited = "The widget is painted a deep blue.\n"
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / "unit.md").write_text(original)
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    (tmp_path / ".tdd").mkdir()
    graded_texts = []

    def launch(name, prompt, *args, env=None):
        if name == "grade-prose":
            graded_texts.append((tmp_path / "unit.md").read_text())
            (tmp_path / ".tdd" / "grade-prose.log").write_text(
                '{"type":"result","subtype":"success","is_error":false,"result":'
                '"BEGIN GRADES\\nA1: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n')
        else:
            (tmp_path / "unit.md").write_text(edited)
        return subprocess.CompletedProcess([name], 0, b"", None)

    def run(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(skill_edit_guard, "_git_ok", lambda *a: True)
    monkeypatch.setattr(skill_edit_guard, "_git_lines", lambda *a: sorted(
        p.name for p in tmp_path.iterdir() if p.name not in (".tdd", "skills")) if a[0] == "ls-files" else [])
    monkeypatch.setattr(grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(leaf, "launch", launch)

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "issue.md", "unit.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    events = [json.loads(l) for l in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    gradings = [e for e in events if e.get("event") == "grading"]
    assert graded_texts == [original, edited], (code, out, err, graded_texts)
    assert (code, (tmp_path / "unit.md").read_text()) == (0, edited), (code, out, err)
    assert [(e.get("unit"), e.get("verdict")) for e in gradings] == [("unit.md", "PASS")] * 2, (events, err)
    assert gradings[-1]["id"] in (tmp_path / "GRADED").read_text(), (gradings, err)


def test_a_change_step_on_a_unit_already_graded_pass_whose_author_writes_a_stray_path_has_it_flagged_and_restored_and_grades_no_attempt_2490(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    skill_edit_guard = skill_edit_step.skill_edit_guard
    original = "The widget is painted a deep blue.\n- a merge is in flight;\n"
    edited = "The widget is painted a deep blue.\n"
    (tmp_path / "unit.md").write_text(original)
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    grades = []

    def grade(path, unit):
        grades.append((tmp_path / unit).read_text())
        (tmp_path / "GRADED").write_text("sig\n")
        return 0, ""

    def run(cmd, **kw):
        if cmd[0].endswith("supervise.sh"):
            (tmp_path / "unit.md").write_text(edited)
            (tmp_path / "stray.txt").write_text("stray\n")
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", grade)
    monkeypatch.setattr(skill_edit_guard, "_git_ok", lambda *a: True)
    monkeypatch.setattr(skill_edit_guard, "_git_lines", lambda *a: sorted(
        p.name for p in tmp_path.iterdir()) if a[0] == "ls-files" else [])
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(subprocess, "run", run)

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "issue.md", "unit.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert grades == [original], (code, out, err, grades)
    assert (code, (tmp_path / "stray.txt").exists(), (tmp_path / "unit.md").read_text()) == (1, False, original), (code, out, err)


def test_a_change_step_on_a_unit_already_graded_pass_ends_in_one_commit_of_exactly_the_unit_its_list_its_graded_and_the_pins_2490(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    skill_edit_guard = skill_edit_step.skill_edit_guard
    original = "The widget is painted a deep blue.\n- a merge is in flight;\n"
    edited = "The widget is painted a deep blue.\n"
    (tmp_path / "unit.md").write_text(original)
    (tmp_path / "pin.md").write_text("pin\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    commands = []

    def grade(path, unit):
        (tmp_path / "GRADED").write_text("sig\n")
        return 0, ""

    def run(cmd, **kw):
        commands.append(cmd)
        if cmd[0].endswith("supervise.sh"):
            (tmp_path / "unit.md").write_text(edited)
            (tmp_path / "pin.md").write_text("pin, edited\n")
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", grade)
    monkeypatch.setattr(skill_edit_guard, "_git_ok", lambda *a: True)
    monkeypatch.setattr(skill_edit_guard, "_git_lines", lambda *a: sorted(
        p.name for p in tmp_path.iterdir()) if a[0] == "ls-files" else [])
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(subprocess, "run", run)

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "issue.md", "unit.md", "pin.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert code == 0, (code, out, err)
    assert len(commits) == 1, commits
    assert sorted(commits[0][5:]) == sorted(["unit.md", "REQUIREMENTS.md", "GRADED", "pin.md"]), commits


def test_an_added_flag_before_a_change_flag_applies_both_as_the_change_first_order_does_never_reading_the_literal_change_as_the_issue_body_2472(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n- a merge is in flight;\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    authors = []
    commits = []

    def run(cmd, **kw):
        if cmd[0].endswith("supervise.sh"):
            authors.append(cmd)
            (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
        if cmd[:2] == ["git", "commit"]:
            commits.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(subprocess, "run", run)

    code, out, err = run_cli(skill_edit_step, ["--added", "drop the stale bullet",
                                               "--change", "delete the bullet - a merge is in flight;",
                                               str(tmp_path / "issue.md"), "unit.md"])

    assert (code, len(authors), len(commits)) == (0, 1, 1), (code, err, authors, commits)


def test_the_usage_refusal_for_a_bad_argument_list_names_the_change_flag_beside_the_added_flag_2472(run_cli):
    skill_edit_step = importlib.import_module("veri.skill_edit_step")

    code, out, err = run_cli(skill_edit_step, ["only-one-file"])

    assert (code, "--change" in err, "--added" in err) == (2, True, True), (code, err)


def test_a_change_step_whose_author_edits_only_a_pin_file_leaves_the_unit_byte_identical_fails_the_attempt_as_prose_unchanged_and_commits_nothing_2473(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n- a merge is in flight;\n")
    (tmp_path / "pin.md").write_text("pin\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    commits = []

    def launch(name, prompt, *args, env=None):
        (tmp_path / "pin.md").write_text("pin, edited\n")
        return subprocess.CompletedProcess([name], 0, b"", None)

    def run(cmd, **kw):
        if cmd[:2] == ["git", "commit"]:
            commits.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(skill_edit_step, "subprocess", types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))
    monkeypatch.setattr(importlib.import_module("veri.leaf"), "launch", launch)

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "issue.md", "unit.md", "pin.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert (code, "FAIL: the author left the prose unchanged" in out, commits) == (1, True, []), (code, out, err)


def test_a_change_step_whose_author_edits_the_unit_and_leaves_every_pin_file_untouched_still_succeeds_and_commits_2473(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n- a merge is in flight;\n")
    (tmp_path / "pin.md").write_text("pin\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    commits = []

    def launch(name, prompt, *args, env=None):
        (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
        return subprocess.CompletedProcess([name], 0, b"", None)

    def run(cmd, **kw):
        if cmd[:2] == ["git", "commit"]:
            commits.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(skill_edit_step, "subprocess", types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))
    monkeypatch.setattr(importlib.import_module("veri.leaf"), "launch", launch)

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "issue.md", "unit.md", "pin.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert (code, len(commits)) == (0, 1), (code, out, err)


def test_the_author_leaf_is_launched_through_veri_leaf_launch_as_author_skill_edit_1_with_bypass_permissions_and_its_edit_is_graded_2498(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    skill_edit_guard = skill_edit_step.skill_edit_guard
    leaf = importlib.import_module("veri.leaf")
    original = "The widget is painted a deep blue.\n- a merge is in flight;\n"
    edited = "The widget is painted a deep blue.\n"
    (tmp_path / "unit.md").write_text(original)
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    graded_texts = []
    launched = []

    def grade(path, unit):
        graded_texts.append((tmp_path / unit).read_text())
        (tmp_path / "GRADED").write_text("sig\n")
        return 0, ""

    def launch(name, prompt, *args, env=None):
        launched.append((name, args))
        (tmp_path / "unit.md").write_text(edited)
        return subprocess.CompletedProcess([name], 0, b"", None)

    def run(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    monkeypatch.setattr(skill_edit_step, "_grade", grade)
    monkeypatch.setattr(skill_edit_guard, "_git_ok", lambda *a: True)
    monkeypatch.setattr(skill_edit_guard, "_git_lines", lambda *a: sorted(
        p.name for p in tmp_path.iterdir()) if a[0] == "ls-files" else [])
    monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: None)
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(subprocess, "run", run)
    monkeypatch.setattr(leaf, "launch", launch)

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "issue.md", "unit.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert [n for n, _ in launched] == ["author-skill-edit-1"], (code, out, err, launched)
    assert launched[0][1][-2:] == ("--permission-mode", "bypassPermissions"), launched
    assert graded_texts == [original, edited], (code, out, err, graded_texts)
    assert (code, (tmp_path / "unit.md").read_text()) == (0, edited), (code, out, err)


def test_an_author_leaf_failing_exits_2_leaving_the_list_the_unit_and_graded_byte_identical_2576(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "GRADED").write_text("old signature\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget glows. | light |\n")
    names = ["unit.md", "GRADED", "REQUIREMENTS.md"]
    before = {n: (tmp_path / n).read_bytes() for n in names}

    def grade(path, unit):
        (tmp_path / "GRADED").write_text("new signature\n")
        return 1, "A2: FAIL - dark\n"

    def author(*a):
        (tmp_path / "unit.md").write_text("The widget glows.\n")
        return 2

    monkeypatch.setattr(skill_edit_step, "_grade", grade)
    monkeypatch.setattr(skill_edit_step, "_author", author)
    monkeypatch.setattr(skill_edit_step, "subprocess", types.SimpleNamespace(
        run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""), PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    after = {n: (tmp_path / n).read_bytes() for n in names}
    assert (code, after) == (2, before), (code, err, after)


def test_a_grader_answering_no_verdict_exits_2_leaving_the_list_the_unit_and_graded_byte_identical_2576(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "GRADED").write_text("old signature\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget glows. | light |\n")
    names = ["unit.md", "GRADED", "REQUIREMENTS.md"]
    before = {n: (tmp_path / n).read_bytes() for n in names}
    authors = []

    def grade(path, unit):
        (tmp_path / "GRADED").write_text("new signature\n")
        return 2, "no verdict\n"

    monkeypatch.setattr(skill_edit_step, "_grade", grade)
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: authors.append(a) or 0)
    monkeypatch.setattr(skill_edit_step, "subprocess", types.SimpleNamespace(
        run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""), PIPE=subprocess.PIPE))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    after = {n: (tmp_path / n).read_bytes() for n in names}
    assert (code, after, authors) == (2, before, []), (code, err, after)


def test_an_as_is_marker_under_a_unit_heading_changes_neither_the_rows_nor_the_unit_apply_reads_2462(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    table = ("| ID | Requirement | Why |\n|---|---|---|\n"
             "| A1 | The widget is blue. | because |\n"
             "| A2 | The widget is square. | corners |\n")
    plain = "## Requirements\n\n### unit.md\n\n" + table
    marked = ("## Requirements\n\n### unit.md\n\n"
              "As is: these rows describe the unit's current text.\n\n" + table)
    (tmp_path / "plain.md").write_text(plain)
    (tmp_path / "marked.md").write_text(marked)

    assert skill_edit_step._issue_rows(str(tmp_path / "marked.md"), "unit.md") == \
        skill_edit_step._issue_rows(str(tmp_path / "plain.md"), "unit.md")
    assert skill_edit_step._issue_rows(str(tmp_path / "marked.md"), "unit.md")

    lists = []
    for name in ("plain.md", "marked.md"):
        (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
        (tmp_path / "REQUIREMENTS.md").write_text(
            "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
        assert skill_edit_step._unknown_heading(str(tmp_path / name)) is None
        skill_edit_step.apply(str(tmp_path / name), "unit.md")
        lists.append(((tmp_path / "REQUIREMENTS.md").read_text(), (tmp_path / "unit.md").read_text()))
    assert lists[0] == lists[1], lists
