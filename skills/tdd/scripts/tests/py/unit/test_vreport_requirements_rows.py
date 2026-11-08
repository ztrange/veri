"""skills/vreport/REQUIREMENTS.md's row IDs."""
import pathlib
import re

REQUIREMENTS = pathlib.Path(__file__).resolve().parents[6] / "skills" / "vreport" / "REQUIREMENTS.md"


def test_skill_requirements_list_holds_no_row_q7_or_q8_3262():
    ids = []
    in_skill_section = False
    for line in REQUIREMENTS.read_text().splitlines():
        if line.startswith("## "):
            in_skill_section = line[3:].strip() == "skills/vreport/SKILL.md"
        elif in_skill_section:
            row = re.match(r"\|\s*(Q\d+)\s*\|", line)
            if row:
                ids.append(row.group(1))
    assert ids, "no rows read under skills/vreport/SKILL.md"
    assert [i for i in ids if i in ("Q7", "Q8")] == []
