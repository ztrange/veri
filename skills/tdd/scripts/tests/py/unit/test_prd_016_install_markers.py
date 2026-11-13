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


LINKED = ("vcoord", "vdev", "vfile", "vgroom", "vhandoff", "vplan")
RETIRED = ("vready", "vreport", "vstatus", "vstop")


@pytest.mark.tree_audit("the six linked skills' markers")
def test_the_on_demand_marker_of_each_linked_skill_says_vinstall_links_it_not_by_hand():
    stale = {}
    for name in LINKED:
        text = (ROOT / "skills" / name / ".on-demand").read_text()
        if "by hand" in text or "/vinstall" not in text:
            stale[name] = text.splitlines()[:1]

    assert stale == {}, sorted(stale)


@pytest.mark.tree_audit("the four retired skills' markers")
def test_the_on_demand_marker_of_each_retired_skill_says_vinstall_does_not_link_it_3750():
    linked = sorted(n for n in RETIRED
                    if "/vinstall links it" in (ROOT / "skills" / n / ".on-demand").read_text().replace("\n", " "))

    assert linked == [], linked


def test_vinstall_carries_no_on_demand_marker():
    assert not (ROOT / "skills" / "vinstall" / ".on-demand").exists()
