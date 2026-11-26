"""Mechanical cases for skills/voutage/: an operator skill read by path, never linked (#4156)."""
import re

from veri import install_links

from conftest import ROOT

SKILL_DIR = ROOT / "skills" / "voutage"


def test_voutage_skill_md_exists_and_voutage_is_not_in_linked_4156():
    assert ((SKILL_DIR / "SKILL.md").is_file(), "voutage" in install_links.LINKED) == (True, False)


def test_every_script_path_in_voutage_skill_resolves_to_an_existing_file_4156():
    text = (SKILL_DIR / "SKILL.md").read_text()
    s_dir = re.search(r"`\$S` is `[^`]*`, reached from this skill's base directory as `([^`]+)`", text)
    assert s_dir, "SKILL.md does not define $S relative to its base directory"
    base = SKILL_DIR / s_dir.group(1)

    paths = [base / p for p in re.findall(r"\$S/([\w./-]+\.sh)", text)]
    paths += [SKILL_DIR / p for p in re.findall(r"(?<![\w$/.])(\.{1,2}/[\w./-]+\.sh)", text)]

    assert paths, "SKILL.md names no script path"
    missing = sorted(str(p) for p in paths if not p.resolve().is_file())
    assert missing == [], "script paths that do not resolve: " + ", ".join(missing)
