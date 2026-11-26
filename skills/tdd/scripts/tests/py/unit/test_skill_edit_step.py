"""In-process cases for veri/skill_edit_step.py, the module skill-edit-step.sh is a shim over."""
import importlib
import json
import subprocess
import types

import pytest

UNIT_TEXT = "The widget is painted a deep blue.\n"
LISTING = "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"
ISSUE = "## Problem\n\nText.\n"


def _git_ok(cmd, **kw):
    return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")


@pytest.fixture
def skill_edit(tmp_path, monkeypatch):
    """A factory: chdir into tmp_path, write the tree (unit.md, REQUIREMENTS.md, issue.md: `unit`, `listing`,
    `issue`, each None to write no such file), and, unless `stubbed=False`, install the four stubs every run
    of the step needs: `_grade` (`grade`: a (code, text) answered every time, a list of them answered in order,
    or a callable), `_author` (`author`: an exit code or a callable), `event.append`, and a fake `subprocess`
    whose `run` (`run`: a callable, default answering 0 with "abc1234\\n") stands in for git. `author=None` or
    `run=None` leaves that one unstubbed, for a case that fakes `leaf.launch` or uses `fake_processes`, and
    `grade=None` leaves `_grade` unstubbed, for a case that grades through `fake_processes`;
    `guard`, when given, replaces `skill_edit_guard.offending`. Returns a namespace: `step` (the module) and
    the recorded `graded`, `launched` (author calls), `events` and `commands` (every run argv)."""
    def install(unit=UNIT_TEXT, listing=LISTING, issue=ISSUE, grade=(1, "A1: FAIL - no\n"), author=0,
                run=_git_ok, guard=None, stubbed=True):
        monkeypatch.chdir(tmp_path)
        skill_edit_step = importlib.import_module("veri.skill_edit_step")
        for name, text in (("unit.md", unit), ("REQUIREMENTS.md", listing), ("issue.md", issue)):
            if text is not None:
                (tmp_path / name).write_text(text)
        case = types.SimpleNamespace(step=skill_edit_step, graded=[], launched=[], events=[], commands=[])
        if not stubbed:
            return case
        if isinstance(grade, list):
            def answer(*a):
                return grade.pop(0)
        elif isinstance(grade, tuple):
            def answer(*a):
                return grade
        else:
            answer = grade
        if grade is not None:
            monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: case.graded.append(a) or answer(*a))
        if author is not None:
            launch = author if callable(author) else (lambda *a: author)
            monkeypatch.setattr(skill_edit_step, "_author", lambda *a: case.launched.append(a) or launch(*a))
        monkeypatch.setattr(skill_edit_step.event, "append", lambda *a, **k: case.events.append(a))
        if guard is not None:
            monkeypatch.setattr(skill_edit_step.skill_edit_guard, "offending", guard)
        if run is not None:
            monkeypatch.setattr(skill_edit_step, "subprocess", types.SimpleNamespace(
                run=lambda cmd, **kw: case.commands.append(cmd) or run(cmd, **kw), PIPE=subprocess.PIPE))
        return case
    return install


def test_apply_adds_the_issue_rows_the_units_list_lacks_at_its_end_and_no_row_the_issue_does_not_state(tmp_path, skill_edit):
    skill_edit_step = skill_edit(
        listing="## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n\n"
        "## other.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| B1 | Other. | o |\n",
        issue="## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A3 | The widget is shiny. | gloss |\n\n"
        "### other.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| B2 | Not ours. | n |\n",
        stubbed=False).step
    (tmp_path / "other.md").write_text("Other unit.\n")
    requirements = importlib.import_module("veri.requirements")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    ids = [row.split("\t")[0] for row in requirements.claims(str(tmp_path / "REQUIREMENTS.md"), "unit.md").splitlines()]
    assert ids == ["A1", "A2", "A3"], ids


def test_apply_rewords_a_row_the_list_already_holds_in_place_keeping_its_id_and_position(tmp_path, skill_edit):
    skill_edit_step = skill_edit(
        listing="## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n"
        "| A3 | The widget is shiny. | gloss |\n",
        issue="## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget is square. | corners |\n",
        stubbed=False).step

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("| A")]
    assert rows == [
        "| A1 | The widget is blue. | because |",
        "| A2 | The widget is square. | corners |",
        "| A3 | The widget is shiny. | gloss |",
    ], rows


def test_apply_rewords_in_place_a_row_whose_id_cell_is_id_reword_writing_the_id_bare_3320(tmp_path, skill_edit):
    skill_edit_step = skill_edit(
        listing="## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n"
        "| A3 | The widget is shiny. | gloss |\n",
        issue="## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2<reword> | The widget is square. | corners |\n",
        stubbed=False).step

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("| A")]
    assert rows == [
        "| A1 | The widget is blue. | because |",
        "| A2 | The widget is square. | corners |",
        "| A3 | The widget is shiny. | gloss |",
    ], rows


def test_apply_drops_the_row_an_issue_marks_dropped_and_renumbers_no_other_row(tmp_path, skill_edit):
    skill_edit_step = skill_edit(
        listing="## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n"
        "| A3 | The widget is shiny. | gloss |\n",
        issue="## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | (dropped) | no longer wanted |\n",
        stubbed=False).step

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("| A")]
    assert rows == [
        "| A1 | The widget is blue. | because |",
        "| A3 | The widget is shiny. | gloss |",
    ], rows


def test_apply_leaves_the_list_byte_for_byte_when_the_issue_has_no_requirements_section_or_none_for_the_unit(tmp_path, skill_edit):
    skill_edit_step = skill_edit(listing=None, issue=None, stubbed=False).step
    (tmp_path / "other.md").write_text("Other unit.\n")
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


def test_apply_creates_a_new_unit_empty_and_its_section_in_a_requirements_list_it_creates(tmp_path, skill_edit):
    skill_edit_step = skill_edit(
        unit=None, listing=None,
        issue="## Requirements\n\n### unit.md (new)\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n",
        stubbed=False).step

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    assert (tmp_path / "unit.md").read_bytes() == b""
    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("|")]
    assert rows[2:] == [
        "| A1 | The widget is blue. | because |",
        "| A2 | The widget is round. | shape |",
    ], rows
    assert "## unit.md" in (tmp_path / "REQUIREMENTS.md").read_text().splitlines()


def test_apply_keeps_the_sections_of_an_existing_requirements_list_when_it_creates_a_new_unit(tmp_path, skill_edit):
    other = ("## other.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
             "| B1 | The gadget hums. | sound |\n")
    skill_edit_step = skill_edit(
        unit=None, listing=other,
        issue="## Requirements\n\n### unit.md (new)\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n",
        stubbed=False).step

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    text = (tmp_path / "REQUIREMENTS.md").read_text()
    assert text.startswith(other), text
    assert "## unit.md" in text.splitlines(), text
    assert "| A1 | The widget is blue. | because |" in text.splitlines(), text


def test_a_veri_skill_edit_budget_that_is_not_a_whole_number_of_at_least_one_exits_2_before_any_grading_or_launch_and_the_shim_header_names_it(tmp_path, skill_edit, run_cli):
    from conftest import SCRIPTS
    calls = []
    skill_edit_step = skill_edit(
        grade=lambda *a: calls.append("grade") or (1, "A1: FAIL - no\n"),
        author=lambda *a: calls.append("author") or 0,
        guard=lambda unit, base, pins: calls.append("guard") or [],
        run=lambda cmd, **kw: calls.append(" ".join(cmd[:2])) or _git_ok(cmd)).step

    codes = {}
    for budget in ["", "0", "-1", "two", "1.5"]:
        codes[budget] = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"],
                                env={"VERI_SKILL_EDIT_BUDGET": budget})[0]

    header = (SCRIPTS / "skill-edit-step.sh").read_text().split("exec ")[0]
    assert (codes, calls, "VERI_SKILL_EDIT_BUDGET" in header) \
        == ({b: 2 for b in ["", "0", "-1", "two", "1.5"]}, [], True), (codes, calls)


def test_a_guard_exit_2_exits_the_step_2_signing_nothing_and_committing_nothing(tmp_path, skill_edit, run_cli):
    def refuse_the_base(unit, base, pins):
        raise skill_edit_step.skill_edit_guard.Refusal("skill-edit-guard.sh: %s is not a commit" % base)

    case = skill_edit(grade=[(1, "A1: FAIL - no\n"), (0, "")], guard=refuse_the_base)
    skill_edit_step = case.step

    code = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])[0]

    gits = [c[:2] for c in case.commands]
    assert (code, [g for g in gits if g[1] in ("add", "commit")], (tmp_path / "GRADED").exists()) == (2, [], False), (code, gits)


def test_the_author_attempts_follow_veri_skill_edit_budget_alone_whatever_the_other_five_budgets_say(tmp_path, skill_edit, run_cli):
    case = skill_edit(guard=lambda unit, base, pins: [])
    others = {"REVISE_BUDGET": "7", "VERI_STUCK_RETRIES": "8", "VERI_NO_VERDICT_RETRIES": "9",
              "VERI_REFACTOR_BUDGET": "10", "VERI_STEP_GROWTH": "11"}

    code = run_cli(case.step, [str(tmp_path / "issue.md"), "unit.md"],
                   env={**others, "VERI_SKILL_EDIT_BUDGET": "2"})[0]

    authors = case.launched
    assert (code, len(authors)) == (1, 2), (code, len(authors))


