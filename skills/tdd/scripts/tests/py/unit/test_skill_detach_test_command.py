"""Cases for how skills/tdd/SKILL.md has the conductor run its own long commands: through detach-command.sh, never backgrounded with the turn ended."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
PREFLIGHT = SKILL.with_name("PREFLIGHT.md")


def lines_of(text):
    return text.splitlines()


def undetached(text):
    return [
        f"SKILL.md:{n}: {line}"
        for n, line in enumerate(lines_of(text), 1)
        if (re.search(r"detect-test-command\.sh --tier (fast|all)", line)
            or (re.search(r"[Rr]un", line) and "make test" in line))
        and not re.search(r"detach-command\.sh", line)
        and "make test TESTS=" not in line
    ]


def test_skill_md_runs_make_test_and_the_detected_test_command_only_through_detach_command_sh():
    planted = "Run `make test` once.\nRun it through `detach-command.sh start full make test`.\n"
    assert undetached(planted) == ["SKILL.md:1: Run `make test` once."]
    assert undetached("Run `make test TESTS=\"<file>\"` alone.\n") == []
    assert undetached(SKILL.read_text() + PREFLIGHT.read_text()) == []
