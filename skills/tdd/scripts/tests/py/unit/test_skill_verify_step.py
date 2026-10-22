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


def test_1625_skill_md_pin_path_says_the_unreplaced_cases_check_bails_only_on_a_second_exit_1_after_the_correction_leaf_or_on_exit_2():
    text = plain_join(section("## Already satisfied — the pin", "PIN.md"))
    sentence = re.search(r"the unreplaced-cases check[^.]*\.", text)
    assert sentence, "skills/tdd/SKILL.md's pin path never says what the unreplaced-cases check did in Red"
    sentence = sentence.group(0)
    assert not re.search(r"already bailed with cause=unreplaced-cases on exit 1\b(?! again)", sentence) or re.search(r"second|again|correction", sentence), (
        f"skills/tdd/SKILL.md's pin path still says the unreplaced-cases check bailed on exit 1 alone: {sentence!r}")
    for pattern, message in [
        (r"second exit 1|exit 1 again|again exit(s)? 1|exits? 1 a second time", "never says a second exit 1 is what bails"),
        (r"correction", "never names the one correction leaf"),
        (r"exit 2", "never says exit 2 bails"),
    ]:
        assert re.search(pattern, sentence), f"skills/tdd/SKILL.md's pin-path unreplaced-cases sentence {message}: {sentence!r}"