def test_apply_reads_no_rows_for_a_unit_below_the_root_under_a_heading_holding_only_its_basename_1959(tmp_path, skill_edit):
    skill_edit_step = skill_edit(
        unit=None, listing=None,
        issue="## Requirements\n\n### SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget is round. | shape |\n",
        stubbed=False).step
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    original = (
        "## SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    (tmp_path / "sub" / "REQUIREMENTS.md").write_bytes(original.encode())

    skill_edit_step.apply(str(tmp_path / "issue.md"), "sub/SKILL.md")

    assert (tmp_path / "sub" / "REQUIREMENTS.md").read_bytes() == original.encode()


def test_apply_adds_the_rows_under_a_repo_relative_path_heading_to_the_list_beside_a_unit_below_the_root_1959(tmp_path, skill_edit):
    skill_edit_step = skill_edit(
        unit=None, listing=None,
        issue="## Requirements\n\n### skills/vdev/SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget is round. | shape |\n",
        stubbed=False).step
    (tmp_path / "skills" / "vdev").mkdir(parents=True)
    (tmp_path / "skills" / "vdev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").write_text(
        "## skills/vdev/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/vdev/SKILL.md")

    rows = [line for line in (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("| A")]
    assert rows == [
        "| A1 | The widget is blue. | because |",
        "| A2 | The widget is round. | shape |",
    ], rows


def test_apply_reads_no_rows_for_a_unit_under_a_heading_naming_a_different_units_repo_relative_path_1959(tmp_path, skill_edit):
    skill_edit_step = skill_edit(
        unit=None, listing=None,
        issue="## Requirements\n\n### skills/other/SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget is round. | shape |\n",
        stubbed=False).step
    (tmp_path / "skills" / "vdev").mkdir(parents=True)
    (tmp_path / "skills" / "vdev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    original = (
        "## SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").write_bytes(original.encode())

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/vdev/SKILL.md")

    assert (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").read_bytes() == original.encode()


def test_a_unit_with_no_requirements_list_run_against_an_issue_with_no_requirements_section_is_left_unchanged_and_exits_3_1959(tmp_path, skill_edit, run_cli):
    skill_edit_step = skill_edit(listing=None, grade=(0, "")).step

    code = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])[0]

    assert (code, (tmp_path / "unit.md").read_bytes()) == (3, b"The widget is painted a deep blue.\n")


def test_apply_makes_the_issue_rows_the_new_list_beside_a_unit_with_no_requirements_list_1959(tmp_path, skill_edit):
    skill_edit_step = skill_edit(
        unit=None, listing=None,
        issue="## Requirements\n\n### skills/vdev/SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n",
        stubbed=False).step
    (tmp_path / "skills" / "vdev").mkdir(parents=True)
    (tmp_path / "skills" / "vdev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/vdev/SKILL.md")

    rows = [line for line in (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("| A")]
    assert rows == ["| A1 | The widget is blue. | because |"], rows


def test_a_unit_with_no_table_whose_requirements_list_holds_only_another_units_section_run_against_an_issue_stating_no_rows_for_it_exits_3_leaving_the_list_byte_identical_1959(tmp_path, skill_edit, run_cli):
    skill_edit_step = skill_edit(unit=None, listing=None, grade=(0, "")).step
    (tmp_path / "skills" / "vdev").mkdir(parents=True)
    (tmp_path / "skills" / "vdev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    original = ("## skills/other/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| B1 | The gadget is red. | colour |\n")
    (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").write_text(original)

    code, _, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "skills/vdev/SKILL.md"])

    assert (code, (tmp_path / "skills" / "vdev" / "REQUIREMENTS.md").read_bytes()) == (3, original.encode()), err


def test_apply_appends_the_issue_rows_as_a_new_section_beside_a_list_holding_only_another_units_section_1959(tmp_path, skill_edit):
    skill_edit_step = skill_edit(
        unit=None, listing=None,
        issue="## Requirements\n\n### skills/vdev/SKILL.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n",
        stubbed=False).step
    (tmp_path / "skills" / "vdev").mkdir(parents=True)
    (tmp_path / "skills" / "vdev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    other = ("## skills/other/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
             "| B1 | The gadget is red. | colour |\n")
    listing = tmp_path / "skills" / "vdev" / "REQUIREMENTS.md"
    listing.write_text(other)

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/vdev/SKILL.md")

    text = listing.read_text()
    assert text.startswith(other), text
    assert "## skills/vdev/SKILL.md" in text.splitlines(), text
    assert "| A1 | The widget is blue. | because |" in text.splitlines(), text


def test_apply_moves_a_units_own_table_into_a_list_holding_only_another_units_section_leaving_that_section_unchanged_1959(tmp_path, skill_edit):
    skill_edit_step = skill_edit(unit=None, listing=None, stubbed=False).step
    (tmp_path / "skills" / "vdev").mkdir(parents=True)
    unit = tmp_path / "skills" / "vdev" / "SKILL.md"
    unit.write_text(
        "Prose.\n\n## Requirements\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    other = ("## skills/other/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
             "| B1 | The gadget is red. | colour |\n")
    listing = tmp_path / "skills" / "vdev" / "REQUIREMENTS.md"
    listing.write_text(other)

    skill_edit_step.apply(str(tmp_path / "issue.md"), "skills/vdev/SKILL.md")

    text = listing.read_text()
    assert text.startswith(other), text
    assert "## skills/vdev/SKILL.md" in text.splitlines(), text
    assert "| A1 | The widget is blue. | because |" in text.splitlines(), text
    assert "## Requirements" not in unit.read_text().splitlines(), unit.read_text()


def test_a_guard_rejected_attempts_edits_to_the_unit_are_reset_before_the_next_author_attempt_1959(tmp_path, skill_edit, run_cli):
    unit = tmp_path / "unit.md"
    seen = []

    def author(*a):
        seen.append(unit.read_text())
        unit.write_text("Edited by attempt %d.\n" % len(seen))
        return 0

    def guard(unit, base, pins):
        return ["stray.md"] if seen else []

    skill_edit_step = skill_edit(author=author, guard=guard).step

    run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"], env={"VERI_SKILL_EDIT_BUDGET": "2"})

    assert seen == ["The widget is painted a deep blue.\n"] * 2, seen


def test_a_list_already_passing_the_grader_launches_no_author_commits_the_list_and_graded_and_exits_3_1959(tmp_path, skill_edit, run_cli):
    case = skill_edit(grade=(0, ""))

    code, out, err = run_cli(case.step, [str(tmp_path / "issue.md"), "unit.md"])

    launched, commands = case.launched, case.commands
    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert launched == [], launched
    assert len(commits) == 1 and "REQUIREMENTS.md" in commits[0], commands
    assert any(p.endswith("GRADED") or "GRADED" in p for p in commits[0]), commits
    assert code == 3, (code, out, err)


def test_an_added_step_on_a_unit_graded_pass_before_any_author_ran_exits_2_naming_the_step_launching_and_committing_nothing_2063(tmp_path, skill_edit, run_cli):
    case = skill_edit(grade=(0, ""))
    skill_edit_step = case.step
    grade_prose = importlib.import_module("veri.grade_prose")
    grade_prose.record_graded("unit.md", grade_prose.signature("REQUIREMENTS.md", "unit.md"), "g1")
    graded_before = (tmp_path / "GRADED").read_text()
    step = "map each grade to the mode stop-run.sh accepts"

    code, out, err = run_cli(skill_edit_step, ["--added", step, str(tmp_path / "issue.md"), "unit.md"])
    usage = run_cli(skill_edit_step, [])[2]

    launched, events, commands = case.launched, case.events, case.commands
    commits = [c for c in commands if c[:2] in (["git", "add"], ["git", "commit"])]
    assert (code, step in err, launched, events, commits, (tmp_path / "GRADED").read_text(), "--added" in usage) \
        == (2, True, [], [], [], graded_before, True), (code, err, launched, events, commits, usage)


def test_an_added_step_stating_a_row_new_to_the_list_on_a_unit_graded_pass_launches_no_author_commits_the_row_and_graded_and_exits_3_2513(tmp_path, skill_edit, run_cli):
    prose = "The widget is painted a deep blue and round.\n"
    case = skill_edit(
        unit=prose,
        issue="## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | shape |\n",
        grade=(0, ""))

    code, out, err = run_cli(case.step, ["--added", "add the round row", str(tmp_path / "issue.md"), "unit.md"])

    launched, commands = case.launched, case.commands
    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert launched == [], launched
    assert (tmp_path / "unit.md").read_text() == prose
    assert "A2" in (tmp_path / "REQUIREMENTS.md").read_text()
    assert len(commits) == 1 and "REQUIREMENTS.md" in commits[0] and any("GRADED" in p for p in commits[0]), commands
    assert code == 3, (code, out, err)


def test_an_added_step_whose_issue_rewords_a_listed_row_on_a_unit_graded_pass_launches_no_author_rewrites_the_row_regrades_commits_and_exits_3_2997(tmp_path, skill_edit, run_cli):
    prose = "The widget is painted a deep blue.\n"
    case = skill_edit(
        unit=prose,
        listing="## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is red. | because |\n",
        issue="## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| A1<reword> | The widget is blue. | because |\n",
        grade=(0, ""))

    code, out, err = run_cli(case.step, ["--added", "reword A1", str(tmp_path / "issue.md"), "unit.md"])

    launched, graded, commands = case.launched, case.graded, case.commands
    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    listed = (tmp_path / "REQUIREMENTS.md").read_text()
    assert launched == [], launched
    assert "The widget is blue." in listed and "The widget is red." not in listed, listed
    assert len(graded) == 1, graded
    assert (tmp_path / "unit.md").read_text() == prose
    assert len(commits) == 1 and "REQUIREMENTS.md" in commits[0] and any("GRADED" in p for p in commits[0]), commands
    assert code == 3, (code, out, err)


def test_a_step_whose_issue_row_id_cell_is_id_reword_naming_a_listed_row_with_different_text_rewords_it_under_its_bare_id_and_exits_as_a_reword_does_3320(tmp_path, skill_edit, run_cli):
    case = skill_edit(
        listing="## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is red. | because |\n",
        issue="## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| A1<reword> | The widget is blue. | because |\n",
        grade=(0, ""))

    code, out, err = run_cli(case.step, ["--added", "reword A1", str(tmp_path / "issue.md"), "unit.md"])

    launched = case.launched
    listed = (tmp_path / "REQUIREMENTS.md").read_text()
    assert launched == [], launched
    assert "| A1 | The widget is blue. | because |" in listed and "The widget is red." not in listed, listed
    assert "<reword>" not in listed, listed
    assert code == 3, (code, out, err)


def test_a_step_whose_issue_row_x2_reword_states_the_full_text_the_section_holds_under_x1_exits_2_naming_both_ids_before_any_git_call_leaving_the_files_byte_identical_4682(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    prose = "The widget is painted a deep blue.\n"
    listing = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
               "| X1 | The widget is blue. | because |\n| X2 | The widget is red. | since |\n")
    skill_edit_step = skill_edit(
        unit=prose, listing=listing,
        issue="## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| X2<reword> | The widget is blue. | because |\n",
        stubbed=False).step
    (tmp_path / "GRADED").write_text("")
    launched = []
    fake = fake_processes.answers({}, default=lambda line, **_: (0, "abc1234\n", ""))
    leaf = importlib.import_module("veri.leaf")
    monkeypatch.setattr(leaf, "launch", lambda *a, **k: launched.append(a))

    code, out, err = run_cli(skill_edit_step, ["--added", "reword X2", str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "X2" in err and "X1" in err, fake.calls, launched) == (2, True, [], []), (code, err, fake.calls, launched)
    assert (tmp_path / "REQUIREMENTS.md").read_text() == listing
    assert (tmp_path / "unit.md").read_text() == prose
    assert (tmp_path / "GRADED").read_text() == ""


def test_a_reword_row_differing_from_the_held_row_in_its_cells_is_not_refused_as_stating_the_held_full_text_when_both_hold_an_unescaped_pipe_in_a_code_span_4752(tmp_path, skill_edit, run_cli):
    case = skill_edit(
        listing="## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| SC1 | offers `a|b` here. | old why |\n",
        issue="## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| SC1<reword> | offers `a|b` here. | new why |\n",
        grade=(0, ""))

    issue_rows = case.step.unit_rows(str(tmp_path / "issue.md"), "unit.md")
    assert case.step._duplicated_rewords(issue_rows, str(tmp_path / "REQUIREMENTS.md"), "unit.md") == []
    code, out, err = run_cli(case.step, ["--added", "reword SC1", str(tmp_path / "issue.md"), "unit.md"])

    assert "states the full text the unit already holds" not in err, (code, out, err)


def test_an_issue_row_not_splitting_into_id_requirement_and_why_exits_2_naming_the_row_id_and_the_cell_count_4752(tmp_path, skill_edit, run_cli):
    listing = "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is red. | because |\n"
    case = skill_edit(
        listing=listing,
        issue="## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| SC1 | offers `a|b` here. | why |\n",
        grade=(0, ""))

    code, out, err = run_cli(case.step, ["--added", "add SC1", str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "Requirement row SC1 splits into 4 cells" in err, "escape" in err) == (2, True, True), (code, out, err)
    assert (tmp_path / "REQUIREMENTS.md").read_text() == listing


def test_an_issue_row_with_too_few_cells_exits_2_naming_the_row_id_and_the_cell_count_without_advising_an_escape_4752(tmp_path, skill_edit, run_cli):
    listing = "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is red. | because |\n"
    case = skill_edit(
        listing=listing,
        issue="## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| SC1 | text |\n",
        grade=(0, ""))

    code, out, err = run_cli(case.step, ["--added", "add SC1", str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "Requirement row SC1 splits into 2 cells" in err, "escape" in err) == (2, True, False), (code, out, err)
    assert (tmp_path / "REQUIREMENTS.md").read_text() == listing


def test_an_added_step_whose_issue_rewords_a_listed_row_on_a_unit_graded_pass_appends_a_skill_edit_no_author_event_naming_the_unit_2997(tmp_path, skill_edit, run_cli):
    case = skill_edit(
        listing="## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is red. | because |\n",
        issue="## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| A1<reword> | The widget is blue. | because |\n",
        grade=(0, ""))

    code, out, err = run_cli(case.step, ["--added", "reword A1", str(tmp_path / "issue.md"), "unit.md"])

    events = case.events
    named = [a for a in events if "skill-edit-no-author" in a]
    assert len(named) == 1 and "unit=unit.md" in named[0][-1], (code, out, err, events)


def test_an_added_step_whose_reworded_row_the_prose_does_not_meet_launches_the_author_with_the_reworded_text_not_the_old_2997(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    prompts = []

    def launch(name, prompt, *args, env=None):
        prompts.append(open(prompt).read())
        return subprocess.CompletedProcess([name], 0, b"", None)

    def run(line, **kw):
        return 0, "abc1234\n", ""

    skill_edit_step = skill_edit(
        unit="The widget is painted a deep green.\n",
        listing="## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is red. | because |\n",
        issue="## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| A1<reword> | The widget is blue. | because |\n",
        grade=[(1, "A1: FAIL - not blue\n"), (0, "")], author=None, run=None,
        guard=lambda unit, base, pins: []).step
    leaf = importlib.import_module("veri.leaf")
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    fake_processes.answers({"": run})
    monkeypatch.setattr(leaf, "launch", launch)

    code, out, err = run_cli(skill_edit_step, ["--added", "reword A1", str(tmp_path / "issue.md"), "unit.md"])

    assert len(prompts) == 1, (code, out, err, prompts)
    assert "The widget is blue." in prompts[0] and "The widget is red." not in prompts[0], prompts[0]


def test_an_added_step_stating_only_rows_the_list_already_carries_on_a_unit_graded_pass_exits_2_naming_the_step_leaving_list_unit_and_graded_unmodified_2583(tmp_path, skill_edit, run_cli):
    prose = "The widget is painted a deep blue.\n"
    listing = "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"
    case = skill_edit(
        unit=prose, listing=listing,
        issue="## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n",
        grade=(0, ""))
    grade_prose = importlib.import_module("veri.grade_prose")
    grade_prose.record_graded("unit.md", grade_prose.signature("REQUIREMENTS.md", "unit.md"), "g1")
    graded_before = (tmp_path / "GRADED").read_text()
    step = "restate the blue row"

    code, out, err = run_cli(case.step, ["--added", step, str(tmp_path / "issue.md"), "unit.md"])

    launched, commands = case.launched, case.commands
    commits = [c for c in commands if c[:2] in (["git", "add"], ["git", "commit"])]
    assert (code, step in err, launched, commits, (tmp_path / "GRADED").read_text()) == (2, True, [], [], graded_before), \
        (code, err, launched, commits)
    assert (tmp_path / "REQUIREMENTS.md").read_text() == listing
    assert (tmp_path / "unit.md").read_text() == prose


def test_an_added_step_on_a_unit_graded_pass_exits_2_naming_the_step_leaving_the_list_unchanged_when_every_issue_row_equals_its_listed_row_2997(tmp_path, skill_edit, run_cli):
    prose = "The widget is painted a deep blue and round.\n"
    rows = "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | because |\n"
    listing = "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n" + rows
    case = skill_edit(
        unit=prose, listing=listing,
        issue="## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n" + rows,
        grade=(0, ""))
    grade_prose = importlib.import_module("veri.grade_prose")
    grade_prose.record_graded("unit.md", grade_prose.signature("REQUIREMENTS.md", "unit.md"), "g1")
    graded_before = (tmp_path / "GRADED").read_text()

    code, out, err = run_cli(case.step, ["--added", "restate both rows", str(tmp_path / "issue.md"), "unit.md"])

    launched, commands = case.launched, case.commands
    commits = [c for c in commands if c[:2] in (["git", "add"], ["git", "commit"])]
    assert code == 2 and "graded PASS before any author ran" in err, (code, out, err)
    assert launched == [] and commits == [], (launched, commits)
    assert (tmp_path / "REQUIREMENTS.md").read_text() == listing
    assert (tmp_path / "GRADED").read_text() == graded_before


def test_an_added_step_on_a_unit_graded_pass_with_a_current_graded_line_and_no_new_row_exits_2_naming_the_step_leaving_requirements_unit_and_graded_unmodified_3310(tmp_path, skill_edit, run_cli):
    prose = "The widget is painted a deep blue.\n"
    listing = "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"
    case = skill_edit(unit=prose, listing=listing, grade=(0, ""))
    grade_prose = importlib.import_module("veri.grade_prose")
    grade_prose.record_graded("unit.md", grade_prose.signature("REQUIREMENTS.md", "unit.md"), "g1")
    graded_before = (tmp_path / "GRADED").read_text()
    step = "sign the blue unit"

    code, out, err = run_cli(case.step, ["--added", step, str(tmp_path / "issue.md"), "unit.md"])

    launched, commands = case.launched, case.commands
    commits = [c for c in commands if c[:2] in (["git", "add"], ["git", "commit"])]
    assert (code, step in err, launched, commits) == (2, True, [], []), (code, err, launched, commits)
    assert (tmp_path / "REQUIREMENTS.md").read_text() == listing
    assert (tmp_path / "unit.md").read_text() == prose
    assert (tmp_path / "GRADED").read_text() == graded_before


def test_an_added_step_on_a_unit_whose_grade_fails_first_runs_its_author_attempt_commits_the_list_graded_and_unit_and_exits_0_2063(tmp_path, skill_edit, run_cli):
    case = skill_edit(grade=[(1, "A1: FAIL - no\n"), (0, "")], guard=lambda unit, base, pins: [])

    code, out, err = run_cli(case.step, ["--added", "map each grade to a mode", str(tmp_path / "issue.md"), "unit.md"])

    launched, commands = case.launched, case.commands
    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert len(launched) == 1 and code == 0, (code, err, launched)
    assert len(commits) == 1 and all(any(n in p for p in commits[0]) for n in ("REQUIREMENTS.md", "GRADED", "unit.md")), commands


def test_the_author_prompt_names_every_pin_file_and_tells_it_to_update_the_checksum_or_verbatim_pins_there_2232(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    prompts = []

    def run(line, **kw):
        cmd = fake.argvs[-1]
        if cmd[0].endswith("supervise.sh"):
            prompts.append(open(cmd[3]).read())
        return 0, "abc1234\n", ""

    skill_edit_step = skill_edit(grade=lambda *a: next(grades), author=None, run=None,
                                 guard=lambda unit, base, pins: []).step
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    fake = fake_processes.answers({"": run})
    for pins in (["tests/test_alpha.py", "tests/test_beta.py"], []):
        grades = iter([(1, "A1: FAIL - no\n"), (0, "")])
        run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md", *pins])

    with_pins, without = prompts
    assert (all(p in with_pins for p in ["tests/test_alpha.py", "tests/test_beta.py", "checksum", "verbatim"]),
            "tests/test_" in without) == (True, False), (with_pins, without)


def test_a_rejected_attempts_edits_to_a_pin_file_are_reset_with_the_unit_so_the_committed_pin_matches_the_committed_unit_2232(tmp_path, skill_edit, run_cli):
    committed = []
    attempts = iter([
        lambda: ((tmp_path / "unit.md").write_text("The widget is red.\n"),
                 (tmp_path / "pin.py").write_text("PINNED = 'The widget is red.'\n")),
        lambda: (tmp_path / "unit.md").write_text((tmp_path / "unit.md").read_text() + "It hums.\n"),
    ])

    def run(cmd, **kw):
        if cmd[:2] == ["git", "commit"]:
            committed.append(((tmp_path / "unit.md").read_text(), (tmp_path / "pin.py").read_text()))
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    skill_edit_step = skill_edit(
        unit="The widget is blue.\n",
        listing="## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget hums. | because |\n",
        grade=[(1, "A1: FAIL - silent\n"), (1, "A1: FAIL - red is wrong\n"), (0, "")],
        author=lambda *a: next(attempts)() and 0, run=run, guard=lambda unit, base, pins: []).step
    (tmp_path / "pin.py").write_text("PINNED = 'The widget is blue.'\n")

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md", "pin.py"])

    assert (code, committed) == (0, [("The widget is blue.\nIt hums.\n", "PINNED = 'The widget is blue.'\n")]), (code, err)


def test_an_added_step_on_a_unit_no_requirements_list_claims_exits_2_naming_the_step_launching_and_committing_nothing_2236(tmp_path, skill_edit, run_cli):
    case = skill_edit(listing=None, grade=(0, ""))
    step = "map each grade to the mode stop-run.sh accepts"

    code, out, err = run_cli(case.step, ["--added", step, str(tmp_path / "issue.md"), "unit.md"])

    launched, commands = case.launched, case.commands
    commits = [c for c in commands if c[:2] in (["git", "add"], ["git", "commit"])]
    assert (code, step in err, launched, commits) == (2, True, [], []), (code, err, launched, commits)


def _next_case_2262(skill_edit, list_rows, issue_rows, heading="unit.md"):
    """A unit, its list holding list_rows (None: no list), and an issue stating issue_rows under heading.

    A heading ending " (new)" names a unit that does not exist yet, so no unit.md is written.
    """
    table = "| ID | Requirement | Why |\n|---|---|---|\n"
    return skill_edit(
        unit=None if heading.endswith(" (new)") else UNIT_TEXT,
        listing=None if list_rows is None else "## unit.md\n\n" + table + "".join(r + "\n" for r in list_rows),
        issue="## Requirements\n\n### %s\n\n" % heading + table + "".join(r + "\n" for r in issue_rows),
        stubbed=False).step


def test_apply_gives_a_prefix_next_row_the_next_free_number_for_its_prefix_and_copies_a_numbered_row_as_is_2262(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        ["| PL3 | The widget is blue. | because |",
         "| PL7 | The widget is round. | shape |",
         "| CY9 | The widget is old. | age |"],
        ["| PL<next> | The widget is shiny. | gloss |",
         "| CY12 | The widget is heavy. | weight |"])
    requirements = importlib.import_module("veri.requirements")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    ids = [row.split("\t")[0] for row in requirements.claims(str(tmp_path / "REQUIREMENTS.md"), "unit.md").splitlines()]
    assert ids == ["PL3", "PL7", "CY9", "PL8", "CY12"], ids


def test_apply_numbers_two_next_rows_of_one_prefix_in_issue_order_as_max_plus_1_then_max_plus_2_2262(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        ["| PL3 | The widget is blue. | because |",
         "| PL7 | The widget is round. | shape |"],
        ["| PL<next> | The widget is shiny. | gloss |",
         "| PL<next> | The widget is heavy. | weight |"])

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("| PL")]
    assert [row.split(" | ")[0] for row in rows] == ["| PL3", "| PL7", "| PL8", "| PL9"], rows
    assert ["shiny" in rows[2], "heavy" in rows[3]] == [True, True], rows


def test_apply_numbers_a_prefix_next_row_1_when_the_list_holds_no_row_of_that_prefix_including_a_list_it_creates_2262(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        None,
        ["| PL<next> | The widget is shiny. | gloss |"],
        heading="unit.md (new)")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("|")]
    assert rows[2:] == ["| PL1 | The widget is shiny. | gloss |"], rows


def test_apply_numbers_a_prefix_next_row_1_when_the_unit_exists_but_no_requirements_list_claims_it_2262(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        None,
        ["| PL<next> | The widget is shiny. | gloss |"])

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("|")]
    assert rows[2:] == ["| PL1 | The widget is shiny. | gloss |"], rows


def test_an_issue_row_whose_id_is_neither_prefix_digits_nor_prefix_next_exits_2_naming_the_id_and_leaves_the_list_byte_identical_2262(tmp_path, skill_edit, run_cli):
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| PL3 | The widget is blue. | because |\n")
    skill_edit_step = skill_edit(
        listing=original,
        issue="## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| PLsoon | The widget is shiny. | gloss |\n",
        grade=(0, "")).step

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "PLsoon" in err, (tmp_path / "REQUIREMENTS.md").read_text()) == (2, True, original), (code, err)


def test_an_issue_with_rows_under_a_unit_heading_outside_requirements_exits_2_naming_the_unit_leaving_list_unit_and_graded_unchanged_2856(tmp_path, skill_edit, run_cli):
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| PL3 | The widget is blue. | because |\n")
    skill_edit_step = skill_edit(
        listing=original,
        issue="## Requirements\n\n### other.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| OT1 | Other is prose. | because |\n\n"
        "## unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| PL4 | The widget is shiny. | gloss |\n",
        grade=(0, "")).step
    (tmp_path / "other.md").write_text("Other prose.\n")

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "unit.md" in err and "not under ## Requirements" in err,
            (tmp_path / "REQUIREMENTS.md").read_text(), (tmp_path / "unit.md").read_text(),
            (tmp_path / "GRADED").exists()) == (
        2, True, original, "The widget is painted a deep blue.\n", False), (code, err)


def test_an_issue_with_a_requirements_row_under_no_unit_heading_exits_2_naming_the_problem_leaving_list_unit_and_graded_unchanged_2856(tmp_path, skill_edit, run_cli):
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| PL3 | The widget is blue. | because |\n")
    skill_edit_step = skill_edit(
        listing=original,
        issue="## Requirements\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| PL4 | The widget is shiny. | gloss |\n",
        grade=(0, "")).step

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "under no ### unit heading" in err,
            (tmp_path / "REQUIREMENTS.md").read_text(), (tmp_path / "unit.md").read_text(),
            (tmp_path / "GRADED").exists()) == (
        2, True, original, "The widget is painted a deep blue.\n", False), (code, err)


def test_an_issue_with_a_requirements_section_but_no_heading_for_the_stepped_unit_exits_2_naming_the_unit_leaving_list_unit_and_graded_unchanged_2856(tmp_path, skill_edit, run_cli):
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| PL3 | The widget is blue. | because |\n")
    skill_edit_step = skill_edit(
        listing=original,
        issue="## Requirements\n\n### other.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| OT1 | Other is prose. | because |\n",
        grade=(0, "")).step
    (tmp_path / "other.md").write_text("Other prose.\n")

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "unit.md" in err,
            (tmp_path / "REQUIREMENTS.md").read_text(), (tmp_path / "unit.md").read_text(),
            (tmp_path / "GRADED").exists()) == (
        2, True, original, "The widget is painted a deep blue.\n", False), (code, err)


