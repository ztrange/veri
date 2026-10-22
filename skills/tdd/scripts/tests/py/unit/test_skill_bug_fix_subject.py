"""Cases for what skills/tdd/SKILL.md tells the conductor to write on the subject line of a bug run's commits and PR."""
import importlib
import pathlib
import re

from skill_sections import plain_lines as plain, window_text as window

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

PR = "### 4. Draft PR"


def _lines(heading):
    section = importlib.import_module("skill_sections").section(SKILL, heading)
    lines = section.splitlines()[1:]
    for i, line in enumerate(lines):
        if line.startswith("#"):
            return lines[:i]
    return lines


def probe_fix_line(heading, unestablished, absent, unqualified):
    text = plain(_lines(heading))
    if not text.strip():
        return f"SKILL.md has no '{heading}' section to read — {unestablished}"
    if "fix:" not in text:
        return absent
    if "bug" not in window(text, "fix:"):
        return unqualified
    return None


def test_skill_md_gives_a_bug_steps_green_commit_a_fix_subject_and_a_bug_runs_pr_title_a_fix_prefix():
    problems = [
        probe_fix_line(
            PR,
            "what prefix a bug run's PR title takes could not be established",
            f"SKILL.md's '{PR}' section never names the fix: prefix, so a bug run opens a PR whose title announces a capability the run did not add",
            f"SKILL.md's '{PR}' section names the fix: prefix without saying it is a bug run's, so the conductor cannot tell which runs title their PR that way",
        ),
    ]
    assert [p for p in problems if p] == []
