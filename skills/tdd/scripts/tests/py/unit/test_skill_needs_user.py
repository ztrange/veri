"""Cases for what skills/tdd/SKILL.md tells a conductor that would ask the user a question, read as text."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"


def test_issue_2147_skill_marks_the_pr_ready_by_running_pr_ready_sh_never_sourcing_a_bash_library():
    sourcing = [line for line in SKILL.read_text().splitlines() if re.search(r"\. \$S/lib/github\.sh", line)]
    assert not sourcing, f"SKILL.md sources the bash GitHub library into the conductor's shell: {sourcing}"
