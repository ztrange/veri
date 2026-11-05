"""Sibling-skill references in skills/*/SKILL.md name skills that exist (#3073)."""
import re

import pytest

from conftest import ROOT

REF = re.compile(r"<(?:resolved )?base dir>/\.\./([^/\s`<>]+|<[^>]*>)")


@pytest.mark.tree_audit("reads every skills/*/SKILL.md")
def test_every_base_dir_sibling_reference_names_an_existing_skill_3073():
    skills = ROOT / "skills"
    missing = []
    for doc in sorted(skills.glob("*/SKILL.md")):
        for name in REF.findall(doc.read_text()):
            if name.startswith("<"):
                continue
            if not (skills / name).is_dir():
                missing.append(f"{doc.relative_to(ROOT)}: {name}")

    assert missing == []


@pytest.mark.tree_audit("reads every skills/*/SKILL.md")
def test_every_file_with_a_sibling_reference_tells_the_agent_to_resolve_the_symlink_3073():
    unresolved = []
    for doc in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = doc.read_text()
        if REF.search(text) and "cd -P" not in text and "realpath" not in text:
            unresolved.append(str(doc.relative_to(ROOT)))

    assert unresolved == []
