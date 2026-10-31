"""PRD 015: skills/veri-plan/SKILL.md is signed against VPL1-VPL15."""
import importlib
import re
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[6]


@pytest.mark.tree_audit("the repository's graded prose units, copied without .git")
def test_prose_owed_sh_prints_nothing_for_veri_plan_skill_and_requirements_list_vpl1_to_vpl15(tmp_path, run_cli):
    prose_owed = importlib.import_module("veri.prose_owed")
    root = tmp_path / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", ".tdd", "node_modules", "__pycache__"), symlinks=True)

    code, out, err = run_cli(prose_owed, [str(root)])

    ids = re.findall(r"^\| (VPL\d+) \|", (root / "skills/veri-plan/REQUIREMENTS.md").read_text(), re.M)
    assert "skills/veri-plan/SKILL.md" not in out.split("\n") and code in (0, 1), (code, out, err)
    assert ids == ["VPL%d" % n for n in range(1, 16)], ids
