from pathlib import Path

import pytest

import conftest
from veri.git import git

REPO = Path(__file__).resolve().parents[6]
RETIRED = ("tdd-" + "fix", "tdd-" + "candidates")
SKIPPED_DIRS = {"specs", "docs", ".tdd", ".git", "__pycache__", ".pytest_cache", "node_modules"}


def namers():
    needles = [m + name for name in RETIRED for m in ("/", "skills/")]
    found = []
    tracked = git("ls-files", "-z", cwd=REPO, check=True, capture_output=True, text=True).stdout.split("\0")
    for name in filter(None, tracked):
        path = REPO / name
        if SKIPPED_DIRS & set(Path(name).parts[:-1]):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if any(n in text for n in needles):
            found.append(name)
    return sorted(found)


@pytest.mark.process("git ls-files over the repository")
@pytest.mark.tree_audit("skills/ listing and a walk of every repo file outside specs/, docs/ and .tdd/")
def test_the_retired_filers_have_no_skill_directory_and_no_file_names_them_to_run(monkeypatch, request):
    monkeypatch.setitem(conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT, conftest.case_tail(request),
                        "the repository's own tracked files are the subject")
    left = [n for n in RETIRED if (REPO / "skills" / n).exists()]
    assert left == [], f"retired skill directories still exist: {left}"
    assert namers() == [], f"files still name a retired filer to run: {namers()}"
