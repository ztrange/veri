"""skills/vplan/SKILL.md caps a sub-PRD at one capability."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]


def test_vplan_skill_limits_a_sub_prd_to_one_capability_the_human_can_use():
    prose = re.sub(r"\s+", " ", (ROOT / "skills/vplan/SKILL.md").read_text())

    assert "A sub-PRD holds at most **one capability the human can use**" in prose
