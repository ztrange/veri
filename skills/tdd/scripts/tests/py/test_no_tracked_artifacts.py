"""Audit of the tree itself: no file a suite run writes may be tracked.

Each case's subject is the tree: the repository it is run in, or a planted one.
"""
import subprocess

import pytest

from conftest import ROOT


def tracked_artifacts(repo):
    listed = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"], capture_output=True, text=True, check=True).stdout
    return [path for path in listed.split("\0") if "/.tdd/" in path]


def new_repo(path):
    subprocess.run(["git", "-C", str(path), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@example.com"], check=True)


@pytest.mark.process("git ls-files over a planted repository holding a tracked file under a nested .tdd/")
def test_a_planted_tracked_file_under_a_nested_tdd_is_named_by_its_path(tmp_path):
    """Its subject is the tree: a planted repository, listed by git."""
    new_repo(tmp_path)
    (tmp_path / "pkg" / ".tdd").mkdir(parents=True)
    (tmp_path / "pkg" / ".tdd" / "events.jsonl").write_text("{}\n")
    (tmp_path / "keep.txt").write_text("x\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)

    assert tracked_artifacts(tmp_path) == ["pkg/.tdd/events.jsonl"]


@pytest.mark.process("git ls-files over a planted repository with no file under a nested .tdd/")
def test_a_tree_with_no_tracked_artifact_names_nothing(tmp_path):
    """Its subject is the tree: a planted repository, listed by git."""
    new_repo(tmp_path)
    (tmp_path / "keep.txt").write_text("x\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)

    assert tracked_artifacts(tmp_path) == []


@pytest.mark.process("git ls-files over the repository this suite runs in")
def test_no_file_under_a_nested_tdd_directory_is_tracked_598():
    """Its subject is the tree: the repository this suite runs in, listed by git."""
    problems = [
        f"{path} is tracked, but a suite run writes it: untrack it (git rm --cached) and ignore the directory"
        for path in tracked_artifacts(ROOT)
    ]

    assert problems == []


@pytest.mark.process("git check-ignore over the repository this suite runs in")
def test_git_ignores_the_event_log_a_suite_run_writes_under_a_nested_tdd_directory_598():
    """Its subject is the tree: the repository this suite runs in, asked what it ignores."""
    problems = [
        f"{path} is not ignored, so a suite run leaves the tree dirty: ignore nested .tdd/ directories"
        for path in ("skills/tdd/scripts/.tdd/events.jsonl", "skills/tdd/scripts/tests/.tdd/events.jsonl")
        if subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", path]).returncode != 0
    ]

    assert problems == []
