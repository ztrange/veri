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


def test_skills_tdd_exists_and_its_skill_md_frontmatter_name_is_still_tdd():
    md = ROOT / "skills" / "tdd" / "SKILL.md"
    found = re.search(r"^name:\s*(\S+)\s*$", md.read_text(), re.M) if md.is_file() else None

    assert found is not None and found.group(1) == "tdd", found and found.group(1)


@pytest.mark.tree_audit("the eleven renamed units' SKILL.md, REQUIREMENTS.md and GRADED files")
def test_each_of_the_11_renamed_units_with_a_requirements_list_has_a_graded_line_under_its_new_path_signed_from_its_current_text_and_rows(
        monkeypatch):
    import importlib

    grade_prose = importlib.import_module("veri.grade_prose")
    monkeypatch.chdir(ROOT)
    stale = []
    for name in NAMES:
        if name == "judge":
            continue
        unit = f"skills/v{name}/SKILL.md"
        graded = ROOT / "skills" / f"v{name}" / "GRADED"
        lines = [l.split(" ") for l in graded.read_text().splitlines()] if graded.is_file() else []
        found = [f[1] for f in lines if f[0] == unit and len(f) > 1]
        want = grade_prose.signature(f"skills/v{name}/REQUIREMENTS.md", unit)
        if found != [want]:
            stale.append((unit, found, want[:12]))

    assert stale == [], stale
