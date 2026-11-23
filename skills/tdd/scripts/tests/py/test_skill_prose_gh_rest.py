import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[5]
GRAPHQL_PORCELAIN = re.compile(r"`gh (?:issue (?:list|view|create)|pr (?:view|diff|merge|list))\b[^`]*`")
FORBIDS = re.compile(r"\bnever\b", re.IGNORECASE)


def _instructions(text):
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        for found in GRAPHQL_PORCELAIN.finditer(line):
            before = line[:found.start()]
            if number > 1 and not line.lstrip().startswith(("-", "*", "#")) and not FORBIDS.search(before):
                before += " " + lines[number - 2].rstrip()[-6:]
            if not FORBIDS.search(before):
                yield number, found.group(0)


@pytest.mark.tree_audit("skills/*/SKILL.md")
def test_issue_4666_no_skill_instruction_names_a_graphql_gh_porcelain_command():
    offenders = [f"{path.relative_to(ROOT)}:{number}: {command}"
                 for path in sorted((ROOT / "skills").glob("*/SKILL.md"))
                 for number, command in _instructions(path.read_text())]
    assert offenders == []
