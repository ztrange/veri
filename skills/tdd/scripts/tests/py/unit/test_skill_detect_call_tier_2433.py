"""Case for the detect-test-command.sh call in skills/tdd/SKILL.md's Detecting the test command naming its tier."""
import pathlib
import re

import skill_sections

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def test_2433_detecting_the_test_command_call_names_tier_fast():
    detecting = skill_sections.section(SKILL, "## Detecting the test command")
    call = next((line for line in detecting.splitlines() if re.search(r"detect-test-command\.sh\b.*--issue", line)), None)
    assert call is not None, "'Detecting the test command' has no detect-test-command.sh --issue call line"
    assert "--tier fast" in call, f"the detect-test-command.sh call does not name --tier fast: {call!r}"
