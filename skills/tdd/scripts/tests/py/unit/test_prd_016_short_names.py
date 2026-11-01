"""PRD 016: every veri skill lives under its short name."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[6]
NAMES = ["bail", "coord", "dev", "file", "groom", "handoff", "judge", "merge", "plan", "report", "status", "stop"]


@pytest.mark.tree_audit("the twelve skill directories under skills/")
def test_each_of_the_12_skills_lives_in_skills_v_name_with_frontmatter_name_v_name_and_no_veri_dir_remains():
    skills = ROOT / "skills"
    wrong = []
    for name in NAMES:
        md = skills / f"v{name}" / "SKILL.md"
        found = re.search(r"^name:\s*(\S+)\s*$", md.read_text(), re.M) if md.is_file() else None
        if not found or found.group(1) != f"v{name}":
            wrong.append(f"v{name}: {found.group(1) if found else 'no SKILL.md'}")
    leftover = sorted(d.name for d in skills.iterdir() if d.is_dir() and d.name.startswith("veri-"))

    assert wrong == [] and leftover == [], (wrong, leftover)
