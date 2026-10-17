"""Cases for how skills/tdd/SKILL.md has the conductor run its own long commands: through detach-command.sh, never backgrounded with the turn ended."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[3] / "SKILL.md"


def lines_of(text):
    return text.splitlines()


def undetached(text):
    return [
        f"SKILL.md:{n}: {line}"
        for n, line in enumerate(lines_of(text), 1)
        if (re.search(r"detect-test-command\.sh --tier (fast|all)", line)
            or (re.search(r"[Rr]un", line) and "make test" in line))
        and not re.search(r"detach-command\.sh", line)
    ]


def any_line(text, *patterns):
    return any(all(re.search(p, line) for p in patterns) for line in lines_of(text))


def test_skill_md_runs_make_test_and_the_detected_test_command_only_through_detach_command_sh():
    planted = "Run `make test` once.\nRun it through `detach-command.sh start full make test`.\n"
    assert undetached(planted) == ["SKILL.md:1: Run `make test` once."]
    assert undetached(SKILL.read_text()) == []


def test_skill_md_says_no_step_backgrounds_a_command_and_ends_its_turn():
    pattern = (r"[Nn]o step", r"background", r"end(s)? (its|the|their)? ?turn")
    planted = "Never launch a leaf in a background Bash call and then wait for its notification.\n"
    assert not any_line(planted, *pattern)
    assert any_line(SKILL.read_text(), *pattern), (
        "SKILL.md: no line says that no step backgrounds a command and ends its turn")


def test_skill_md_says_the_conductor_never_ends_its_turn_while_a_subagent_background_command_or_background_task_it_started_is_running():
    pattern = (r"[Nn]ever end(s)? (its|the) turn", r"subagent", r"background (command|task)", r"pairs table")
    planted = ("The conductor may end its turn while a subagent, a background command or a background task "
               "is running; the pairs table is built inline.\n")
    assert not any_line(planted, *pattern)
    assert any_line(SKILL.read_text(), *pattern), (
        "SKILL.md: no line says the conductor never ends its turn while a background command, subagent "
        "or background task it started is running, pairs table included")


def test_skill_md_says_what_detach_command_sh_wait_answers_0_passed_1_red_2_died_3_still_running():
    pattern = (r"detach-command\.sh wait", r"pass", r"red", r"died", r"still running")
    planted = "Run `detach-command.sh wait <name> 500`, calling it again each time it returns 3.\n"
    assert not any_line(planted, *pattern)
    assert any_line(SKILL.read_text(), *pattern), (
        "SKILL.md: no line reads detach-command.sh wait's exit codes (0 passed, 1 red, 2 died, 3 still running)")
