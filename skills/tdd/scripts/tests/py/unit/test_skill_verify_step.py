"""Cases for the step a verifier launch in skills/tdd/SKILL.md carries and the unreplaced-cases guard before verify-green."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

BAILING = "## Bailing"
BAIL = SKILL.with_name("BAIL.md")
RESUME_MD = SKILL.with_name("RESUME.md")

FLAG = '--step "<STEP>"'
FAST_FLAG = "--fast-cmd '<fast-cmd>'"
CALL_RE = rf"verify\.sh {FLAG}( {FAST_FLAG})? (red|green|refactor|pin|<phase>)"
GREEN_RE = rf"verify\.sh {FLAG}( {FAST_FLAG})? (green|<phase>) "


def plain_join(text):
    return " ".join(text.replace("*", "").replace("`", "").lower().splitlines()) + " "


def verify_calls():
    return [
        (n, line) for path in (SKILL, RESUME_MD) for n, line in enumerate(path.read_text().splitlines(), 1)
        if re.search(r"verify\.sh.*(<spec-file>|\.tdd/issue-<n>-spec\.md)", line)
        and "<red|green|refactor|pin|plan>" not in line
    ]


def section(heading, name=None):
    path = SKILL.with_name(name) if name else BAIL if heading == BAILING else SKILL
    return importlib.import_module("skill_sections").section(path, heading)


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
        if re.search(GREEN_RE, line) and f"verify.sh {FLAG} {FAST_FLAG} " not in line
    ]
    assert not problems, "\n".join(problems)


def test_1521_skill_md_lists_unreplaced_cases_among_the_bail_causes():
    assert re.search(r"- unreplaced-cases —", plain_join(section(BAILING))), (
        "skills/tdd/SKILL.md's bail causes never list `unreplaced-cases`")
