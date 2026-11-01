"""Script-path cases for skills/vmerge/SKILL.md."""
import re

from conftest import ROOT

SKILL_DIR = ROOT / "skills" / "vmerge"


def test_1836_every_script_path_in_veri_merge_skill_resolves_to_an_existing_file():
    text = (SKILL_DIR / "SKILL.md").read_text()
    s_dir = re.search(r"`\$S` is `[^`]*`, reached from this skill's base directory as `([^`]+)`", text)
    assert s_dir, "SKILL.md does not define $S relative to its base directory"
    base = SKILL_DIR / s_dir.group(1)

    paths = [base / p for p in re.findall(r"\$S/([\w./-]+\.sh)", text)]
    paths += [SKILL_DIR / p for p in re.findall(r"(?<![\w$/.])(\.{1,2}/[\w./-]+\.sh)", text)]

    assert paths, "SKILL.md names no script path"
    missing = sorted(str(p) for p in paths if not p.resolve().is_file())
    assert missing == [], "script paths that do not resolve: " + ", ".join(missing)
