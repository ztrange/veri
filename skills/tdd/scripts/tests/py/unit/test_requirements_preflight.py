"""In-process cases for veri/requirements_preflight.py, the module requirements-preflight.sh is a shim over."""
import importlib


def test_3567_an_issue_whose_requirements_rows_are_all_new_identical_or_reword_marked_exits_0(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n")
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2<reword> | The widget is square. | corners |\n"
        "| A3 | The widget is shiny. | gloss |\n")

    code, out, err = run_cli(requirements_preflight, [str(issue)], cwd=tmp_path)

    assert (code, err) == (0, ""), (code, out, err)


def test_3567_an_issue_with_rows_clashing_across_tables_exits_2_naming_every_clashing_id(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("Unit text.\n")
    (tmp_path / "other.md").write_text("Other text.\n")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n" + head + "| A1 | The widget is blue. | because |\n\n"
        "## other.md\n\n" + head + "| B1 | The gadget is red. | because |\n"
        "| B2 | The gadget is small. | size |\n")

    def issue_with(a_row, b_row):
        path = tmp_path / "issue.md"
        path.write_text(
            "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n" + head + a_row + "\n"
            "| A2 | The widget is round. | shape |\n\n### other.md\n\n" + head + b_row + "\n"
            "| B2<reword> | The gadget is large. | size |\n")
        return path

    clean = issue_with("| A1 | The widget is blue. | because |", "| B1 | The gadget is red. | because |")
    assert run_cli(requirements_preflight, [str(clean)], cwd=tmp_path)[::2] == (0, "")

    clashing = issue_with("| A1 | The widget is green. | because |", "| B1 | The gadget is blue. | because |")
    code, out, err = run_cli(requirements_preflight, [str(clashing)], cwd=tmp_path)

    assert code == 2 and "A1" in err and "B1" in err and "A2" not in err and "B2" not in err, (code, out, err)


def test_3567_a_unit_whose_heading_repeats_in_the_issue_names_each_clashing_id_once(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("Unit text.\n")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n" + head + "| A1 | The widget is blue. | because |\n")
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n" + head +
        "| A1 | The widget is green. | because |\n\n### unit.md\n\n" + head +
        "| A2 | The widget is round. | shape |\n")

    code, out, err = run_cli(requirements_preflight, [str(issue)], cwd=tmp_path)

    assert code == 2 and err.count("A1") == 1 and "A2" not in err, (code, out, err)


def test_3567_a_ledger_skill_edit_step_whose_unit_has_no_issue_table_is_named_with_the_clashing_ids_in_one_exit_2(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("Unit text.\n")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n" + head + "| A1 | The widget is blue. | because |\n")
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n" + head +
        "| A1 | The widget is green. | because |\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_text(
        "- [ ] ⟦skill-edit⟧ regrade `unit.md` against A1\n"
        "- [ ] ⟦skill-edit⟧ regrade `missing/NOTES.md` against A1\n"
        "- [ ] plain step touching `plain/ignored.md`\n")

    code, out, err = run_cli(requirements_preflight, [str(issue), str(ledger)], cwd=tmp_path)

    assert code == 2 and "A1" in err and "missing/NOTES.md" in err and "unit.md\n" not in err.replace("A1", "") and "plain/ignored.md" not in err, (code, out, err)


def test_3567_a_ledger_skill_edit_step_whose_unit_has_no_issue_table_alone_exits_2_naming_that_unit(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("Unit text.\n")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n" + head + "| A1 | The widget is blue. | because |\n")
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n" + head +
        "| A1 | The widget is blue. | because |\n")
    covered = "- [ ] regrade `unit.md` against A1 ⟦skill-edit⟧ ⟦criterion 1⟧\n"
    ledger = tmp_path / "ledger.md"
    ledger.write_text(covered)
    assert run_cli(requirements_preflight, [str(issue), str(ledger)], cwd=tmp_path)[::2] == (0, "")

    ledger.write_text(covered + "- [ ] regrade `missing/NOTES.md` ⟦skill-edit⟧ ⟦criterion 2⟧\n"
                      "- [ ] plain step touching `plain/ignored.md` ⟦criterion 3⟧\n")
    code, out, err = run_cli(requirements_preflight, [str(issue), str(ledger)], cwd=tmp_path)

    assert code == 2 and "missing/NOTES.md" in err and "plain/ignored.md" not in err and "A1" not in err, (code, out, err)