def test_a_well_formed_unit_heading_under_requirements_keeps_the_step_exiting_0_with_its_rows_applied_and_an_author_attempt_passed_2856(tmp_path, skill_edit, run_cli):
    case = skill_edit(
        issue="## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget is round. | because |\n",
        grade=[(1, "A2: FAIL - no\n"), (0, "")], guard=lambda unit, base, pins: [])

    code, out, err = run_cli(case.step, [str(tmp_path / "issue.md"), "unit.md"])

    launched = case.launched
    assert (code, len(launched), "A2" in (tmp_path / "REQUIREMENTS.md").read_text()) == (0, 1, True), (code, err, launched)


def test_a_change_only_step_on_an_issue_with_no_requirements_section_keeps_exiting_0_2856(tmp_path, skill_edit, run_cli):
    def author(*a):
        (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
        return 0

    case = skill_edit(unit="The widget is painted a deep blue.\n- a merge is in flight;\n", grade=(0, ""),
                      author=author, guard=lambda unit, base, pins: [])

    code, out, err = run_cli(case.step, ["--change", "delete the bullet", str(tmp_path / "issue.md"), "unit.md"])

    launched = case.launched
    assert (code, len(launched)) == (0, 1), (code, err, launched)


def test_apply_numbers_a_prefix_next_row_past_the_max_over_the_lists_ids_and_the_issues_own_explicit_ids_2262(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        ["| PL5 | The widget is blue. | because |"],
        ["| PL<next> | The widget is shiny. | gloss |",
         "| PL7 | The widget is heavy. | weight |"])
    requirements = importlib.import_module("veri.requirements")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    ids = [row.split("\t")[0] for row in requirements.claims(str(tmp_path / "REQUIREMENTS.md"), "unit.md").splitlines()]
    assert ids == ["PL5", "PL8", "PL7"], ids


def test_an_issue_whose_rows_for_one_unit_resolve_to_the_same_id_twice_exits_2_naming_the_id_and_leaves_the_list_byte_identical_2262(tmp_path, skill_edit, run_cli):
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| PL3 | The widget is blue. | because |\n")
    skill_edit_step = skill_edit(
        listing=original,
        issue="## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| PL7 | The widget is shiny. | gloss |\n"
        "| PL7 | The widget is heavy. | weight |\n",
        grade=(0, "")).step

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (tmp_path / "REQUIREMENTS.md").read_text() == original, (code, err)
    assert (code, "PL7" in err) == (2, True), (code, err)


def test_apply_still_rewords_a_list_row_when_the_issue_states_its_explicit_id_beside_a_prefix_next_row_2262(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        ["| PL5 | The widget is blue. | because |"],
        ["| PL<next> | The widget is shiny. | gloss |",
         "| PL5 | The widget is deep blue. | because |"])
    requirements = importlib.import_module("veri.requirements")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = requirements.claims(str(tmp_path / "REQUIREMENTS.md"), "unit.md").splitlines()
    assert rows == ["PL5\tThe widget is deep blue.", "PL6\tThe widget is shiny."], rows


def test_apply_writes_a_prefix_next_rows_other_cells_byte_for_byte_keeping_an_escaped_pipe_2262(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        ["| PL5 | The widget is blue. | because |"],
        ["| PL<next> | The widget shows a\\|b. | gloss\\|shine |"])

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("| PL")]
    assert rows == ["| PL5 | The widget is blue. | because |",
                    "| PL6 | The widget shows a\\|b. | gloss\\|shine |"], rows


