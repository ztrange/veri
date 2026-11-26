"""PRD 016.3b: `.veri/test-command` is no longer a declaration (TF1), and no tracked file still names it (TF6).

This file holds the cases proving TF1, so it is the one file outside specs/ and .tdd/ the TF6 guard lets name the path.
"""
import importlib
from pathlib import Path

import pytest
from veri.git import git

import conftest

RETIRED = ".veri/test-command"
REPO = Path(__file__).resolve().parents[6]
OWN = Path(__file__).resolve().relative_to(REPO).as_posix()


def namers(root, tracked):
    """`<path>:<line>` for each line naming the retired file in <tracked> (paths under <root>), outside specs/, .tdd/
    and this file."""
    found = []
    for name in tracked:
        if name == OWN or name.startswith(("specs/", ".tdd/")) or "/.tdd/" in name:
            continue
        try:
            lines = (root / name).read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        found += ["%s:%d" % (name, n) for n, line in enumerate(lines, 1) if RETIRED in line]
    return found


def test_the_guard_names_a_mention_under_skills_by_file_and_line_and_none_under_specs_or_tdd(tmp_path):
    for name in ("skills/tdd/x.sh", "specs/prd.md", ".tdd/issue-1.md", "skills/a/.tdd/issue-2.md"):
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text("first\nreads " + RETIRED + "\n")
    tracked = ["skills/tdd/x.sh", "specs/prd.md", ".tdd/issue-1.md", "skills/a/.tdd/issue-2.md"]

    assert namers(tmp_path, tracked) == ["skills/tdd/x.sh:2"]
    (tmp_path / "skills/tdd/x.sh").write_text("first\n")
    assert namers(tmp_path, tracked) == []


@pytest.mark.process("git ls-files over the repository")
@pytest.mark.tree_audit("a walk of every tracked file outside specs/ and .tdd/")
def test_no_tracked_file_outside_specs_tdd_and_the_tf1_cases_names_the_retired_file(monkeypatch, request):
    monkeypatch.setitem(conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT, conftest.case_tail(request),
                        "the repository's own tracked files are the subject")
    tracked = git("ls-files", "-z", cwd=REPO, check=True, capture_output=True, text=True).stdout.split("\0")

    assert namers(REPO, filter(None, tracked)) == []


@pytest.fixture
def detect():
    return importlib.import_module("veri.detect_test_command")


def planted(root, **files):
    """<root> holding a `.veri/test-command` and <files> (the name's `__` is a `/`)."""
    (root / ".veri").mkdir(parents=True)
    (root / RETIRED).write_text("bin/run-suite --all --strict\n")
    for name, text in files.items():
        (root / name.replace("__", "/")).write_text(text)
    return str(root)


@pytest.mark.parametrize("tier", ["fast", "all"])
def test_a_repo_declaring_only_the_retired_file_gets_what_inference_finds_or_exit_3_with_nothing(tmp_path, run_cli, detect, tier):
    made = planted(tmp_path / "made", Makefile="test:\n\techo hi\n")
    bare = planted(tmp_path / "bare")

    assert (run_cli(detect, ["--tier", tier, made]), run_cli(detect, ["--tier", tier, bare])) == (
        (0, "make test\n", ""), (3, "", ""))