def test_3567_a_ledger_line_with_the_skill_edit_marker_that_is_not_a_checkbox_is_ignored_by_the_unit_heading_check(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("Unit text.\n")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n" + head + "| A1 | The widget is blue. | because |\n")
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n" + head +
        "| A1 | The widget is blue. | because |\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_text("Note: ⟦skill-edit⟧ steps cover `notes/PROSE.md` too.\n"
                      "  ⟦skill-edit⟧ indented mention of `notes/INDENT.md`\n"
                      "- [ ] regrade `missing/NOTES.md` ⟦skill-edit⟧\n")

    code, out, err = run_cli(requirements_preflight, [str(issue), str(ledger)], cwd=tmp_path)

    assert code == 2 and "missing/NOTES.md" in err and "notes/PROSE.md" not in err and "notes/INDENT.md" not in err, (code, out, err)


def test_3567_a_missing_unit_heading_prints_no_clash_line_while_a_real_clashing_id_does(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("Unit text.\n")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n" + head + "| A1 | The widget is blue. | because |\n")
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n" + head +
        "| A1 | The widget is green. | because |\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [ ] regrade `missing/NOTES.md` ⟦skill-edit⟧\n")

    code, out, err = run_cli(requirements_preflight, [str(issue), str(ledger)], cwd=tmp_path)

    clash_lines = [l for l in err.splitlines() if l.startswith("Requirement row ID already held")]
    assert code == 2 and "missing/NOTES.md" in err and len(clash_lines) == 1 and clash_lines[0].endswith(": A1"), (code, out, err)


def test_3567_two_missing_skill_edit_units_and_two_clashing_ids_in_one_unit_are_all_named_in_one_exit_2(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("Unit text.\n")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n" + head + "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n")
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n" + head +
        "| A1 | The widget is green. | because |\n"
        "| A2 | The widget is square. | shape |\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [ ] regrade `missing/ONE.md` ⟦skill-edit⟧\n"
                      "- [ ] regrade `missing/TWO.md` ⟦skill-edit⟧\n")

    code, out, err = run_cli(requirements_preflight, [str(issue), str(ledger)], cwd=tmp_path)

    assert code == 2 and all(n in err for n in ("missing/ONE.md", "missing/TWO.md", "A1", "A2")), (code, out, err)


def test_3634_a_ledger_step_that_mentions_the_skill_edit_marker_only_in_its_prose_is_not_checked_for_a_unit_heading(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("Unit text.\n")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n" + head + "| A1 | The widget is blue. | because |\n")
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n" + head +
        "| A1 | The widget is blue. | because |\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [ ] `add-ledger-step.sh` records a step that mentions ⟦skill-edit⟧ in its wording ⟦criterion 1⟧\n")

    code, out, err = run_cli(requirements_preflight, [str(issue), str(ledger)], cwd=tmp_path)

    assert code == 0 and "## Requirements has no ### heading" not in err, (code, out, err)


def test_3634_a_ledger_step_carrying_the_skill_edit_marker_in_its_trailing_tag_run_whose_unit_has_no_heading_exits_2_naming_that_unit(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    (tmp_path / "unit.md").write_text("Unit text.\n")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## unit.md\n\n" + head + "| A1 | The widget is blue. | because |\n")
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n" + head +
        "| A1 | The widget is blue. | because |\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [ ] `other.md` records a step that mentions ⟦skill-edit⟧ in its wording ⟦skill-edit⟧ ⟦criterion 2⟧\n")

    code, out, err = run_cli(requirements_preflight, [str(issue), str(ledger)], cwd=tmp_path)

    assert code == 2 and "## Requirements has no ### heading for unit: other.md" in err, (code, out, err)


def test_3686_a_ticked_skill_edit_step_whose_first_backticked_token_is_not_path_shaped_takes_the_later_path_shaped_one_as_its_unit(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    (tmp_path / "REQUIREMENTS.md").write_text("## skills/tdd/SKILL.md\n\n" + head + "| A1 | The route is named. | because |\n")
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### skills/tdd/SKILL.md\n\n" + head +
        "| A1 | The route is named. | because |\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [x] ⟦skill-edit⟧ SKILL.md (the `missing` route) `skills/tdd/SKILL.md`\n")

    code, out, err = run_cli(requirements_preflight, [str(issue), str(ledger)], cwd=tmp_path)

    assert (code, err) == (0, ""), (code, out, err)


def test_3686_a_skill_edit_step_with_no_path_shaped_backticked_token_exits_2_naming_the_step(tmp_path, run_cli):
    requirements_preflight = importlib.import_module("veri.requirements_preflight")
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    issue = tmp_path / "issue.md"
    issue.write_text(
        "## Problem\n\nText.\n\n## Requirements\n\n### skills/tdd/SKILL.md\n\n" + head +
        "| A1 | The route is named. | because |\n")
    ledger = tmp_path / "ledger.md"
    ledger.write_text("- [ ] ⟦skill-edit⟧ route the `missing` case ⟦criterion 1⟧\n")

    code, out, err = run_cli(requirements_preflight, [str(issue), str(ledger)], cwd=tmp_path)

    assert code == 2 and "no path-shaped unit for skill-edit step: " in err and "route the `missing` case" in err, (code, out, err)