def test_apply_numbers_a_prefix_next_row_past_the_issues_explicit_ids_when_the_unit_exists_but_no_requirements_list_claims_it_2262(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        None,
        ["| PL<next> | The widget is shiny. | gloss |",
         "| PL1 | The widget is heavy. | weight |"])

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("| PL")]
    assert rows == ["| PL2 | The widget is shiny. | gloss |",
                    "| PL1 | The widget is heavy. | weight |"], rows


def test_apply_numbers_a_prefix_next_row_past_the_issues_explicit_ids_in_a_list_it_creates_under_a_new_heading_2262(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        None,
        ["| PL<next> | The widget is shiny. | gloss |",
         "| PL1 | The widget is heavy. | weight |"],
        heading="unit.md (new)")

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("| PL")]
    assert rows == ["| PL2 | The widget is shiny. | gloss |",
                    "| PL1 | The widget is heavy. | weight |"], rows


HUMS_LISTING = "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget hums. | because |\n"


def test_a_refused_attempts_edit_to_a_file_the_guard_names_is_restored_so_the_next_attempt_is_accepted_with_the_file_unchanged_2281(tmp_path, skill_edit, run_cli):
    attempts = iter([
        lambda: ((tmp_path / "unit.md").write_text("The widget hums.\n"),
                 (tmp_path / "stray_test.py").write_text("EDITED = 1\n")),
        lambda: (tmp_path / "unit.md").write_text("The widget hums.\n"),
    ])
    guarded = []

    def guard(unit, base, pins):
        guarded.append([unit, base, *pins])
        return ["stray_test.py"] if len(guarded) == 2 else []

    skill_edit_step = skill_edit(unit="The widget is blue.\n", listing=HUMS_LISTING,
                                 grade=[(1, "A1: FAIL - silent\n"), (0, "")],
                                 author=lambda *a: next(attempts)() and 0, guard=guard).step
    (tmp_path / "stray_test.py").write_text("ORIGINAL = 1\n")

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, (tmp_path / "stray_test.py").read_text()) == (0, "ORIGINAL = 1\n"), (code, err)


def test_exhausted_author_attempts_exit_1_with_the_tree_as_before_the_run_requirements_list_included_2281(tmp_path, skill_edit, run_cli):
    authored = []

    def author(*a):
        authored.append(a)
        (tmp_path / "unit.md").write_text("The widget hums.\n")
        (tmp_path / "stray_test.py").write_text("EDITED = 1\n")
        return 0

    def guard(unit, base, pins):
        return ["stray_test.py"] if authored else []

    skill_edit_step = skill_edit(
        unit="The widget is blue.\n", listing=HUMS_LISTING,
        issue="## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A2 | The widget glows. | light |\n",
        grade=(1, "A2: FAIL - dark\n"), author=author, guard=guard).step
    (tmp_path / "stray_test.py").write_text("ORIGINAL = 1\n")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    after = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert (code, after) == (1, before), (code, err)


def test_a_guard_refusal_never_deletes_a_tdd_file_the_guard_names_that_it_holds_no_snapshot_for_2281(tmp_path, skill_edit, run_cli):
    def guard(unit, base, pins):
        return [".tdd/issue-9-added.md", ".tdd/issue-9.md"]

    skill_edit_step = skill_edit(unit="The widget is blue.\n", listing=HUMS_LISTING,
                                 grade=(1, "A1: FAIL - silent\n"), guard=guard).step
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-9-added.md").write_text("an untracked added ledger\n")
    (tmp_path / ".tdd" / "issue-9.md").write_text("a dirty ledger\n")
    before = {p.name: p.read_bytes() for p in (tmp_path / ".tdd").iterdir()}

    run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"], env={"VERI_SKILL_EDIT_BUDGET": "1"})

    after = {p.name: p.read_bytes() for p in (tmp_path / ".tdd").iterdir()}
    assert after == before, after


