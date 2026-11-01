"""skills/vplan/SKILL.md caps a sub-PRD at one capability."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]


def test_vplan_skill_limits_a_sub_prd_to_one_capability_the_human_can_use():
    prose = re.sub(r"\s+", " ", (ROOT / "skills/vplan/SKILL.md").read_text())

    assert "A sub-PRD holds at most **one capability the human can use**" in prose


def test_vplan_skill_splits_a_multi_capability_sub_prd_or_states_why_it_cannot_be():
    prose = re.sub(r"\s+", " ", (ROOT / "skills/vplan/SKILL.md").read_text())

    assert (
        "One that would hold more is split; if it cannot be, it states in its own text why not."
        in prose
    )


def test_vplan_skill_splits_a_multi_capability_outline_sub_prd_at_the_outline_stage():
    prose = re.sub(r"\s+", " ", (ROOT / "skills/vplan/SKILL.md").read_text())

    assert (
        "An outline expected to hold more than one capability is split while it is still an outline, not left for later."
        in prose
    )
