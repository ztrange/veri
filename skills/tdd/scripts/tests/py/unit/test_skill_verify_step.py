"""Cases for the step a verifier launch in skills/tdd/SKILL.md carries and the unreplaced-cases guard before verify-green."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

RESUME_MD = SKILL.with_name("RESUME.md")

FLAG = '--step "<STEP>"'
FAST_FLAG = "--fast-cmd '<fast-cmd>'"
BASE_FLAG = "--branch-base <base>"  # the recorded branch base, ahead of every other flag (#4375)
STEP_GREEN = r'( --step-green "\$step_green")?'  # refactor's file bounds (#4544)
CALL_RE = rf"verify\.sh {BASE_FLAG}{STEP_GREEN} {FLAG}( {FAST_FLAG})? (red|green|refactor|pin|<phase>)"
GREEN_RE = rf"verify\.sh {BASE_FLAG} {FLAG}( {FAST_FLAG})? (green|<phase>) "


def verify_calls():
    return [
        (n, line) for path in (SKILL, RESUME_MD) for n, line in enumerate(path.read_text().splitlines(), 1)
        if re.search(r"verify\.sh.*(<spec-file>|\.tdd/issue-<n>-spec\.md)", line)
        and "<red|green|refactor|pin|plan>" not in line
    ]


def test_skill_md_passes_step_on_every_verify_sh_call_it_tells_the_conductor_to_run():
    calls = verify_calls()
    assert calls, "skills/tdd/SKILL.md has no verify.sh call naming a spec file — the calls this case is about could not be read"
    problems = [
        f"skills/tdd/SKILL.md:{n} does not pass {FLAG} before verify.sh's positionals: {line}"
        for n, line in calls if not re.search(CALL_RE, line)
    ]
    assert not problems, "\n".join(problems)


def test_skill_md_passes_fast_cmd_on_every_verify_sh_call_that_can_judge_green():
    problems = [
        f"skills/tdd/SKILL.md:{n} can judge green but does not pass {FAST_FLAG}: {line}"
        for n, line in verify_calls()
        if re.search(GREEN_RE, line) and f"verify.sh {BASE_FLAG} {FLAG} {FAST_FLAG} " not in line
    ]
    assert not problems, "\n".join(problems)


def test_structural_md_launches_the_transform_verifier_with_the_fast_tier_command():
    structural = SKILL.with_name("STRUCTURAL.md")
    launches = [(n, line) for n, line in enumerate(structural.read_text().splitlines(), 1)
                if re.search(r"\$S/supervise\.sh verdict-transform \$S/run-verdict\.sh ", line)]
    assert launches, "skills/tdd/STRUCTURAL.md has no verdict-transform launch into run-verdict.sh — the line this case is about could not be read"
    problems = [
        f"skills/tdd/STRUCTURAL.md:{n} launches the transform verifier without {FAST_FLAG} before `transform`: {line}"
        for n, line in launches if not re.search(rf"run-verdict\.sh .*{re.escape(FAST_FLAG)} transform ", line)
    ]
    assert not problems, "\n".join(problems)
