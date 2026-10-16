"""Cases for the step a verifier launch in skills/tdd/SKILL.md carries and the unreplaced-cases guard before verify-green."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[3] / "SKILL.md"

RED = "#### Red — one failing test (developer leaf), then verify-red (blind)"
BAILING = "## Bailing"

FLAG = '--step "<STEP>"'
FAST_FLAG = "--fast-cmd '<fast-cmd>'"
CALL_RE = rf"verify\.sh {FLAG}( {FAST_FLAG})? (red|green|refactor|pin|<phase>)"
GREEN_RE = rf"verify\.sh {FLAG}( {FAST_FLAG})? (green|<phase>) "
MENTION = "unreplaced-cases.sh"


def plain_join(text):
    return " ".join(text.replace("*", "").replace("`", "").lower().splitlines()) + " "


def verify_calls():
    return [
        (n, line) for n, line in enumerate(SKILL.read_text().splitlines(), 1)
        if re.search(r"verify\.sh.*(<spec-file>|\.tdd/issue-<n>-spec\.md)", line)
        and "<red|green|refactor|pin|plan>" not in line
    ]


def section(heading):
    return importlib.import_module("skill_sections").section(SKILL, heading)


def guard(text):
    out, on = [], False
    for line in text.splitlines():
        if MENTION in line:
            on = True
        if on and re.match(r" *```", line):
            break
        if on:
            out.append(line)
    return plain_join("\n".join(out))


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


def test_1521_skill_md_has_the_conductor_run_unreplaced_cases_sh_before_verify_green_and_bail_unreplaced_cases_on_exit_1():
    text = plain_join(section(RED))
    assert MENTION in text, "skills/tdd/SKILL.md never mentions unreplaced-cases.sh"
    text = text.split(MENTION, 1)[1][:1200]
    for pattern, message in [
        ("replaces-case", "never says it applies to a ⟦replaces-case⟧ step"),
        (r"exit 1|exits 1|exit \*\*1", "never branches on exit 1"),
        (r"cause=unreplaced-cases|cause `unreplaced-cases`", "never bails with cause unreplaced-cases"),
        (r"(without|never|not|before)[^.]{0,80}verify-green|verify-green[^.]{0,80}(not|never|without)",
         "never keeps verify-green from launching"),
    ]:
        assert re.search(pattern, text), f"skills/tdd/SKILL.md's unreplaced-cases.sh guard {message}"


def test_1521_skill_md_lists_unreplaced_cases_among_the_bail_causes_and_says_what_exit_2_of_unreplaced_cases_sh_does():
    assert re.search(r"- unreplaced-cases —", plain_join(section(BAILING))), (
        "skills/tdd/SKILL.md's bail causes never list `unreplaced-cases`")
    assert re.search(r"exits? 2[^.]*(bail|stop|retr|launch)", guard(section(RED))), (
        "skills/tdd/SKILL.md's unreplaced-cases.sh guard never says what the conductor does on exit 2")


def test_1521_skill_md_has_the_unreplaced_cases_sh_guard_read_the_current_attempt_s_red_report_tdd_revise_red_k_out_after_a_red_revise():
    text = guard(section(RED))
    assert ".tdd/revise-red-<k>.out" in text, (
        "skills/tdd/SKILL.md's unreplaced-cases.sh guard names .tdd/develop-red.out alone, never .tdd/revise-red-<k>.out after a red revise")
    assert ".tdd/develop-red.out" in text, "skills/tdd/SKILL.md's unreplaced-cases.sh guard never names .tdd/develop-red.out"


def test_1625_skill_md_has_unreplaced_cases_sh_exit_2_bail_at_once_launching_no_correction_leaf_and_no_verifier():
    text = guard(section(RED))
    sentence = re.search(r"exits? 2[^.]*\.", text.split("exit 1 again", 1)[1])
    assert sentence, "skills/tdd/SKILL.md's unreplaced-cases.sh guard never says what the conductor does on exit 2 after the correction paragraph"
    sentence = sentence.group(0)
    for pattern, message in [
        (r"cause=unreplaced-cases", "never bails with cause=unreplaced-cases on exit 2"),
        (r"at once|immediately", "never says exit 2 bails at once"),
        (r"(launch|launching|launches)[^.]{0,40}no (correction )?leaf|no (correction )?leaf", "never says exit 2 launches no correction leaf"),
        (r"(launch|launching|launches)[^.]{0,60}no[^.]{0,40}verifier|no verifier", "never says exit 2 launches no verifier"),
    ]:
        assert re.search(pattern, sentence), f"skills/tdd/SKILL.md's unreplaced-cases.sh exit 2 sentence {message}: {sentence!r}"
