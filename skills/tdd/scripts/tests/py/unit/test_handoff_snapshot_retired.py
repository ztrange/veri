"""The run-state snapshot script a handoff carried is retired (#3245): no tracked file names it."""
from pathlib import Path

import pytest
from veri.git import git

import conftest

REPO = Path(__file__).resolve().parents[6]
RETIRED = ("handoff" + "-state", "handoff" + "_state")
EXEMPT_PREFIXES = ("specs/", "docs/adr/", ".tdd/")
OWN = Path(__file__).resolve().relative_to(REPO).as_posix()


def namers(root, tracked):
    """Each of `tracked` (paths relative to `root`) outside the exempt trees whose text names a retired name."""
    found = []
    for name in tracked:
        if name == OWN or name.startswith(EXEMPT_PREFIXES) or "/.tdd/" in name:
            continue
        try:
            text = (root / name).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if any(r in text or r in name for r in RETIRED):
            found.append(name)
    return sorted(found)


def test_the_guard_names_a_skill_file_that_names_the_script_and_nothing_once_it_is_removed(tmp_path):
    skill = tmp_path / "skills" / "vdev" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("Run `$S/" + RETIRED[0] + ".sh` first.\n")
    (tmp_path / "specs").mkdir()
    (tmp_path / "specs" / "prd.md").write_text(RETIRED[1] + "\n")
    tracked = ["skills/vdev/SKILL.md", "specs/prd.md"]
    assert namers(tmp_path, tracked) == ["skills/vdev/SKILL.md"]
    skill.write_text("Run `$S/status.sh --recover` first.\n")
    assert namers(tmp_path, tracked) == []


@pytest.mark.process("git ls-files over the repository")
@pytest.mark.tree_audit("a walk of every tracked file outside specs/, docs/adr/ and .tdd/")
def test_no_tracked_file_outside_the_exempt_trees_names_the_retired_snapshot_script(monkeypatch, request):
    monkeypatch.setitem(conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT, conftest.case_tail(request),
                        "the repository's own tracked files are the subject")
    tracked = git("ls-files", "-z", cwd=REPO, check=True, capture_output=True, text=True).stdout.split("\0")
    assert namers(REPO, filter(None, tracked)) == []
