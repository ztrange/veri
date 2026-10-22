"""Cases for the procedure skills/tdd/SKILL-EDIT.md holds for a ⟦skill-edit⟧ step."""
import pathlib
import re

DOC = pathlib.Path(__file__).resolve().parents[4] / "SKILL-EDIT.md"
SKILL = DOC.with_name("SKILL.md")


def _sentences(text):
    return re.split(r"(?<=\.)\s", re.sub(r"\s+", " ", text.replace("`", "")))


def test_skill_edit_md_runs_skill_edit_step_ticks_on_exit_0_or_3_bails_on_1_and_handles_2_as_no_answer_1871():
    assert DOC.is_file(), "skills/tdd/SKILL-EDIT.md does not exist"
    sentences = _sentences(DOC.read_text(encoding="utf-8"))
    run = next((s for s in sentences if "skill-edit-step.sh" in s and "issue body" in s), "")
    assert run, "SKILL-EDIT.md never runs skill-edit-step.sh on the issue body"
    assert "unit" in run, "the run never names the step's unit"
    tick = next((s for s in sentences if "exit 0 or 3" in s and "tick" in s), "")
    assert tick, "SKILL-EDIT.md never ticks the step on exit 0 or 3"
    bail = next((s for s in sentences if "exit 1" in s and "bail" in s), "")
    assert bail, "SKILL-EDIT.md never bails on exit 1"
    assert "exhausted revise" in bail, "the exit 1 bail is never an exhausted revise"
    no_answer = next((s for s in sentences if "exit 2" in s and "no answer" in s), "")
    assert no_answer, "SKILL-EDIT.md never handles exit 2 as no answer"


def test_skill_edit_md_redoes_an_unfinished_skill_edit_step_from_its_start_with_its_budget_reset_1871():
    sentences = _sentences(DOC.read_text(encoding="utf-8"))
    resume = next((s for s in sentences if "resumed run" in s and "unfinished" in s), "")
    assert resume, "SKILL-EDIT.md never says what a resumed run does with an unfinished skill-edit step"
    assert "from its start" in resume, "the resumed run never redoes the step from its start"
    assert "budget" in resume and "reset" in resume, "the resumed run never resets the step's budget"


def test_skill_md_points_the_conductor_to_skill_edit_md_on_a_skill_edit_step_in_place_of_red_green_refactor_1871():
    sentences = _sentences(SKILL.read_text(encoding="utf-8"))
    pointer = next((s for s in sentences if "<base directory>/SKILL-EDIT.md" in s), "")
    assert pointer, "SKILL.md never points the conductor to <base directory>/SKILL-EDIT.md"
    assert "Read" in pointer, "the pointer never tells the conductor to Read SKILL-EDIT.md"
    assert "⟦skill-edit⟧" in pointer, "the pointer never names the skill-edit step it applies to"
    assert re.search(r"in place of[^.]*Red[^.]*Green[^.]*Refactor", pointer), \
        "the pointer never says SKILL-EDIT.md replaces Red, Green and Refactor"


def test_skill_edit_md_bails_at_once_on_exit_2_without_spending_stuck_retries_yet_retries_a_killed_author_inside_the_runner_2037():
    sentences = _sentences(DOC.read_text(encoding="utf-8"))
    bail = next((s for s in sentences if "exit 2" in s and "at once" in s), "")
    assert bail, "SKILL-EDIT.md never bails at once on exit 2"
    assert "bad argument" in bail, "the exit 2 bail never names a bad argument"
    assert "system failure" in bail and "no-verdict" in bail, \
        "the exit 2 bail is never a system failure with cause no-verdict"
    assert "never relaunch" in bail and "VERI_STUCK_RETRIES" in bail, \
        "the exit 2 bail never rules out a relaunch under VERI_STUCK_RETRIES"
    stuck = next((s for s in sentences if "killed" in s and "stuck" in s and "VERI_STUCK_RETRIES" in s
                  and "supervise.sh" in s and "retried" in s), "")
    assert stuck, "SKILL-EDIT.md never says a killed or stuck author is retried under VERI_STUCK_RETRIES by supervise.sh"


def test_skill_edit_md_names_the_issue_body_file_and_the_gh_api_command_that_writes_it_before_the_runner_2037():
    text = re.sub(r"\s+", " ", DOC.read_text(encoding="utf-8"))
    command = "gh api repos/{owner}/{repo}/issues/<n> -q .body > .tdd/issue-<n>-body"
    assert ".tdd/issue-<n>-body" in text, "SKILL-EDIT.md never names the file the issue body is read into"
    assert command in text, "SKILL-EDIT.md never says how the issue body file is produced"
    assert text.index(command) < text.index("skill-edit-step.sh"), \
        "the issue body file is never produced before skill-edit-step.sh runs"
    handed = next((s for s in _sentences(text) if "skill-edit-step.sh" in s and ".tdd/issue-<n>-body" in s), "")
    assert handed, "SKILL-EDIT.md never hands skill-edit-step.sh the issue body path"
