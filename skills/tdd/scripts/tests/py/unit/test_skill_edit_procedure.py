"""Cases for the procedure skills/tdd/SKILL-EDIT.md holds for a ⟦skill-edit⟧ step."""
import pathlib
import re

DOC = pathlib.Path(__file__).resolve().parents[4] / "SKILL-EDIT.md"


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
