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


@pytest.mark.tree_audit("the repository's graded prose units, copied without .git")
def test_prose_owed_sh_prints_nothing_for_veri_file_skill_and_requirements_list_f1_naming_feature_f13_and_f14(tmp_path, run_cli):
    prose_owed = importlib.import_module("veri.prose_owed")
    root = tmp_path / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", ".tdd", "node_modules", "__pycache__"), symlinks=True)

    code, out, err = run_cli(prose_owed, [str(root)])

    rows = {m[0]: m[1] for m in re.findall(r"^\| (F\d+) \| (.*)$", (root / "skills/veri-file/REQUIREMENTS.md").read_text(), re.M)}
    assert "skills/veri-file/SKILL.md" not in out.split("\n") and code in (0, 1), (code, out, err)
    assert "feature" in rows.get("F1", "") and "F13" in rows and "F14" in rows, sorted(rows)


@pytest.mark.tree_audit("the repository's graded prose units, copied without .git")
def test_prose_owed_sh_prints_nothing_for_readme_and_root_requirements_list_rd28_under_readme(tmp_path, run_cli):
    prose_owed = importlib.import_module("veri.prose_owed")
    root = tmp_path / "repo"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", ".tdd", "node_modules", "__pycache__"), symlinks=True)

    code, out, err = run_cli(prose_owed, [str(root)])

    section = (root / "REQUIREMENTS.md").read_text().split("\n## README.md", 1)[1].split("\n## ", 1)[0]
    assert "README.md" not in out.split("\n") and code in (0, 1), (code, out, err)
    assert re.search(r"^\| RD28 \|", section, re.M), section
