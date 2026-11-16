"""Mechanical cases for skills/voutage/: an operator skill read by path, never linked (#4156)."""
from conftest import ROOT

from veri import install_links

SKILL_DIR = ROOT / "skills" / "voutage"


def test_voutage_skill_md_exists_and_voutage_is_not_in_linked_4156():
    assert ((SKILL_DIR / "SKILL.md").is_file(), "voutage" in install_links.LINKED) == (True, False)
