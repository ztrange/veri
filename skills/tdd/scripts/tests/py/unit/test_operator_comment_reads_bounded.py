"""Source-text audit of skills/vcoord and skills/vdev: no gh comment read returns a whole thread."""
import re

import pytest

from conftest import ROOT

READS = ("--json comments", "/comments", "--comments")
BOUNDS = ("[-1]", "head -c")


def commands(text):
    spans = re.findall(r"`([^`\n]+)`", text)
    lines = [ln.strip() for ln in text.splitlines()]
    return [c for c in spans + lines if re.search(r"\bgh\b", c)]


@pytest.mark.tree_audit("every Markdown file under skills/vcoord and skills/vdev")
def test_every_gh_comment_read_in_vcoord_and_vdev_is_bounded():
    unbounded = []
    for skill in ("vcoord", "vdev"):
        for path in sorted((ROOT / "skills" / skill).rglob("*.md")):
            text = path.read_bytes().decode("utf-8", "surrogateescape")
            for cmd in commands(text):
                if any(r in cmd for r in READS) and not any(b in cmd for b in BOUNDS):
                    unbounded.append(f"{path.relative_to(ROOT)}: {cmd}")
    assert unbounded == [], "whole-thread gh comment read: " + "; ".join(unbounded)
