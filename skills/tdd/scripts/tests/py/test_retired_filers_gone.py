import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[5]
RETIRED = ("tdd-" + "fix", "tdd-" + "candidates")
SKIPPED_DIRS = {"specs", "docs", ".tdd", ".git", "__pycache__", ".pytest_cache", "node_modules"}


def namers():
    needles = [m + name for name in RETIRED for m in ("/", "skills/")]
    found = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIPPED_DIRS]
        for f in files:
            path = Path(root) / f
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if any(n in text for n in needles):
                found.append(str(path.relative_to(REPO)))
    return sorted(found)


@pytest.mark.tree_audit("skills/ listing and a walk of every repo file outside specs/, docs/ and .tdd/")
def test_the_retired_filers_have_no_skill_directory_and_no_file_names_them_to_run():
    left = [n for n in RETIRED if (REPO / "skills" / n).exists()]
    assert left == [], f"retired skill directories still exist: {left}"
    assert namers() == [], f"files still name a retired filer to run: {namers()}"
