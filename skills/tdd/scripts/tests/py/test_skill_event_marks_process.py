"""Cases for the conductor's marks in the run's event log, as skills/tdd/SKILL.md prescribes them, read as text.

Contract under test:
  SKILL.md prescribes an `event.sh <mark>` call in the same instruction as the issue comment
  that mark mirrors; the refactor mark carries transforms, budget, stopped and pass, with the
  count observed and unclamped; every `add-ledger-step.sh` insertion has a `step-added` call
  beside it; and the exhausted-budget split and the needs-user park each leave a mark.
"""
import importlib
import pathlib
import subprocess

import pytest

SKILL = pathlib.Path(__file__).resolve().parents[3] / "SKILL.md"


@pytest.mark.process("SKILL.md's own event.sh refactor line runs under bash -c, its $(next-pending-refactor.sh) and event.sh shim starting real processes")
def test_a_run_whose_skill_md_refactor_mark_is_present_renders_real_refactor_and_stopped_cells_for_that_step_and_unknown_for_a_step_without_one(tmp_path, run_cli):
    scripts = SKILL.parent / "scripts"
    call = next((line.strip() for line in SKILL.read_text().splitlines() if "event.sh refactor " in line), None)
    assert call, "SKILL.md has no `event.sh refactor` call line to run — the report could not be checked"
    tidied = "the step whose refactor mark was written"
    untidied = "the step that wrote no refactor mark"
    for old, new in (("$S", str(scripts)), ("<n>", "230"), ("<STEP>", tidied), ("<count>", "7"),
                     ("<VERI_REFACTOR_BUDGET>", "5"), ("<reason>", "budget"),
                     ("\"$pass\"", "1")):  # the conductor's $pass: 1 on a step's first refactor pass (SKILL.md)
        call = call.replace(old, new)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-230.md").write_text(f"- [x] {tidied} ⟂ refactor pending\n- [ ] {untidied}\n")
    event = importlib.import_module("veri.event")
    for step in (tidied, untidied):
        code, out, err = run_cli(event, ["launch", "name=develop-refactor", "cmd=claude", "model=sonnet"], cwd=tmp_path, env={
            "VERI_ISSUE": "230", "VERI_ACTOR": "developer", "VERI_STEP": step, "VERI_PHASE": "refactor", "VERI_ATTEMPT": "1"})
        assert code == 0, f"event.sh could not write the fixture's launch line for step: {step}: {err}"
    ran = subprocess.run(["bash", "-c", call], cwd=tmp_path, capture_output=True, text=True)
    assert ran.returncode == 0, f"the call SKILL.md prescribes did not run: {call}: {ran.stderr}"
    code, report, err = run_cli(importlib.import_module("veri.metrics"), ["230"], cwd=tmp_path)
    assert code == 0, f"want metrics.sh to exit 0, it did not: {report}{err}"

    def cell_of(step, want):
        seen, col = False, 0
        for line in report.splitlines():
            if not line.startswith("|"):
                seen, col = False, 0
                continue
            cells = line.split("|")
            if not seen:
                seen = True
                for i in range(1, len(cells) - 1):
                    if cells[i].strip() == want:
                        col = i
                continue
            if col and cells[1].strip() == step:
                return cells[col].strip()
        return ""

    problems = []
    for step, heading, want in ((tidied, "refactor", "7/5"), (tidied, "stopped", "budget"),
                                (untidied, "refactor", "unknown"), (untidied, "stopped", "unknown")):
        got = cell_of(step, heading)
        if got != want:
            problems.append(f'step "{step}": want its {heading} cell to say `{want}`, it says `{got}`')
    assert not problems, "\n".join(problems) + f"\nthe report was: {report!r}"
