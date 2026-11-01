"""PRD 016.2: every skill but vinstall carries an .on-demand marker."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[6]


@pytest.mark.tree_audit("every directory under skills/")
def test_every_directory_under_skills_other_than_vinstall_carries_an_on_demand_marker():
    missing = sorted(
        d.name for d in (ROOT / "skills").iterdir()
        if d.is_dir() and d.name != "vinstall" and not (d / ".on-demand").is_file()
    )

    assert missing == [], missing
