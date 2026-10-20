"""What skills/tdd/SKILL.md says about asking whether a run can still afford to finish, read as text."""
import pathlib
import re

import skill_sections
from skill_sections import plain_lower as plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

CYCLE_LOOP = "### 3. The cycle loop"


def loop_lines():
    return skill_sections.section(SKILL, CYCLE_LOOP).splitlines()[1:]


def call_at(loop):
    return next((i + 1 for i, line in enumerate(loop) if "$S/run-affordable.sh" in line), None)


def at_the_call(check):
    loop = loop_lines()
    at = call_at(loop)
    if at is None:
        return ["the cycle loop has no $S/run-affordable.sh call"]
    return check(loop, at)


def test_skill_md_calls_run_affordable_sh_at_the_step_boundary_after_the_step_s_ledger_commit_with_the_count_next_unchecked_sh_implies_and_parks_on_exit_1_carrying_spent_steps_remaining_the_median_the_projection_the_ceiling_and_the_two_answers():
    def check(loop, at):
        problems = []
        commit_at = next((i + 1 for i, line in enumerate(loop) if 'git commit -m "chore: refactor verified' in line), None)
        if commit_at is None:
            problems.append("the cycle loop has no 'chore: refactor verified' ledger commit to call it after")
        elif at < commit_at:
            problems.append(f"$S/run-affordable.sh is called at line {at} of the cycle loop, before the step's ledger commit at line {commit_at}")
        start = at - 5 if at > 5 else 1
        around = plain("\n".join(loop[start - 1:]))
        for probe in ["next-unchecked.sh", "exit 1", "park", "spent", "steps remaining", "median",
                      "projection", "ceiling", "veri_run_budget", "resume", "split",
                      "⟦full-suite⟧", "⟦human-owed⟧"]:
            if probe not in around:
                problems.append(f"the text around the $S/run-affordable.sh call never says '{probe}'")
        return problems

    problems = at_the_call(check)
    assert not problems, "\n".join(problems)


def test_skill_md_says_what_the_step_boundary_does_when_run_affordable_sh_exits_3_no_full_step_done_yet_carry_on_or_exits_2_no_answer_could_be_obtained():
    def check(loop, at):
        kept = []
        for line in loop[at - 1:]:
            if re.match(r"\s*- \*\*REJECT", line):
                break
            kept.append(line)
        boundary = plain("\n".join(kept))
        return [f"the step boundary after the $S/run-affordable.sh call never says '{probe}'"
                for probe in ["exit 3", "no full step", "exit 2", "no answer"] if probe not in boundary]

    problems = at_the_call(check)
    assert not problems, "\n".join(problems)


def test_skill_md_says_an_affordability_park_on_run_affordable_sh_exit_1_is_not_a_bail_and_that_classify_bail_sh_is_not_called_on_it():
    def check(loop, at):
        park, inside = [], False
        for line in plain("\n".join(loop[at - 1:])).splitlines():
            if "on exit 1" in line:
                inside = True
            if "on exit 2" in line:
                break
            if inside:
                park.append(line)
        text = "\n".join(park)
        if not park:
            return ["the step boundary after the $S/run-affordable.sh call has no exit 1 answer"]
        return [f"the exit 1 park after the $S/run-affordable.sh call never says '{probe}'"
                for probe in ["not a bail", "classify-bail.sh"] if probe not in text]

    problems = at_the_call(check)
    assert not problems, "\n".join(problems)
