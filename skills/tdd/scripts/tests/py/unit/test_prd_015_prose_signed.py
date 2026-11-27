"""PRD 015: skills/vplan/SKILL.md is signed against VPL1-VPL27."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]


def test_veri_plan_requirements_list_vpl1_to_vpl27_in_order():
    ids = re.findall(r"^\| (VPL\d+) \|", (ROOT / "skills/vplan/REQUIREMENTS.md").read_text(), re.M)

    assert ids == ["VPL%d" % n for n in range(1, 28)], ids


def test_veri_file_requirements_list_f1_naming_feature_f13_and_f14():
    rows = {m[0]: m[1] for m in re.findall(r"^\| (F\d+) \| (.*)$", (ROOT / "skills/vfile/REQUIREMENTS.md").read_text(), re.M)}

    assert "feature" in rows.get("F1", "") and "F13" in rows and "F14" in rows, sorted(rows)


def test_root_requirements_list_rd28_under_readme():
    section = (ROOT / "REQUIREMENTS.md").read_text().split("\n## README.md", 1)[1].split("\n## ", 1)[0]

    assert re.search(r"^\| RD28 \|", section, re.M), section


def test_row_sc23_names_the_refusal_of_a_criterion_tagged_text():
    row = re.search(r"^\| SC23 \|(.*)$", (ROOT / "skills/tdd/REQUIREMENTS.md").read_text(), re.M)

    assert row and "already carries a `⟦criterion k⟧` tag" in row.group(1), row and row.group(1)[:200]