def test_a_guard_refusal_removes_a_new_file_the_author_created_and_the_guard_named_beside_a_surviving_tdd_file_2281(tmp_path, skill_edit, run_cli):
    def guard(unit, base, pins):
        return ["stray.py", ".tdd/issue-9.md"]

    skill_edit_step = skill_edit(unit="The widget is blue.\n", listing=HUMS_LISTING,
                                 grade=(1, "A1: FAIL - silent\n"),
                                 author=lambda *a: (tmp_path / "stray.py").write_text("NEW = 1\n") and 0,
                                 guard=guard).step
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-9.md").write_text("a dirty ledger\n")

    run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"], env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert ((tmp_path / "stray.py").exists(), (tmp_path / ".tdd" / "issue-9.md").read_text()) == (False, "a dirty ledger\n")


def test_a_guard_refusal_leaves_a_pre_existing_untracked_symlink_the_guard_names_and_still_removes_a_new_file_2281(tmp_path, skill_edit, run_cli):
    def guard(unit, base, pins):
        return ["link", "stray.py"]

    skill_edit_step = skill_edit(unit="The widget is blue.\n", listing=HUMS_LISTING,
                                 grade=(1, "A1: FAIL - silent\n"),
                                 author=lambda *a: (tmp_path / "stray.py").write_text("NEW = 1\n") and 0,
                                 guard=guard).step
    (tmp_path / "target").mkdir()
    (tmp_path / "link").symlink_to("target", target_is_directory=True)

    run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"], env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert ((tmp_path / "link").is_symlink(), (tmp_path / "stray.py").exists()) == (True, False)


