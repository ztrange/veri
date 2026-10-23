"""In-process cases for veri/skill_edit_step.py, the module skill-edit-step.sh is a shim over."""
import importlib


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
    (tmp_path / "skills" / "veri-dev").mkdir(parents=True)
    (tmp_path / "skills" / "veri-dev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "skills" / "veri-dev" / "REQUIREMENTS.md").write_text(
        "## skills/veri-dev/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### skills/veri-dev/SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget is round. | shape |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/veri-dev/SKILL.md")

    rows = [l for l in (tmp_path / "skills" / "veri-dev" / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("| A")]
    assert rows == [
        "| A1 | The widget is blue. | because |",
        "| A2 | The widget is round. | shape |",
    ], rows


def test_apply_reads_no_rows_for_a_unit_under_a_heading_naming_a_different_units_repo_relative_path_1959(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "skills" / "veri-dev").mkdir(parents=True)
    (tmp_path / "skills" / "veri-dev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    original = (
        "## SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    (tmp_path / "skills" / "veri-dev" / "REQUIREMENTS.md").write_bytes(original.encode())
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### skills/other/SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget is round. | shape |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/veri-dev/SKILL.md")

    assert (tmp_path / "skills" / "veri-dev" / "REQUIREMENTS.md").read_bytes() == original.encode()


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
    (tmp_path / "skills" / "veri-dev").mkdir(parents=True)
    (tmp_path / "skills" / "veri-dev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### skills/veri-dev/SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/veri-dev/SKILL.md")

    rows = [l for l in (tmp_path / "skills" / "veri-dev" / "REQUIREMENTS.md").read_text().splitlines() if l.startswith("| A")]
    assert rows == ["| A1 | The widget is blue. | because |"], rows


def test_a_unit_with_no_table_whose_requirements_list_holds_only_another_units_section_run_against_an_issue_stating_no_rows_for_it_exits_3_leaving_the_list_byte_identical_1959(tmp_path, monkeypatch, run_cli):
    monkeypatch.chdir(tmp_path)
    import subprocess
    import types
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "skills" / "veri-dev").mkdir(parents=True)
    (tmp_path / "skills" / "veri-dev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    original = ("## skills/other/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| B1 | The gadget is red. | colour |\n")
    (tmp_path / "skills" / "veri-dev" / "REQUIREMENTS.md").write_text(original)
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")
    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    fake = types.SimpleNamespace(
        run=lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "abc1234\n", ""),
        PIPE=subprocess.PIPE)
    monkeypatch.setattr(skill_edit_step, "subprocess", fake)

    code, _, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "skills/veri-dev/SKILL.md"])

    assert (code, (tmp_path / "skills" / "veri-dev" / "REQUIREMENTS.md").read_bytes()) == (3, original.encode()), err


def test_apply_appends_the_issue_rows_as_a_new_section_beside_a_list_holding_only_another_units_section_1959(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "skills" / "veri-dev").mkdir(parents=True)
    (tmp_path / "skills" / "veri-dev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    other = ("## skills/other/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
             "| B1 | The gadget is red. | colour |\n")
    listing = tmp_path / "skills" / "veri-dev" / "REQUIREMENTS.md"
    listing.write_text(other)
    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### skills/veri-dev/SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/veri-dev/SKILL.md")

    text = listing.read_text()
    assert text.startswith(other), text
    assert "## skills/veri-dev/SKILL.md" in text.splitlines(), text
    assert "| A1 | The widget is blue. | because |" in text.splitlines(), text


def test_apply_moves_a_units_own_table_into_a_list_holding_only_another_units_section_leaving_that_section_unchanged_1959(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    (tmp_path / "skills" / "veri-dev").mkdir(parents=True)
    unit = tmp_path / "skills" / "veri-dev" / "SKILL.md"
    unit.write_text(
        "Prose.\n\n## Requirements\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    other = ("## skills/other/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
             "| B1 | The gadget is red. | colour |\n")
    listing = tmp_path / "skills" / "veri-dev" / "REQUIREMENTS.md"
    listing.write_text(other)
    (tmp_path / "issue.md").write_text("## Problem\n\nText.\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/veri-dev/SKILL.md")

    text = listing.read_text()
    assert text.startswith(other), text
    assert "## skills/veri-dev/SKILL.md" in text.splitlines(), text
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
    import types
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
    monkeypatch.setattr(skill_edit_step, "subprocess", types.SimpleNamespace(run=run, PIPE=subprocess.PIPE))
    for pins in (["tests/test_alpha.py", "tests/test_beta.py"], []):
        grades = iter([(1, "A1: FAIL - no\n"), (0, "")])
        monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: next(grades))
        run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md", *pins])

    with_pins, without = prompts
    assert (all(p in with_pins for p in ["tests/test_alpha.py", "tests/test_beta.py", "checksum", "verbatim"]),
            "tests/test_" in without) == (True, False), (with_pins, without)