def test_a_pass_on_the_unchanged_text_of_a_unit_with_a_recorded_reject_signs_nothing_in_graded_without_an_author_changing_it_2121(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    case = skill_edit(grade=None, run=None, guard=lambda unit, base, pins: [])
    skill_edit_step = case.step
    grade_prose = skill_edit_step.grade_prose
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
    (tmp_path / ".tdd").mkdir()
    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    sig = grade_prose.signature("REQUIREMENTS.md", "unit.md")
    (tmp_path / ".tdd" / "grade-prose-rejected").write_text("unit.md %s 2026-10-22 earlier\n" % sig)

    def run(line, **kw):
        cmd = fake.argvs[-1]
        if cmd[0] == "git":
            return 0, "abc1234\n", ""
        (tmp_path / ".tdd" / "grade-prose.log").write_text(
            '{"type":"result","subtype":"success","is_error":false,"result":'
            '"BEGIN GRADES\\nA1: PASS - blue\\nVERDICT: PASS\\nEND GRADES"}\n')
        return 0, "", ""

    monkeypatch.setenv("PATH", "")
    fake = fake_processes.answers({"": run})

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    authors = case.launched
    assert (len(authors), (tmp_path / "GRADED").exists()) == (1, False), (code, out, err, authors)


BULLET_UNIT = "The widget is painted a deep blue.\n- a merge is in flight;\n"


def test_a_change_step_on_a_unit_already_graded_pass_launches_an_author_whose_prompt_names_the_change_and_commits_the_unit_list_and_graded_when_the_unit_grades_pass_after_it_2340(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    skill_edit_step = skill_edit(unit=BULLET_UNIT, grade=(0, ""), author=None, run=None,
                                 guard=lambda unit, base, pins: []).step
    change = "delete the bullet - a merge is in flight;"
    prompts = []
    commands = []

    def run(line, **kw):
        cmd = fake.argvs[-1]
        commands.append(cmd)
        if cmd[0].endswith("supervise.sh"):
            prompts.append(open(cmd[3]).read())
            (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
        return 0, "abc1234\n", ""

    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    fake = fake_processes.answers({"": run})

    code, out, err = run_cli(skill_edit_step, ["--change", change, str(tmp_path / "issue.md"), "unit.md"])

    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert code == 0 and len(prompts) == 1 and change in prompts[0], (code, err, prompts)
    assert len(commits) == 1 and all(any(n in p for p in commits[0]) for n in ("REQUIREMENTS.md", "GRADED", "unit.md")), commands


def test_a_run_given_no_change_whose_unit_grades_fail_sends_its_author_a_prompt_without_a_change_to_make_line_2340(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    skill_edit_step = skill_edit(grade=[(1, "A1: FAIL - no\n"), (0, "")], author=None, run=None,
                                 guard=lambda unit, base, pins: []).step
    prompts = []

    def run(line, **kw):
        cmd = fake.argvs[-1]
        if cmd[0].endswith("supervise.sh"):
            prompts.append(open(cmd[3]).read())
        return 0, "abc1234\n", ""

    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    fake = fake_processes.answers({"": run})

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert code == 0 and len(prompts) == 1 and "Change to make:" not in prompts[0], (code, err, prompts)


def test_a_change_step_whose_every_author_attempt_leaves_the_prose_unchanged_spends_the_whole_budget_commits_nothing_and_exits_1_2340(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    skill_edit_step = skill_edit(unit=BULLET_UNIT, grade=(0, ""), author=None, run=None,
                                 guard=lambda unit, base, pins: []).step
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    authors = []
    commits = []

    def run(line, **kw):
        cmd = fake.argvs[-1]
        if cmd[0].endswith("supervise.sh"):
            authors.append(cmd)
        if cmd[:2] == ["git", "commit"]:
            commits.append(cmd)
        return 0, "abc1234\n", ""

    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    fake = fake_processes.answers({"": run})

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               str(tmp_path / "issue.md"), "unit.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "2"})

    after = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert (code, len(authors), len(commits), after) == (1, 2, 0, before), (code, err)


def test_an_added_step_given_a_change_on_a_unit_graded_pass_before_any_author_ran_launches_its_author_and_commits_instead_of_exiting_2_2340(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    skill_edit_step = skill_edit(unit=BULLET_UNIT, grade=(0, ""), author=None, run=None,
                                 guard=lambda unit, base, pins: []).step
    authors = []
    commits = []

    def run(line, **kw):
        cmd = fake.argvs[-1]
        if cmd[0].endswith("supervise.sh"):
            authors.append(cmd)
            (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
        if cmd[:2] == ["git", "commit"]:
            commits.append(cmd)
        return 0, "abc1234\n", ""

    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    fake = fake_processes.answers({"": run})

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "--added", "drop the stale bullet",
                                               str(tmp_path / "issue.md"), "unit.md"])

    assert (code, len(authors), len(commits)) == (0, 1, 1), (code, err, authors, commits)


def test_a_run_given_no_change_on_a_unit_graded_pass_launches_no_author_commits_only_the_list_and_graded_and_exits_3_2340(tmp_path, skill_edit, run_cli):
    case = skill_edit(unit=BULLET_UNIT, grade=(0, ""))

    code, out, err = run_cli(case.step, [str(tmp_path / "issue.md"), "unit.md"])

    launched, commands = case.launched, case.commands
    adds = [c[2:] for c in commands if c[:2] == ["git", "add"]]
    assert launched == [] and code == 3, (code, out, err, launched)
    assert len(adds) == 1 and sorted(adds[0]) == sorted(["REQUIREMENTS.md", "GRADED"]), adds


def test_a_change_step_on_a_unit_already_graded_pass_grades_the_authors_edit_though_the_up_front_passs_own_graded_write_is_uncommitted_2490(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    original = BULLET_UNIT
    edited = "The widget is painted a deep blue.\n"
    skill_edit_step = skill_edit(unit=original, stubbed=False).step
    skill_edit_guard = skill_edit_step.skill_edit_guard
    leaf = importlib.import_module("veri.leaf")
    grade_prose = skill_edit_step.grade_prose
    (tmp_path / "skills" / "tdd" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "tdd" / "grader.conf").write_text("model=sonnet-4\n")
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

    def run(line, **kw):
        return 0, "abc1234\n", ""

    monkeypatch.setattr(grade_prose, "SCRIPTS", str(tmp_path / "skills" / "tdd" / "scripts"))
    monkeypatch.setattr(skill_edit_guard, "_git_ok", lambda *a: True)
    monkeypatch.setattr(skill_edit_guard, "_git_lines", lambda *a: sorted(
        p.name for p in tmp_path.iterdir() if p.name not in (".tdd", "skills")) if a[0] == "ls-files" else [])
    monkeypatch.setattr(grade_prose, "modern_python_dir", lambda: "")
    fake_processes.answers({"": run})
    monkeypatch.setattr(leaf, "launch", launch)

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "issue.md", "unit.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    events = [json.loads(line) for line in (tmp_path / ".tdd" / "events.jsonl").read_text().splitlines()]
    gradings = [e for e in events if e.get("event") == "grading"]
    assert graded_texts == [original, edited], (code, out, err, graded_texts)
    assert (code, (tmp_path / "unit.md").read_text()) == (0, edited), (code, out, err)
    assert [(e.get("unit"), e.get("verdict")) for e in gradings] == [("unit.md", "PASS")] * 2, (events, err)
    assert gradings[-1]["id"] in (tmp_path / "GRADED").read_text(), (gradings, err)


def test_a_change_step_on_a_unit_already_graded_pass_whose_author_writes_a_stray_path_has_it_flagged_and_restored_and_grades_no_attempt_2490(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    original = BULLET_UNIT
    edited = "The widget is painted a deep blue.\n"
    grades = []

    def grade(path, unit):
        grades.append((tmp_path / unit).read_text())
        (tmp_path / "GRADED").write_text("sig\n")
        return 0, ""

    def run(line, **kw):
        cmd = fake.argvs[-1]
        if cmd[0].endswith("supervise.sh"):
            (tmp_path / "unit.md").write_text(edited)
            (tmp_path / "stray.txt").write_text("stray\n")
        return 0, "abc1234\n", ""

    skill_edit_step = skill_edit(unit=original, grade=grade, author=None, run=None).step
    skill_edit_guard = skill_edit_step.skill_edit_guard
    monkeypatch.setattr(skill_edit_guard, "_git_ok", lambda *a: True)
    monkeypatch.setattr(skill_edit_guard, "_git_lines", lambda *a: sorted(
        p.name for p in tmp_path.iterdir()) if a[0] == "ls-files" else [])
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    fake = fake_processes.answers({"": run})

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "issue.md", "unit.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert grades == [original], (code, out, err, grades)
    assert (code, (tmp_path / "stray.txt").exists(), (tmp_path / "unit.md").read_text()) == (1, False, original), (code, out, err)


def test_a_change_step_on_a_unit_already_graded_pass_ends_in_one_commit_of_exactly_the_unit_its_list_its_graded_and_the_pins_2490(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    edited = "The widget is painted a deep blue.\n"
    commands = []

    def grade(path, unit):
        (tmp_path / "GRADED").write_text("sig\n")
        return 0, ""

    def run(line, **kw):
        cmd = fake.argvs[-1]
        commands.append(cmd)
        if cmd[0].endswith("supervise.sh"):
            (tmp_path / "unit.md").write_text(edited)
            (tmp_path / "pin.md").write_text("pin, edited\n")
        return 0, "abc1234\n", ""

    skill_edit_step = skill_edit(unit=BULLET_UNIT, grade=grade, author=None, run=None).step
    skill_edit_guard = skill_edit_step.skill_edit_guard
    (tmp_path / "pin.md").write_text("pin\n")
    monkeypatch.setattr(skill_edit_guard, "_git_ok", lambda *a: True)
    monkeypatch.setattr(skill_edit_guard, "_git_lines", lambda *a: sorted(
        p.name for p in tmp_path.iterdir()) if a[0] == "ls-files" else [])
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    fake = fake_processes.answers({"": run})

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "issue.md", "unit.md", "pin.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert code == 0, (code, out, err)
    assert len(commits) == 1, commits
    assert sorted(commits[0][5:]) == sorted(["unit.md", "REQUIREMENTS.md", "GRADED", "pin.md"]), commits


def test_an_added_flag_before_a_change_flag_applies_both_as_the_change_first_order_does_never_reading_the_literal_change_as_the_issue_body_2472(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    skill_edit_step = skill_edit(unit=BULLET_UNIT, grade=(0, ""), author=None, run=None,
                                 guard=lambda unit, base, pins: []).step
    authors = []
    commits = []

    def run(line, **kw):
        cmd = fake.argvs[-1]
        if cmd[0].endswith("supervise.sh"):
            authors.append(cmd)
            (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
        if cmd[:2] == ["git", "commit"]:
            commits.append(cmd)
        return 0, "abc1234\n", ""

    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    fake = fake_processes.answers({"": run})

    code, out, err = run_cli(skill_edit_step, ["--added", "drop the stale bullet",
                                               "--change", "delete the bullet - a merge is in flight;",
                                               str(tmp_path / "issue.md"), "unit.md"])

    assert (code, len(authors), len(commits)) == (0, 1, 1), (code, err, authors, commits)


def test_the_usage_refusal_for_a_bad_argument_list_names_the_change_flag_beside_the_added_flag_2472(run_cli):
    skill_edit_step = importlib.import_module("veri.skill_edit_step")

    code, out, err = run_cli(skill_edit_step, ["only-one-file"])

    assert (code, "--change" in err, "--added" in err) == (2, True, True), (code, err)


def test_a_change_step_whose_author_edits_only_a_pin_file_leaves_the_unit_byte_identical_fails_the_attempt_as_prose_unchanged_and_commits_nothing_2473(tmp_path, monkeypatch, skill_edit, run_cli):
    commits = []

    def launch(name, prompt, *args, env=None):
        (tmp_path / "pin.md").write_text("pin, edited\n")
        return subprocess.CompletedProcess([name], 0, b"", None)

    def run(cmd, **kw):
        if cmd[:2] == ["git", "commit"]:
            commits.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    skill_edit_step = skill_edit(unit=BULLET_UNIT, grade=(0, ""), author=None, run=run,
                                 guard=lambda unit, base, pins: []).step
    (tmp_path / "pin.md").write_text("pin\n")
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(importlib.import_module("veri.leaf"), "launch", launch)

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "issue.md", "unit.md", "pin.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert (code, "FAIL: the author left the prose and the rows unchanged" in out, commits) == (1, True, []), (code, out, err)


def test_a_change_step_whose_author_edits_the_unit_and_leaves_every_pin_file_untouched_still_succeeds_and_commits_2473(tmp_path, monkeypatch, skill_edit, run_cli):
    commits = []

    def launch(name, prompt, *args, env=None):
        (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
        return subprocess.CompletedProcess([name], 0, b"", None)

    def run(cmd, **kw):
        if cmd[:2] == ["git", "commit"]:
            commits.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    skill_edit_step = skill_edit(unit=BULLET_UNIT, grade=(0, ""), author=None, run=run,
                                 guard=lambda unit, base, pins: []).step
    (tmp_path / "pin.md").write_text("pin\n")
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(importlib.import_module("veri.leaf"), "launch", launch)

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "issue.md", "unit.md", "pin.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert (code, len(commits)) == (0, 1), (code, out, err)


def test_the_author_leaf_is_launched_through_veri_leaf_launch_as_author_skill_edit_1_with_bypass_permissions_and_its_edit_is_graded_2498(tmp_path, monkeypatch, skill_edit, run_cli, fake_processes):
    original = BULLET_UNIT
    edited = "The widget is painted a deep blue.\n"
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

    def run(line, **kw):
        return 0, "abc1234\n", ""

    skill_edit_step = skill_edit(unit=original, grade=grade, author=None, run=None).step
    skill_edit_guard = skill_edit_step.skill_edit_guard
    leaf = importlib.import_module("veri.leaf")
    monkeypatch.setattr(skill_edit_guard, "_git_ok", lambda *a: True)
    monkeypatch.setattr(skill_edit_guard, "_git_lines", lambda *a: sorted(
        p.name for p in tmp_path.iterdir()) if a[0] == "ls-files" else [])
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    fake_processes.answers({"": run})
    monkeypatch.setattr(leaf, "launch", launch)

    code, out, err = run_cli(skill_edit_step, ["--change", "delete the bullet - a merge is in flight;",
                                               "issue.md", "unit.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert [n for n, _ in launched] == ["author-skill-edit-1"], (code, out, err, launched)
    assert launched[0][1][-2:] == ("--permission-mode", "bypassPermissions"), launched
    assert graded_texts == [original, edited], (code, out, err, graded_texts)
    assert (code, (tmp_path / "unit.md").read_text()) == (0, edited), (code, out, err)


A2_ISSUE = ("## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
            "| A2 | The widget glows. | light |\n")


def test_an_author_leaf_failing_exits_2_leaving_the_list_the_unit_and_graded_byte_identical_2576(tmp_path, skill_edit, run_cli):
    def grade(path, unit):
        (tmp_path / "GRADED").write_text("new signature\n")
        return 1, "A2: FAIL - dark\n"

    def author(*a):
        (tmp_path / "unit.md").write_text("The widget glows.\n")
        return 2

    skill_edit_step = skill_edit(issue=A2_ISSUE, grade=grade, author=author,
                                 guard=lambda unit, base, pins: []).step
    (tmp_path / "GRADED").write_text("old signature\n")
    names = ["unit.md", "GRADED", "REQUIREMENTS.md"]
    before = {n: (tmp_path / n).read_bytes() for n in names}

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    after = {n: (tmp_path / n).read_bytes() for n in names}
    assert (code, after) == (2, before), (code, err, after)


def test_a_grader_answering_no_verdict_exits_2_leaving_the_list_the_unit_and_graded_byte_identical_2576(tmp_path, skill_edit, run_cli):
    def grade(path, unit):
        (tmp_path / "GRADED").write_text("new signature\n")
        return 2, "no verdict\n"

    case = skill_edit(issue=A2_ISSUE, grade=grade)
    (tmp_path / "GRADED").write_text("old signature\n")
    names = ["unit.md", "GRADED", "REQUIREMENTS.md"]
    before = {n: (tmp_path / n).read_bytes() for n in names}

    code, out, err = run_cli(case.step, [str(tmp_path / "issue.md"), "unit.md"])

    authors = case.launched
    after = {n: (tmp_path / n).read_bytes() for n in names}
    assert (code, after, authors) == (2, before, []), (code, err, after)


def test_an_as_is_marker_under_a_unit_heading_changes_neither_the_rows_nor_the_unit_apply_reads_2462(tmp_path, skill_edit):
    skill_edit_step = skill_edit(unit=None, listing=None, issue=None, stubbed=False).step
    table =("| ID | Requirement | Why |\n|---|---|---|\n"
             "| A1 | The widget is blue. | because |\n"
             "| A2 | The widget is square. | corners |\n")
    plain = "## Requirements\n\n### unit.md\n\n" + table
    marked = ("## Requirements\n\n### unit.md\n\n"
              "As is: these rows describe the unit's current text.\n\n" + table)
    (tmp_path / "plain.md").write_text(plain)
    (tmp_path / "marked.md").write_text(marked)

    assert skill_edit_step.unit_rows(str(tmp_path / "marked.md"), "unit.md") == \
        skill_edit_step.unit_rows(str(tmp_path / "plain.md"), "unit.md")
    assert skill_edit_step.unit_rows(str(tmp_path / "marked.md"), "unit.md")

    lists = []
    for name in ("plain.md", "marked.md"):
        (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
        (tmp_path / "REQUIREMENTS.md").write_text(
            "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
        assert skill_edit_step._unknown_heading(str(tmp_path / name)) is None
        skill_edit_step.apply(str(tmp_path / name), "unit.md")
        lists.append(((tmp_path / "REQUIREMENTS.md").read_text(), (tmp_path / "unit.md").read_text()))
    assert lists[0] == lists[1], lists


def test_an_added_step_on_a_unit_graded_pass_with_no_graded_line_and_no_new_row_commits_the_signature_launches_no_author_and_exits_3_3310(tmp_path, skill_edit, run_cli):
    grade_prose = importlib.import_module("veri.grade_prose")

    def grade(path, unit):
        grade_prose.record_graded(unit, grade_prose.signature(path, unit), "g1")
        return 0, ""

    case = skill_edit(grade=grade)
    skill_edit_step, launched, commands = case.step, case.launched, case.commands

    code, out, err = run_cli(skill_edit_step, ["--added", "sign the blue unit", str(tmp_path / "issue.md"), "unit.md"])

    adds = [c[2:] for c in commands if c[:2] == ["git", "add"]]
    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert (code, launched) == (3, []), (code, err, launched)
    assert len(commits) == 1 and len(adds) == 1 and "GRADED" in adds[0] and "unit.md" in (tmp_path / "GRADED").read_text(), (adds, commits)



def test_an_added_step_on_a_unit_graded_pass_with_a_stale_graded_line_and_no_new_row_refreshes_the_signature_launches_no_author_and_exits_3_3310(tmp_path, skill_edit, run_cli):
    grade_prose = importlib.import_module("veri.grade_prose")

    def grade(path, unit):
        grade_prose.record_graded(unit, grade_prose.signature(path, unit), "g2")
        return 0, ""

    case = skill_edit(unit="The widget is painted blue.\n", grade=grade)
    skill_edit_step, launched, commands = case.step, case.launched, case.commands
    grade_prose.record_graded("unit.md", grade_prose.signature("REQUIREMENTS.md", "unit.md"), "g1")
    (tmp_path / "unit.md").write_text("The widget is painted a deep blue.\n")
    stale = (tmp_path / "GRADED").read_text()

    code, out, err = run_cli(skill_edit_step, ["--added", "refresh the blue unit", str(tmp_path / "issue.md"), "unit.md"])

    adds = [c[2:] for c in commands if c[:2] == ["git", "add"]]
    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert (code, launched) == (3, []), (code, err, launched)
    assert len(commits) == 1 and len(adds) == 1 and "GRADED" in adds[0] and (tmp_path / "GRADED").read_text() != stale, (adds, commits)


@pytest.mark.parametrize("existing,incoming", [
    ("The widget is red.", "The widget is blue."),
    ("The widget is Red.", "The widget is red."),
    ("The widget is red.", "The widget is blu."),
], ids=["different-words", "case-only", "equal-length"])
def test_a_step_whose_issue_row_has_a_bare_id_the_list_holds_with_different_text_exits_2_naming_the_id_and_both_texts_leaving_the_list_byte_identical_3320(tmp_path, monkeypatch, skill_edit, run_cli, existing, incoming):
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                f"| A1 | {existing} | because |\n")
    case = skill_edit(listing=original, issue=(
        "## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| A1 | " + incoming + " | because |\n"),
        grade=[(1, "FAIL: unit says red\n"), (0, "")])
    skill_edit_step, launched, commands = case.step, case.launched, case.commands
    monkeypatch.setattr(skill_edit_step, "_guard", lambda *a: (0, ""))

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    named = "A1" in err and existing in err and incoming in err
    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert (code, named, len(launched), len(commits), (tmp_path / "REQUIREMENTS.md").read_text()) \
        == (2, True, 0, 0, original), (code, err)


def test_a_step_whose_issue_row_is_identical_to_the_listed_row_of_the_same_bare_id_refuses_nothing_and_leaves_the_list_byte_identical_3320(tmp_path, skill_edit, run_cli):
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| A1 | The widget is blue. | because |\n")
    skill_edit_step = skill_edit(listing=original, issue=(
        "## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"), grade=(0, "")).step

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "A1" in err, (tmp_path / "REQUIREMENTS.md").read_text()) == (3, False, original), (code, err)


def test_a_step_whose_issue_row_is_prefix_next_for_a_list_holding_rows_of_that_prefix_refuses_nothing_and_adds_the_row_under_the_next_free_number_3320(tmp_path, skill_edit, run_cli):
    skill_edit_step = skill_edit(listing=(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | shape |\n"), issue=(
        "## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| A<next> | The widget is shiny. | gloss |\n"), grade=(0, "")).step

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    listed = (tmp_path / "REQUIREMENTS.md").read_text()
    assert (code != 2, "| A3 | The widget is shiny. | gloss |" in listed) == (True, True), (code, err, listed)


def test_a_requirements_table_without_its_header_and_separator_exits_2_naming_the_unit_and_header_before_any_author_while_the_same_row_under_a_header_is_applied_3445(tmp_path, skill_edit, run_cli):
    original = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
                "| M9 | The widget is blue. | because |\n")
    case = skill_edit(listing=original, issue=None, grade=(0, ""))
    skill_edit_step, authors = case.step, case.launched

    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| M9<reword> | new text | why |\n")
    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, "unit.md" in err and "header" in err, authors,
            (tmp_path / "REQUIREMENTS.md").read_text()) == (2, True, [], original), (code, err)

    (tmp_path / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n| M9<reword> | new text | why |\n")
    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code != 2, "| M9 | new text | why |" in (tmp_path / "REQUIREMENTS.md").read_text()) == (True, True), (code, err)


def test_a_requirements_table_with_the_header_line_but_a_missing_or_wrong_separator_exits_2_naming_the_unit_before_any_author_while_the_correct_separator_is_accepted_3445(tmp_path, skill_edit, run_cli):
    row = "| A2 | The widget is round. | because |\n"
    head = "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n"
    case = skill_edit(listing=None, issue=None, grade=(1, "A2: FAIL - no\n"), author=1,
                      guard=lambda unit, base, pins: [])
    skill_edit_step, launched = case.step, case.launched

    outcomes = {}
    for name, separator in (("short", "|--|--|\n"), ("none", ""), ("correct", "|---|---|---|\n")):
        launched.clear()
        (tmp_path / "issue.md").write_text(head + separator + row)
        code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])
        outcomes[name] = (code == 2 and "unit.md" in err, len(launched) > 0)

    assert outcomes == {"short": (True, False), "none": (True, False), "correct": (False, True)}, outcomes


def test_a_requirements_table_with_the_separator_line_but_a_wrong_header_line_exits_2_naming_the_unit_before_any_author_while_the_exact_header_is_accepted_3445(tmp_path, skill_edit, run_cli):
    row = "| A2 | The widget is round. | because |\n"
    case = skill_edit(listing=None, issue=None, grade=(1, "A2: FAIL - no\n"), author=1,
                      guard=lambda unit, base, pins: [])
    skill_edit_step, launched = case.step, case.launched

    outcomes = {}
    for name, header in (("wrong", "| A | B | C |\n"), ("exact", "| ID | Requirement | Why |\n")):
        launched.clear()
        (tmp_path / "issue.md").write_text(
            "## Requirements\n\n### unit.md\n\n" + header + "|---|---|---|\n" + row)
        code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])
        outcomes[name] = (code == 2 and "unit.md" in err, len(launched) > 0)

    assert outcomes == {"wrong": (True, False), "exact": (False, True)}, outcomes


def test_apply_skips_an_explicit_new_id_row_whose_text_the_unit_already_holds_under_another_id_3589(tmp_path, skill_edit):
    held = (
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| PF60 | The widget is round. | shape |\n"
        "| PF61 | The widget is blue. | because |\n")
    skill_edit_step = skill_edit(listing=held, issue=(
        "## Requirements\n\n### unit.md\n\n"
        "| ID | Requirement | Why |\n|---|---|---|\n"
        "| PF62 | The widget is blue. | because |\n"), stubbed=False).step

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    assert (tmp_path / "REQUIREMENTS.md").read_text() == held


def test_apply_run_twice_on_one_prefix_next_row_leaves_the_section_byte_identical_to_after_the_first_run_3589(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        ["| PF60 | The widget is round. | shape |"],
        ["| PF<next> | The widget is blue. | because |"])

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")
    after_first = (tmp_path / "REQUIREMENTS.md").read_text()
    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    assert (tmp_path / "REQUIREMENTS.md").read_text() == after_first
    assert after_first.count("The widget is blue.") == 1, after_first


def test_apply_still_appends_a_prefix_next_row_whose_requirement_text_differs_from_every_held_row_under_the_next_free_id_3589(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        ["| PF60 | The widget is round. | shape |"],
        ["| PF<next> | The widget is blue. | because |"])

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("| PF")]
    assert rows == ["| PF60 | The widget is round. | shape |", "| PF61 | The widget is blue. | because |"], rows


def test_apply_still_appends_a_prefix_next_row_whose_requirement_text_equals_a_held_row_but_whose_why_differs_under_the_next_free_id_3589(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        ["| PF60 | The widget is blue. | because |"],
        ["| PF<next> | The widget is blue. | for another reason |"])

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    rows = [line for line in (tmp_path / "REQUIREMENTS.md").read_text().splitlines() if line.startswith("| PF")]
    assert rows == ["| PF60 | The widget is blue. | because |", "| PF61 | The widget is blue. | for another reason |"], rows


def test_apply_still_appends_a_prefix_next_row_whose_text_equals_a_row_held_only_in_another_units_section_under_the_next_free_id_3589(tmp_path, skill_edit):
    skill_edit_step = _next_case_2262(
        skill_edit,
        ["| PF60 | The widget is round. | shape |"],
        ["| PF<next> | The widget is blue. | because |"])
    table = "| ID | Requirement | Why |\n|---|---|---|\n"
    mine = (tmp_path / "REQUIREMENTS.md").read_text()
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## other.md\n\n" + table + "| OT1 | The widget is blue. | because |\n\n" + mine)

    skill_edit_step.apply(str(tmp_path / "issue.md"), "unit.md")

    section = (tmp_path / "REQUIREMENTS.md").read_text().split("## unit.md")[1]
    rows = [line for line in section.splitlines() if line.startswith("| PF")]
    assert rows == ["| PF60 | The widget is round. | shape |", "| PF61 | The widget is blue. | because |"], rows


@pytest.mark.parametrize("line, step_reads, grader_reads", [
    ("unit.md sig 2026-11-15 id tmpl", ["sig"], "sig"),
    ("unit.md  sig 2026-11-15 id tmpl", ["sig"], ""),
    ("unit.md\tsig 2026-11-15 id tmpl", ["sig"], None),
    (" unit.md sig 2026-11-15 id tmpl", ["sig"], None),
], ids=["one-space", "two-spaces", "tab", "leading-space"])
def test_skill_edit_steps_graded_signature_splits_on_any_whitespace_where_grade_prose_splits_on_single_spaces(
        line, step_reads, grader_reads):
    """Not unified on purpose: skill_edit_step._signature reads a GRADED line with str.split(), grade_prose's
    graded_fields with split(" "), so a line grade_prose never writes (two spaces, a tab, a leading space) reads
    differently. Each keeps its own result until that is decided."""
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    grade_prose = importlib.import_module("veri.grade_prose")

    fields = grade_prose.graded_fields(line)
    by_grader = fields[1] if fields[0] == "unit.md" and len(fields) > 1 else None

    assert (skill_edit_step._signature(line.encode() + b"\n", "unit.md"), by_grader) == (step_reads, grader_reads)
    assert grade_prose.graded_line(fields) == line


def test_a_stray_path_present_when_an_author_attempt_would_run_exits_2_naming_it_launching_no_author_and_leaving_unit_list_and_graded_byte_identical_4058(tmp_path, skill_edit, run_cli):
    case = skill_edit(issue=(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A<next> | The widget is round. | shape |\n"),
        grade=(1, "A2: FAIL - not round\n"), guard=lambda unit, base, pins: [".tdd/issue-3481-body.md"])
    skill_edit_step, authors = case.step, case.launched
    unit = tmp_path / "unit.md"
    listed = tmp_path / "REQUIREMENTS.md"
    graded = tmp_path / "GRADED"
    graded.write_text("unit.md oldsig 2026-01-01 id prefix\n")
    before = {p: p.read_bytes() for p in (unit, listed, graded)}

    code, _, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, ".tdd/issue-3481-body.md" in err, authors) == (2, True, []), (code, err, len(authors))
    assert {p: p.read_bytes() for p in (unit, listed, graded)} == before


def test_the_issue_body_file_given_reported_changed_does_not_stop_the_step_whose_author_attempts_run_as_before_4058(tmp_path, skill_edit, run_cli):
    case = skill_edit(grade=(1, "A1: FAIL - no\n"), guard=lambda unit, base, pins: ["issue.md"])
    skill_edit_step, authors = case.step, case.launched

    code = run_cli(skill_edit_step, ["issue.md", "unit.md"], env={"VERI_SKILL_EDIT_BUDGET": "2"})[0]

    assert (code, len(authors)) == (1, 2), (code, len(authors))


def test_the_author_prompt_carries_the_untrusted_text_paragraph_of_leaf_safety_before_the_requirements_3959(tmp_path, monkeypatch, skill_edit):
    import re

    from conftest import SCRIPTS
    skill_edit_step = skill_edit(unit="The widget is painted a deep green.\n", issue=None, stubbed=False).step
    prompts = []

    def launch(name, prompt, *args, env=None):
        prompts.append(open(prompt).read())
        return types.SimpleNamespace(returncode=0)

    monkeypatch.setattr(skill_edit_step.leaf, "launch", launch)
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")

    def flat(text):
        return re.sub(r"\s+", " ", text).strip()

    paragraph = flat((SCRIPTS / "prompts" / "_leaf-safety.md").read_text().split("\n\n")[2])
    skill_edit_step._author("unit.md", str(tmp_path / "REQUIREMENTS.md"), "A1: FAIL - not blue\n")
    prompt = flat(prompts[0]) if len(prompts) == 1 else ""

    assert (paragraph.startswith("{{INCLUDE:"), -1 < prompt.find(paragraph) < prompt.find("A1: The widget is blue.")) \
        == (False, True), prompt


HEADED_UNIT = "# Title\n\nIntro.\n\n## Part A\n\nThe widget is painted a deep blue.\n\n## Part B\n\nOther.\n"


def _heading_unit_case(skill_edit, tmp_path, monkeypatch, fake_processes, grades, edit=None, author_rc=0, seen=None):
    """A step on the heading unit `unit.md#Part A`: the list holds A1 under it, the issue adds A2. `grades` are the
    grader's exit codes in order; `edit` is what the author writes over unit.md."""
    leaf = importlib.import_module("veri.leaf")
    graded = []
    launched = []

    def grade(path, unit):
        graded.append(unit)
        (tmp_path / "GRADED").write_text("sig\n")
        return grades[len(graded) - 1], ""

    def launch(name, prompt, *args, env=None):
        launched.append(name)
        if seen is not None:
            seen.append((tmp_path / "unit.md").read_text())
        (tmp_path / "unit.md").write_text(edit)
        return subprocess.CompletedProcess([name], author_rc, b"", None)

    skill_edit_step = skill_edit(unit=HEADED_UNIT, listing=(
        "## unit.md#Part A\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"),
        issue=("## Problem\n\nText.\n\n## Requirements\n\n### unit.md#Part A\n\n"
               "| ID | Requirement | Why |\n|---|---|---|\n| A2 | The widget is deep. | depth |\n"),
        grade=grade, author=None, run=None).step
    skill_edit_guard = skill_edit_step.skill_edit_guard
    monkeypatch.setattr(skill_edit_guard, "_git_ok", lambda *a: True)
    monkeypatch.setattr(skill_edit_guard, "_git_lines", lambda *a: ["unit.md", "REQUIREMENTS.md", "GRADED"]
                        if a[0] == "diff" else [])
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(leaf, "launch", launch)
    fake = fake_processes.answers({"": lambda line, **kw: (0, "abc1234\n", "")})
    return skill_edit_step, fake, graded, launched


def test_a_step_on_a_heading_unit_applies_its_rows_under_its_heading_in_the_list_beside_its_file_and_creates_no_file_of_its_name_4210(tmp_path, monkeypatch, run_cli, fake_processes, skill_edit):
    skill_edit_step, fake, graded, launched = _heading_unit_case(skill_edit, tmp_path, monkeypatch, fake_processes, [0])

    code, out, err = run_cli(skill_edit_step, ["issue.md", "unit.md#Part A"])

    requirements = importlib.import_module("veri.requirements")
    ids = [r.split("\t")[0] for r in requirements.claims(str(tmp_path / "REQUIREMENTS.md"), "unit.md#Part A").splitlines()]
    commits = [a for a in fake.argvs if a[:2] == ["git", "commit"]]
    assert (code, ids, graded, launched) == (3, ["A1", "A2"], ["unit.md#Part A"], []), (code, out, err)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["GRADED", "REQUIREMENTS.md", "issue.md", "unit.md"]
    assert len(commits) == 1 and "unit.md#Part A" not in commits[0], commits


def test_a_step_on_a_heading_unit_whose_author_edits_its_file_commits_the_file_not_a_path_of_the_units_name_4210(tmp_path, monkeypatch, run_cli, fake_processes, skill_edit):
    edited = HEADED_UNIT.replace("deep blue.", "deep, deep blue.")
    skill_edit_step, fake, graded, launched = _heading_unit_case(skill_edit, tmp_path, monkeypatch, fake_processes, [1, 0], edited)

    code, out, err = run_cli(skill_edit_step, ["issue.md", "unit.md#Part A"], env={"VERI_SKILL_EDIT_BUDGET": "1"})

    adds = [a for a in fake.argvs if a[:2] == ["git", "add"]]
    assert (code, launched, (tmp_path / "unit.md").read_text()) == (0, ["author-skill-edit-1"], edited), (code, out, err)
    assert len(adds) == 1 and "unit.md" in adds[0] and "unit.md#Part A" not in adds[0], adds


def test_an_added_step_on_a_heading_unit_graded_pass_with_a_stale_graded_line_refreshes_the_signature_and_exits_3_4210(tmp_path, monkeypatch, skill_edit, run_cli):
    grade_prose = importlib.import_module("veri.grade_prose")
    unit = "unit.md#Part A"

    def grade(path, unit):
        grade_prose.record_graded(unit, grade_prose.signature(path, unit, units=[unit]), "g2")
        return 0, ""

    case = skill_edit(unit=HEADED_UNIT, listing=(
        "## unit.md#Part A\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"),
        grade=grade, author=1)
    skill_edit_step, commands = case.step, case.commands
    monkeypatch.setattr(grade_prose, "grader_conf", lambda: {"model": "m"})
    grade_prose.record_graded(unit, grade_prose.signature("REQUIREMENTS.md", unit, units=[unit]), "g1")
    (tmp_path / "unit.md").write_text(HEADED_UNIT.replace("deep blue.", "deep, deep blue."))
    stale = (tmp_path / "GRADED").read_text()

    code, out, err = run_cli(skill_edit_step, ["--added", "refresh part A", "issue.md", unit])

    commits = [c for c in commands if c[:2] == ["git", "commit"]]
    assert (code, len(commits)) == (3, 1), (code, out, err)
    assert (tmp_path / "GRADED").read_text() != stale


def test_a_heading_unit_whose_author_attempts_are_rejected_starts_each_from_its_file_as_it_was_and_leaves_it_so_4210(tmp_path, monkeypatch, run_cli, fake_processes, skill_edit):
    edited = HEADED_UNIT.replace("deep blue.", "pale green.")
    seen = []
    skill_edit_step, fake, graded, launched = _heading_unit_case(skill_edit, tmp_path, monkeypatch, fake_processes, [1, 1, 1], edited,
                                                                 seen=seen)

    code, out, err = run_cli(skill_edit_step, ["issue.md", "unit.md#Part A"], env={"VERI_SKILL_EDIT_BUDGET": "2"})

    assert (code, seen, (tmp_path / "unit.md").read_text()) == (1, [HEADED_UNIT, HEADED_UNIT], HEADED_UNIT), (code, out, err)


def test_a_heading_unit_whose_author_leaf_fails_after_editing_its_file_restores_the_file_and_exits_2_4210(tmp_path, monkeypatch, run_cli, fake_processes, skill_edit):
    edited = HEADED_UNIT.replace("deep blue.", "pale green.")
    skill_edit_step, fake, graded, launched = _heading_unit_case(skill_edit, tmp_path, monkeypatch, fake_processes, [1], edited,
                                                                 author_rc=1)

    code, out, err = run_cli(skill_edit_step, ["issue.md", "unit.md#Part A"], env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert (code, launched, (tmp_path / "unit.md").read_text()) == (2, ["author-skill-edit-1"], HEADED_UNIT), (code, out, err)


def test_a_change_step_on_a_heading_unit_whose_author_edits_its_file_counts_the_prose_as_changed_and_exits_0_4210(tmp_path, monkeypatch, run_cli, fake_processes, skill_edit):
    edited = HEADED_UNIT.replace("deep blue.", "deep, deep blue.")
    skill_edit_step, fake, graded, launched = _heading_unit_case(skill_edit, tmp_path, monkeypatch, fake_processes, [0, 0], edited)

    code, out, err = run_cli(skill_edit_step, ["--change", "say deep twice", "issue.md", "unit.md#Part A"],
                             env={"VERI_SKILL_EDIT_BUDGET": "1"})

    assert (code, launched, (tmp_path / "unit.md").read_text()) == (0, ["author-skill-edit-1"], edited), (code, out, err)


def test_a_step_whose_issue_row_is_a_letter_suffixed_id_reword_of_a_held_row_is_not_refused_as_a_malformed_id_4541(tmp_path, skill_edit, run_cli):
    case = skill_edit(listing=(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| QU6b | The widget is red. | because |\n"),
        issue=("## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
               "| ID | Requirement | Why |\n|---|---|---|\n| QU6b<reword> | The widget is blue. | because |\n"),
        grade=[(1, "QU6b: FAIL - not blue\n"), (0, "")], guard=lambda unit, base, pins: [])
    skill_edit_step, authors = case.step, case.launched

    code, out, err = run_cli(skill_edit_step, ["--added", "reword QU6b", str(tmp_path / "issue.md"), "unit.md"])

    assert code == 0, (code, out, err)
    assert "QU6b" not in err, (code, out, err)
    assert len(authors) == 1, (code, out, err, authors)


def test_a_row_whose_text_the_unit_holds_under_another_id_though_its_own_id_holds_other_text_is_not_refused_and_leaves_the_list_byte_identical_4588(tmp_path, skill_edit, run_cli):
    head = "| ID | Requirement | Why |\n|---|---|---|\n"
    listing = "## unit.md\n\n" + head + "| A10 | The widget is round. | shape |\n| A12 | The widget is blue. | because |\n"
    skill_edit_step = skill_edit(unit="The widget is painted a deep blue and is round.\n", listing=listing, issue=(
        "## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n" + head + "| A10 | The widget is blue. | because |\n"),
        grade=(0, "")).step

    code, out, err = run_cli(skill_edit_step, [str(tmp_path / "issue.md"), "unit.md"])

    assert (code, (tmp_path / "REQUIREMENTS.md").read_text()) == (3, listing), (code, out, err)


def test_a_change_step_whose_author_drops_a_requirements_row_and_leaves_the_prose_byte_identical_grades_the_attempt_and_commits_after_one_author_4689(tmp_path, monkeypatch, skill_edit, run_cli):
    commits = []
    authors = []

    def launch(name, prompt, *args, env=None):
        authors.append(name)
        (tmp_path / "REQUIREMENTS.md").write_text(
            "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
        return subprocess.CompletedProcess([name], 0, b"", None)

    def run(cmd, **kw):
        if cmd[:2] == ["git", "commit"]:
            commits.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    skill_edit_step = skill_edit(listing=(
        "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n| A2 | The widget is blue. | duplicate |\n"),
        grade=(0, ""), author=None, run=run, guard=lambda unit, base, pins: []).step
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(importlib.import_module("veri.leaf"), "launch", launch)

    code, out, err = run_cli(skill_edit_step, ["--change", "drop row A2 as a duplicate of A1",
                                               "issue.md", "unit.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "3"})

    assert (code, len(authors), len(commits)) == (0, 1, 1), (code, out, err, authors, commits)


def test_a_change_step_whose_author_rewrites_requirements_rows_and_is_graded_fail_starts_its_next_attempt_on_the_rows_it_began_with_and_exits_1_4689(tmp_path, monkeypatch, skill_edit, run_cli):
    rows = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
            "| A1 | The widget is blue. | because |\n| A2 | The widget is round. | shape |\n")
    commits = []
    seen = []

    def launch(name, prompt, *args, env=None):
        seen.append((tmp_path / "REQUIREMENTS.md").read_text())
        (tmp_path / "REQUIREMENTS.md").write_text(
            "## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
        return subprocess.CompletedProcess([name], 0, b"", None)

    def run(cmd, **kw):
        if cmd[:2] == ["git", "commit"]:
            commits.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "abc1234\n", "")

    skill_edit_step = skill_edit(listing=rows, grade=(1, "FAIL: rows\n"), author=None, run=run,
                                 guard=lambda unit, base, pins: []).step
    monkeypatch.setattr(skill_edit_step.grade_prose, "modern_python_dir", lambda: "")
    monkeypatch.setattr(importlib.import_module("veri.leaf"), "launch", launch)

    code, out, err = run_cli(skill_edit_step, ["--change", "drop row A2", "issue.md", "unit.md"],
                             env={"VERI_SKILL_EDIT_BUDGET": "2"})

    assert (code, seen, (tmp_path / "REQUIREMENTS.md").read_text(), commits) == (1, [rows, rows], rows, []), (code, out, err)
